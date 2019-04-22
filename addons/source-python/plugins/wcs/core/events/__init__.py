# ../wcs/core/events.py

# ============================================================================
# >> IMPORTS
# ============================================================================
# Source.Python Imports
#   Events
from events import Event as _Event
from events.manager import event_manager

# WCS Imports
#   Constants
from ..constants import IS_ESC_SUPPORT_ENABLED

# Is ESC supported?
if IS_ESC_SUPPORT_ENABLED:
    from es_emulator.logic import fill_event_vars
    from es_emulator.logic import current_event_vars


# ============================================================================
# >> ALL DECLARATION
# ============================================================================
__all__ = (
    'Event',
    'FakeEvent',
)


# ============================================================================
# >> GLOBAL VARIABLES
# ============================================================================
_events = {}


# ============================================================================
# >> CLASSES
# ============================================================================
class Event(_Event):
    def __call__(self, callback):
        self.callback = callback

        return self.callback

    def _add_instance(self, caller):
        self._caller = caller.split('.')[-1]

        if self._caller not in _events:
            _events[self._caller] = {'events':[], 'counter':0}

        _events[self._caller]['events'].append(self)

        super()._add_instance(caller)

    def _unload_instance(self):
        if _events[self._caller]['counter']:
            if self.callback is None:
                return

            self.unregister()

    def register(self):
        for event_name in self._event_names:
            event_manager.register_for_event(event_name, self.callback)

    def unregister(self):
        for event_name in self._event_names:
            event_manager.unregister_for_event(event_name, self.callback)


# Emulates a real GameEvent object (with ESC support)
class FakeEvent(object):
    class _Container(dict):
        def as_dict(self):
            return self

    def __init__(self, name, **kwargs):
        self._name = name
        self._variables = self._Container(wcs_fake=1, **kwargs)

        self._tmp = None

    def __enter__(self):
        # Is ESC supported?
        if IS_ESC_SUPPORT_ENABLED:
            tmp = self._variables.copy()

            for variable, value in tmp.items():
                if isinstance(value, (list, tuple)):
                    tmp[variable] = ','.join([str(x) for x in value])

            self._tmp = current_event_vars.copy()
            current_event_vars.clear()
            current_event_vars.update(tmp)
            current_event_vars['es_event'] = self._name

            userid = current_event_vars.get('userid')

            if userid:
                fill_event_vars(userid, 'user')

            attacker = current_event_vars.get('attacker')

            if attacker:
                fill_event_vars(attacker, 'attacker')

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Is ESC supported?
        if IS_ESC_SUPPORT_ENABLED:
            current_event_vars.clear()
            current_event_vars.update(self._tmp)

            self._tmp = None

    def __getitem__(self, name):
        return self._variables[name]

    def __setitem__(self, name, value):
        self._variables[name] = value

    def is_reliable(self):
        raise NotImplementedError()

    def is_local(self):
        raise NotImplementedError()

    def is_empty(self, key_name=None):
        if key_name is None:
            return not self._variables

        return key_name in self._variables

    def get_bool(self, key_name, default_value=False):
        return self._variables.get(key_name, default_value)

    def get_int(self, key_name, default_value=0):
        return self._variables.get(key_name, default_value)

    def get_float(self, key_name, default_value=0.0):
        return self._variables.get(key_name, default_value)

    def get_str(self, key_name, default_value=''):
        return self._variables.get(key_name, default_value)

    def set_bool(self, key_name, value):
        assert isinstance(value, bool)
        self._variables[key_name] = value

    def set_int(self, key_name, value):
        assert isinstance(value, int)
        self._variables[key_name] = value

    def set_float(self, key_name, value):
        assert isinstance(value, float)
        self._variables[key_name] = value

    def set_str(self, key_name, value):
        assert isinstance(value, str)
        self._variables[key_name] = value

    @property
    def name(self):
        return self._name

    @property
    def descriptor(self):
        raise NotImplementedError()

    @property
    def variables(self):
        return self._variables
