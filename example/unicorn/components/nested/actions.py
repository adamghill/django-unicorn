from django_unicorn.components import UnicornView
from typing import Callable


class ActionsView(UnicornView):
    # In this example the ActionsView is completely controlled by the
    # RowView and it doesn't really "own" these - its useful to put them
    # on the class for type hints and/or default values, but we don't
    # want to give the impression they are ActionsView's own state

    is_editing: bool
    on_edit: Callable
    on_cancel: Callable
    on_save: Callable