
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

    def get_response_data(self):
        # The payload value is needed in two places
        return {
            "redirect": self.redirect_url,
            "return": self.to_dict(),
        }

    # def get_payload_value(self):
    #     return {
    #         "timing": self.timing,
    #         "method": self.method,
    #         "disable": self.disable,
    #     }

    # def get_response_data(self):
    #     # The payload value is needed in two places
    #     return {
    #         "poll": self.get_payload_value(),
    #         "return": self.to_dict(),
    #     }
