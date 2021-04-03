from django_unicorn.serializer import model_value


class ModelValueMixin:
    """
    Adds a `value` method to a model similar to `QuerySet.values(*fields)` which serializes
    a model into a dictionary with the fields as specified in the `fields` argument.
    """

    def value(self, *fields):
        return model_value(self, *fields)
