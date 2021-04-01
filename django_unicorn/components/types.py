from typing import Generic, Iterator, TypeVar

from django.db.models import Model, QuerySet


M = TypeVar("M", bound=Model)


class QueryType(Generic[M], QuerySet):
    def __iter__(self) -> Iterator[M]:
        ...
