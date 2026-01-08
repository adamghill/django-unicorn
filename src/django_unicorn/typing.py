from collections.abc import Iterator
from typing import TYPE_CHECKING, Generic, TypeVar

from django.db.models import Model, QuerySet

M_co = TypeVar("M_co", bound=Model, covariant=True)


if TYPE_CHECKING:

    class QuerySetType(QuerySet[M_co]):
        pass
else:

    class QuerySetType(Generic[M_co], QuerySet):
        """
        Type for QuerySet that can be used for a typehint in components.
        """

        # This is based on https://github.com/Vieolo/django-hint/blob/97e22bf/django_hint/typehint.py#L167,
        # although https://github.com/typeddjango/django-stubs/blob/2a732fd/django-stubs/db/models/manager.pyi#L28
        # might be a better long-term solution.

        def __iter__(self) -> Iterator[M_co]: ...
