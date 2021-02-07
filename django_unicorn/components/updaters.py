import logging

from django.http.response import HttpResponseRedirect


logger = logging.getLogger(__name__)


class Update:
    """
    Base class for updaters.
    """

    def to_json(self):
        return self.__dict__


class HashUpdate(Update):
    """
    Updates the current URL hash from an action method.
    """

    def __init__(self, hash: str):
        """
        Args:
            param hash: The hash to change. Example: `#model-123`.
        """
        self.hash = hash


class LocationUpdate(Update):
    """
    Updates the current URL from an action method.
    """

    def __init__(self, redirect: HttpResponseRedirect, title: str = None):
        """
        Args:
            param redirect: The redirect that contains the URL to redirect to.
            param title: The new title of the page. Optional.
        """
        self.redirect = redirect
        self.title = title


class PollUpdate(Update):
    """
    Updates the current poll from an action method.
    """

    def __init__(self, timing: int = None, method: str = None, disable: bool = False):
        """
        Args:
            param timing: The timing that should be used for the poll. Optional. Defaults to `None`
                which keeps the existing timing.
            param method: The method that should be used for the poll. Optional. Defaults to `None`
                which keeps the existing method.
            param disable: Whether to disable the poll or not not. Optional. Defaults to `False`.
        """
        self.timing = timing
        self.method = method
        self.disable = disable
