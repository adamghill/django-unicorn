
from django.http.response import HttpResponseRedirect

from .base import FrontendAction


class Redirect(FrontendAction):

    def __init__(self, *, url: str):
        self.url = url

    @classmethod
    def from_django(cls, redirect: HttpResponseRedirect):
        return cls(url=redirect.url)

    def get_payload_value(self):
        return {"url": self.url}

    def get_response_data(self):
        # The payload value is needed in two places
        return {
            "redirect": self.get_payload_value(),
            "return": self.to_dict(),
        }
