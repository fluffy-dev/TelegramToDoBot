from typing import Any, Dict, Tuple

from django.db import models
from django.db.models import QuerySet


def model_update(
    *,
    instance: models.Model,
    fields: list[str],
    data: Dict[str, Any]
) -> Tuple[models.Model, bool]:
    """
    Generic update service to update a model instance.

    Args:
        instance (Model): The model instance to update.
        fields (list[str]): A list of field names to update.
        data (Dict[str, Any]): A dictionary containing the new data.

    Returns:
        Tuple[Model, bool]: A tuple containing the updated instance and
        a boolean indicating if the instance was updated.
    """
    has_updated = False
    updated_fields = []

    for field in fields:
        if field not in data:
            continue

        if getattr(instance, field) != data[field]:
            setattr(instance, field, data[field])
            updated_fields.append(field)
            has_updated = True

    if has_updated:
        instance.full_clean()
        instance.save(update_fields=updated_fields)

    return instance, has_updated