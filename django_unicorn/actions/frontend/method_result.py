
from .base import FrontendAction


class MethodResult(FrontendAction):

    def __init__(self, value=None):

        # TODO: Support a tuple/list return_value which could contain multiple values
        self.value = value or {}

    def get_payload_value(self):
        return self.value
