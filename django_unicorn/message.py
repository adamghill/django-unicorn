import logging

from django.http.response import HttpResponseRedirect

import orjson

from .components import HashUpdate, LocationUpdate, PollUpdate
from .errors import UnicornViewError
from .serializer import dumps
from .utils import generate_checksum


logger = logging.getLogger(__name__)


class ComponentRequest:
    """
    Parses, validates, and stores all of the data from the message request.
    """

    def __init__(self, request):
        self.body = {}

        try:
            self.body = orjson.loads(request.body)
            assert self.body, "Invalid JSON body"
        except orjson.JSONDecodeError as e:
            raise UnicornViewError("Body could not be parsed") from e

        self.data = self.body.get("data")
        assert self.data is not None, "Missing data"  # data could theoretically be {}

        self.id = self.body.get("id")
        assert self.id, "Missing component id"

        self.key = self.body.get("key", "")

        self.validate_checksum()

        self.action_queue = self.body.get("actionQueue", [])

    def validate_checksum(self):
        """
        Validates that the checksum in the request matches the data.

        Returns:
            Raises `AssertionError` if the checksums don't match.
        """
        checksum = self.body.get("checksum")
        assert checksum, "Missing checksum"

        generated_checksum = generate_checksum(orjson.dumps(self.data))
        assert checksum == generated_checksum, "Checksum does not match"


class Return:
    def __init__(self, method_name, params=[]):
        self.method_name = method_name
        self.params = params
        self._value = {}
        self.redirect = {}
        self.poll = {}

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value
        # TODO: Support a tuple/list return_value which could contain multiple values

        if value is not None:
            if isinstance(value, HttpResponseRedirect):
                self.redirect = {
                    "url": value.url,
                }
            elif isinstance(value, HashUpdate):
                self.redirect = {
                    "hash": value.hash,
                }
            elif isinstance(value, LocationUpdate):
                self.redirect = {
                    "url": value.redirect.url,
                    "refresh": True,
                    "title": value.title,
                }
            elif isinstance(value, PollUpdate):
                self.poll = value.to_json()

            if self.redirect:
                self._value = self.redirect

    def get_data(self):
        try:
            serialized_value = orjson.loads(dumps(self.value))
            serialized_params = orjson.loads(dumps(self.params))

            return {
                "method": self.method_name,
                "params": serialized_params,
                "value": serialized_value,
            }
        except Exception as e:
            logger.exception(e)

        return {}
