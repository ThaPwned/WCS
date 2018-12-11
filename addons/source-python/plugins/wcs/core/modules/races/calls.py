# ../wcs/core/modules/races/calls.py

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
from .manager import race_manager


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
        self.race = callback.__module__.rsplit('.', 1)[1]

        _callbacks[self.race][self.event] = callback

        if event is not None:
            config = race_manager[self.race].config['skills']

            # TODO: Figure out a better way of doing this
            if self.event in config:
                config[self.event]['event'] = event
            elif self.event.endswith(('_on', '_off')):
                config[self.event.rsplit('_', 1)[0]]['event'] = event
            else:
                raise ValueError(f'Invalid function name: {self.event}')

    def _unload_instance(self):
        del _callbacks[self.race][self.event]

        if not _callbacks[self.race]:
            del _callbacks[self.race]


# ============================================================================
# >> FUNCTIONS
# ============================================================================
def command(function=_guard, *, event=None):
    if function is _guard:
        return partial(_Decorator, event=event)

    return _Decorator(function, event=event)
