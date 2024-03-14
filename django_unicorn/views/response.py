
class ComponentResponse:
    """
    Contains the result of changes made to a Component after a
    ComponentRequest (and its actions) have been applied to it
    """

    def __init__(self, result: dict):
        breakpoint()
        # Sort data so it's stable
        self.data = {key: result["data"][key] for key in sorted(result["data"])}

    @classmethod
    def from_inspection(cls, request, component, return_data):
        # typing: objs of ComponentRequest, Component, Return

        breakpoint()

        original_context = request.data.items()
        new_context = component.get_frontend_context()

        # inspect for special actions & pull out updated_data
        if not request.is_refresh_called:
            if not request.is_reset_called:
                # Get the context that only includes updated data
                updated_data = {
                    key: value
                    for key, value in original_context.items()
                    if new_context.get(key) != value
                }

            if request.validate_all_fields:
                component.validate()
            else:
                component.validate(model_names=list(updated_data.keys()))
        else:
            updated_data = copy(new_context.deepcopy())

        # TODO: Handle redirects and messages by patching request obj...?
        # I'm not sure what's going on here yet
        #
        # request_queued_messages = []
        # if return_data and return_data.redirect and "url" in return_data.redirect:
        #     # If we know the user wants to redirect, get a copy of the private queued messages
        #     # and make sure they get stored for the next page load instead of getting rendered
        #     # by the component
        #     try:
        #         request_queued_messages = copy.deepcopy(component.request._messages._queued_messages)
        #         component.request._messages._queued_messages = []
        #     except AttributeError as e:
        #         logger.warning(e)
        # if request_queued_messages:
        #     try:
        #         component.request._messages._queued_messages = request_queued_messages
        #     except AttributeError as e:
        #         logger.warning(e)

        # generate the html using the current request
        component_html = component.render(
            request=request,  # gives the original HttpRequest
        )

        # !!! might want to rename this hook to "post_render"... confused me at first
        # Also is there an example of when this would be used? And why it takes
        # the html as input?
        component.rendered(component_html)

        # Check if there are partials, and if so, we only want specific
        # elements of the component_html, rather than all of it
        partial_doms = cls._get_partials_from_html(
            html=component_html,
            partials=request.partials,
        )

        # base results. we add to & update this below
        result = {
            "id": request.id,
            "data": updated_data,
            "errors": component.errors,
            "calls": component.calls,
            # !!! should I checksum the request or the response data?
            "checksum": generate_checksum(request.data),
        }

        # add result from the Return object
        if return_data:
            result["return"] = return_data.get_data()
            if return_data.redirect:
                result["redirect"] = return_data.redirect
            if return_data.poll:
                result["poll"] = return_data.poll

        # --------------

        # !!! Code below needs more refactoring

        # Grab the relevant html changes in order to set "partials" or "dom"
        # and check if the html has changed at all.
        render_not_modified = False  # until proven otherwise
        if partial_doms:
            soup_root = None
            result["partials"] = partial_doms
        else:
            component_html_hash = generate_checksum(component_html)

            if (
                request.hash == component_html_hash
                and (not return_data or not return_data.value)
                and not component.calls
            ):
                if not component.parent and component.force_render is False:
                    raise RenderNotModifiedError()
                else:
                    render_not_modified = True
                    # NOTE: this can be "overturned" below when looking at parents

            # Make sure that partials with comments or blank lines before the root element
            # only return the root element
            soup = BeautifulSoup(component_html, features="html.parser")
            soup_root = get_root_element(soup)
            component_html_cleaned = str(soup_root)
            # !!! Should this be moved to the component.render method?

            result["dom"] = component_html_cleaned
            result["hash"] = component_html_hash

        # --------------

        # !!! Code below is a big shift from single to child/parent components

        # Iteratively check parent objects in can we need to update its dom instead
        # !!! what about iteratively checking children...?
        parent_component = component.parent
        parent_result = result
        while parent_component:
            if parent_component.force_render is True:
                # TODO: Should parent_component.hydrate() be called?
                parent_frontend_context_variables = loads(
                    parent_component.get_frontend_context_variables()
                )
                parent_checksum = generate_checksum(
                    str(parent_frontend_context_variables)
                )

                parent = {
                    "id": parent_component.component_id,
                    "checksum": parent_checksum,
                }

                if not partial_doms:
                    parent_dom = parent_component.render()
                    component.parent_rendered(parent_dom)

                    # Get re-generated child checksum and update the child component inside the parent DOM
                    if not soup_root:
                        raise AssertionError("Missing root element")

                    # TODO: Use minestrone for this
                    child_soup_checksum = soup_root.attrs["unicorn:checksum"]
                    child_soup_unicorn_id = soup_root.attrs["unicorn:id"]

                    parent_soup = BeautifulSoup(parent_dom, features="html.parser")

                    for _child in parent_soup.descendants:
                        if isinstance(
                            _child, Tag
                        ) and child_soup_unicorn_id == _child.attrs.get("unicorn:id"):
                            _child.attrs["unicorn:checksum"] = child_soup_checksum

                    parent_soup = get_root_element(parent_soup)
                    parent_dom = str(parent_soup)

                    # Remove the child DOM from the payload since the parent DOM supersedes it
                    result["dom"] = None

                    parent.update(
                        {
                            "dom": parent_dom,
                            "data": parent_frontend_context_variables,
                            "errors": parent_component.errors,
                            "hash": generate_checksum(parent_dom),
                        }
                    )

            if render_not_modified:
                # TODO: Determine if all parents have not changed and return a 304 if
                # that's the case
                # i.e. render_not_modified = render_not_modified and (parent hash test)
                pass

            parent_result.update({"parent": parent})
            parent_result = parent

        component = parent_component
        parent_component = parent_component.parent

        return cls(result)

    def to_json_response(self):
        breakpoint()
        return JsonResponse(
            data=self.updates,
            json_dumps_params={"separators": (",", ":")},
        )

    @staticmethod
    def _get_partials_from_html(html: str, partials: list[dict]) -> list[dict]:
        """
        Given the fully rendered html string and a list partial configs, this
        will return a list of the partial_doms (i.e. only the relevent html)
        needed, rather than the entire html.
        """

        partial_doms = []

        if partials and all(partials):
            soup = BeautifulSoup(html, features="html.parser")

            for partial in partials:
                partial_found = False
                only_id = False
                only_key = False

                target = partial.get("target")

                if not target:
                    target = partial.get("key")

                    if target:
                        only_key = True

                if not target:
                    target = partial.get("id")

                    if target:
                        only_id = True

                if not target:
                    raise AssertionError("Partial target is required")

                if not only_id:
                    for element in soup.find_all():
                        if (
                            "unicorn:key" in element.attrs
                            and element.attrs["unicorn:key"] == target
                        ):
                            partial_doms.append({"key": target, "dom": str(element)})
                            partial_found = True
                            break

                if not partial_found and not only_key:
                    for element in soup.find_all():
                        if "id" in element.attrs and element.attrs["id"] == target:
                            partial_doms.append({"id": target, "dom": str(element)})
                            partial_found = True
                            break

        return partial_doms