import logging
from typing import Optional

from django.http.response import HttpResponseRedirect

logger = logging.getLogger(__name__)


class Update:
    """
    Base class for updaters.
    """

    def to_json(self):
        return self.__dict__

