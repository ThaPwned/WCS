# ../wcs/core/modules/items/calls.py

# ============================================================================
# >> IMPORTS
# ============================================================================
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
    'ItemEvent',
)


# ============================================================================
# >> CLASSES
# ============================================================================
class ItemEvent(AutoUnload):
    def __init__(self, event):
        self.event = event

    def __call__(self, callback):
        self.callback = callback
        self.item = callback.__module__.rsplit('.', 1)[1]

        assert self.event not in _callbacks[self.item]

        _callbacks[self.item][self.event] = callback

        config = item_manager[self.item]

        if 'event' not in config:
            config['event'] = []

        config['event'].append(self.event)

    def _unload_instance(self):
        del _callbacks[self.item][self.event]

        if not _callbacks[self.item]:
            del _callbacks[self.item]
