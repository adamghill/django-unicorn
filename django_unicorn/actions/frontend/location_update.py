
class LocationUpdate(Update):
    """
    Updates the current URL from an action method.
    """

    def __init__(self, redirect: HttpResponseRedirect, title: Optional[str] = None):
        """
        Args:
            param redirect: The redirect that contains the URL to redirect to.
            param title: The new title of the page. Optional.
        """
        self.redirect = redirect
        self.title = title
