# ../wcs/core/modules/items/calls.py

# ============================================================================
# >> IMPORTS
# ============================================================================
# Python Imports
#   Functools
from functools import partial

# Source.Python Imports
#   Core
from core import AutoUnload

# WCS Imports
#   Modules
from . import _callbacks
from .manager import item_manager


# ============================================================================
# >> ALL DECLARATION
# ============================================================================
__all__ = (
    'command',
)


# ============================================================================
# >> GLOBAL VARIABLES
# ============================================================================
_guard = object()


# ============================================================================
# >> CLASSES
# ============================================================================
class _Decorator(AutoUnload):
    def __init__(self, callback, event=None):
        self.callback = callback
        self.event = callback.__name__
        self.item = callback.__module__.rsplit('.', 1)[1]

        _callbacks[self.item][self.event] = callback

        if event is not None:
            item_manager[self.item].config['event'] = event

    def _unload_instance(self):
        del _callbacks[self.item][self.event]

        if not _callbacks[self.item]:
            del _callbacks[self.item]


# ============================================================================
# >> FUNCTIONS
# ============================================================================
def command(function=_guard, *, event=None):
    if function is _guard:
        return partial(_Decorator, event=event)

    return _Decorator(function, event=event)
