
from .base import FrontendAction


class HashUpdate(FrontendAction):
    """
    Updates the current URL hash from an action method.
    """

    def __init__(self, url_hash: str):
        """
        Args:
            param url_hash: The URL hash to change. Example: `#model-123`.
        """
        self.hash = url_hash
