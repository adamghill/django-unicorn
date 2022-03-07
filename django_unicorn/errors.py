class UnicornCacheError(Exception):
    pass


class UnicornViewError(Exception):
    pass


class ComponentModuleLoadError(Exception):
    def __init__(self, *args, locations=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.locations = locations


class ComponentClassLoadError(Exception):
    def __init__(self, *args, locations=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.locations = locations


class RenderNotModified(Exception):
    pass


class MissingComponentElement(Exception):
    pass


class MissingComponentViewElement(Exception):
    pass


class ComponentNotValid(Exception):
    pass
