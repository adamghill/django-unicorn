
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
        self.url_hash = url_hash

    def get_payload_value(self):
        return {"hash": self.url_hash}

    def get_response_data(self):
        # The payload value is needed in two places
        return {
            "redirect": self.get_payload_value(),
            "return": self.to_dict(),
        }
