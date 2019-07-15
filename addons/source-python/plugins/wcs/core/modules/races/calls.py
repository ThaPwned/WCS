# ../wcs/core/modules/races/calls.py

# ============================================================================
# >> IMPORTS
# ============================================================================
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
    'RaceEvent',
    'SkillEvent',
)


# ============================================================================
# >> CLASSES
# ============================================================================
class RaceEvent(AutoUnload):
    def __init__(self, event=None):
        self.event = event

    def __call__(self, callback):
        if self.event is None:
            self.event = callback.__name__

        self.race = callback.__module__.rsplit('.', 1)[1]

        _callbacks[self.race][self.event] = callback

        return callback

    def _unload_instance(self):
        del _callbacks[self.race][self.event]

        if not _callbacks[self.race]:
            del _callbacks[self.race]


class SkillEvent(AutoUnload):
    def __init__(self, event, skill=None):
        self.event = event
        self.skill = skill

    def __call__(self, callback):
        if self.skill is None:
            self.skill = callback.__name__

        self.race = callback.__module__.rsplit('.', 1)[1]

        if self.skill not in _callbacks[self.race]:
            _callbacks[self.race][self.skill] = {}

        assert self.event not in _callbacks[self.race][self.skill]

        _callbacks[self.race][self.skill][self.event] = callback

        config = race_manager[self.race].config['skills']

        if 'event' not in config[self.skill]:
            config[self.skill]['event'] = []

        config[self.skill]['event'].append(self.event)

        return callback

    def _unload_instance(self):
        del _callbacks[self.race][self.skill][self.event]

        if not _callbacks[self.race][self.skill]:
            del _callbacks[self.race][self.skill]

            if not _callbacks[self.race]:
                del _callbacks[self.race]
