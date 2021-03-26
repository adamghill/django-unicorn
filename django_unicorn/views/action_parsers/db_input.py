from typing import Dict

from django.db.models import Model

from django_unicorn.components import UnicornView


def handle(component: UnicornView, payload: Dict):
    model = payload.get("model")
    db = payload.get("db", {})
    db_model_name = db.get("name")
    pk = db.get("pk")

    DbModel = None
    db_defaults = {}

    if model:
        model_class = getattr(component, model)

        if hasattr(model_class, "model"):
            DbModel = model_class.model

            if hasattr(component, "Meta"):
                for m in component.Meta.db_models:
                    if m.model_class == model_class.model:
                        db_defaults = m.defaults
                        break

    if not DbModel and db_model_name:
        assert hasattr(component, "Meta") and hasattr(
            component.Meta, "db_models"
        ), "Missing Meta.db_models list in component"

        for m in component.Meta.db_models:
            if m.name == db_model_name:
                DbModel = m.model_class
                db_defaults = m.defaults
                break

    fields = payload.get("fields", {})

    assert DbModel, f"Missing {model}.model and {db_model_name} in Meta.db_models"
    assert issubclass(
        DbModel, Model
    ), "Model must be an instance of `django.db.models.Model"

    if fields:
        fields_to_update = db_defaults
        fields_to_update.update(fields)

        if pk:
            DbModel.objects.filter(pk=pk).update(**fields_to_update)
        else:
            instance = DbModel(**fields_to_update)
            instance.save()
            pk = instance.pk
