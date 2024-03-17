
from django.http.response import HttpResponseRedirect

from .base import FrontendAction


class Redirect(FrontendAction):
    # TODO
    pass

    # if isinstance(value, HttpResponseRedirect):
    #     self.redirect = {
    #         "url": value.url,
    #     }

    # if self.redirect:
    #     self.value = self.redirect
