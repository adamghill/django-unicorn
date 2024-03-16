
class PollUpdate(Update):
    """
    Updates the current poll from an action method.
    """

    def __init__(self, *, timing: Optional[int] = None, method: Optional[str] = None, disable: bool = False):
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
