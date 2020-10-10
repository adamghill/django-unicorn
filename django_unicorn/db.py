from django.db.models import Model


class DbModel:
    def __init__(self, name: str, model_class: Model, *, defaults: dict = {}):
        self.name = name
        self.model_class = model_class
        self.defaults = defaults
