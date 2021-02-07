class UnicornField:
    """
    Base class to provide a way to serialize a component field quickly.
    """

    def to_json(self):
        return self.__dict__
