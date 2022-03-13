from django import forms
from django.forms import Field
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
        for (
            field_name,
            field,
        ) in self.form_class.base_fields.items():  # type: (str, Field)
            # don't override existing "initial" attrs
            if not hasattr(self, field_name):
                setattr(self.__class__, field_name, "")

            field.widget.attrs.update(self.get_widget_attr(field_name, field))

        super().__init__(**kwargs)
        
    def get_widget_attr(self, field_name: str, field: Field) -> Dict[str, Any]:
        """Returns an html attribute for the given field.

        This method can be overridden for setting special attributes to some fields. As default, it returns
        "unicorn:model"""

        if isinstance(
            field,
            (
                forms.BooleanField,
                forms.NullBooleanField,
                forms.RadioSelect,
                forms.NullBooleanSelect,
                forms.ChoiceField,
                forms.ModelChoiceField,
                forms.MultipleChoiceField,
                forms.ModelMultipleChoiceField,
                forms.TypedChoiceField,
                forms.TypedMultipleChoiceField,
            ),
        ):
            return {"unicorn:model": field_name}
        else:
            return {"unicorn:model.lazy": field_name}

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
