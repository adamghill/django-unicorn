from django import forms
from django.views.generic.edit import FormMixin

from django_unicorn.serializer import model_value


class ModelValueMixin:
    """
    Adds a `value` method to a model similar to `QuerySet.values(*fields)` which serializes
    a model into a dictionary with the fields as specified in the `fields` argument.
    """

    def value(self, *fields):
        return model_value(self, *fields)


class UnicornFormMixin(FormMixin):
    """Mixin for UnicornView to add Forms functionality."""

    def __init__(self, **kwargs):
        if self.success_url is not None:
            # FIXME Use AttributeError instead, but AttributeErrors are catched by Unicorn and it overrides it with a generic message
            raise AttributeError(
                f"You may not use a success URL attribute with Unicorn's {self.__class__.__name__}."
            )
        if self.initial:
            raise AttributeError(
                f"Do not use the 'initial' attr for setting initial data in a component. Set attributes directly in the component class '{self.__class__.__name__}' instead ."
            )

        # set the classes Unicorn attrs dynamically,
        for field_name, field in self.form_class.base_fields.items():  # type: str,Field
            # don't override existing "initial" attrs
            if not hasattr(self, field_name):
                setattr(self.__class__, field_name, "")

            # FIXME: Unicorn attr should be made configurable by the user, and maybe per field?
            if isinstance(field, forms.BooleanField):
                unicorn_attr = "unicorn:model"
            else:
                unicorn_attr = "unicorn:model.lazy"
            field.widget.attrs.update({unicorn_attr: field_name})

        super().__init__(**kwargs)

    def get_initial(self):
        return self._attributes()

    def get_success_url(self):
        return ""

    def form_valid(self, form):
        # TODO is there anything to do here?
        # At least a HttpResponseRedirect to success_url is wrong, like in FormMixin
        pass

    def form_invalid(self, form):
        # TODO is there anything to do here?
        pass

    # from django.forms.FormMixin:
    # def get_form_kwargs(self):
    #     """Return the keyword arguments for instantiating the form."""
    #     kwargs = super().get_form_kwargs()
    #     # kwargs = {
    #     #     # "initial": self.get_initial(),
    #     #     # "prefix": self.get_prefix(),
    #     # }
    #
    #     if self.request.method in ("POST", "PUT"):
    #         kwargs.update(
    #             {
    #                 "data": self.request.POST,
    #                 "files": self.request.FILES,
    #             }
    #         )
    #     return kwargs
