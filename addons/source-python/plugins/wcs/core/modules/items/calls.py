# ../wcs/core/modules/items/calls.py

# ============================================================================
# >> IMPORTS
# ============================================================================
# Python Imports
#   Collections
from collections import defaultdict

from core import AutoUnload


# ============================================================================
# >> ALL DECLARATION
# ============================================================================
__all__ = (
    'Command',
)


# ============================================================================
# >> GLOBAL VARIABLES
# ============================================================================
_callbacks = defaultdict(dict)


# ============================================================================
# >> CLASSES
# ============================================================================
class Command(AutoUnload):
    def __init__(self, callback):
        self.callback = callback
        self.event = callback.__name__
        self.item = callback.__module__.rsplit('.', 1)[1]

        _callbacks[self.item][self.event] = callback

    def _unload_instance(self):
        del _callbacks[self.item][self.event]

        if not _callbacks[self.item]:
            del _callbacks[self.item]
