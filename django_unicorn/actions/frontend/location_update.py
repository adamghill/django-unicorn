
from django.http import HttpResponseRedirect

from .base import FrontendAction


class LocationUpdate(FrontendAction):
    """
    Updates the current URL from an action method.
    """

    def __init__(self, redirect: HttpResponseRedirect, title: str | None = None):
        """
        Args:
            param redirect: The redirect that contains the URL to redirect to.
            param title: The new title of the page. Optional.
        """
        self.url = redirect.url
        self.title = title

    # @classmethod
    # def from_django(cls, redirect: HttpResponseRedirect):
    #     return cls(url=redirect.url)

    def get_payload_value(self):
        return {
            "refresh": True,
            "title": self.title,
            "url": self.url,
        }

    def get_response_data(self):
        # The payload value is needed in two places
        return {
            "redirect": self.get_payload_value(),
            "return": self.to_dict(),
        }
