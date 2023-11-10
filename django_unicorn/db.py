from typing import Optional

from django.db.models import Model


class DbModel:
    def __init__(self, name: str, model_class: Model, *, defaults: Optional[dict] = None):
        if defaults is None:
            defaults = {}
        self.name = name
        self.model_class = model_class
        self.defaults = defaults
