# ../wcs/core/modules/races/manager.py

# ============================================================================
# >> IMPORTS
# ============================================================================
# Python Imports
#   Itertools
from itertools import chain
#   Warnings
from warnings import warn

# Source.Python Imports
#   Engines
from engines.server import global_vars
#   Translations
from translations.strings import TranslationStrings

# WCS Imports
#   Config
from ...config import cfg_default_race, cfg_ffa_enabled, cfg_bot_ignore_level_requirement
#   Constants
from ...constants import IS_ESC_SUPPORT_ENABLED
from ...constants import RaceReason
from ...constants.paths import RACE_PATH_ES
from ...constants.paths import RACE_PATH
#   Listeners
from ...listeners import OnIsRaceUsable
from ...listeners import OnPluginRaceLoad
#   Menus
from ...menus import changerace_menu
from ...menus import raceinfo_menu
#   Modules
from . import _callbacks
from ..base import _BaseManager
from ..base import _BaseSetting
#   Players
from ...players import team_data


# ============================================================================
# >> ALL DECLARATION
# ============================================================================
__all__ = (
    'race_manager',
)


# ============================================================================
# >> CLASSES
# ============================================================================
class _LanguageString(str):
    def get_string(self, *args, **kwargs):
        return self


class _FakeRace(_BaseSetting):
    def __init__(self):
        self.name = 'none'
        self.type = None
        self.module = None

        self.config = {'required': 0, 'maximum': 0, 'restrictbot': 0, 'restrictmap': [], 'restrictitem': [], 'restrictweapon': [], 'restrictteam': 0, 'teamlimit': 0, 'author': 'Tha Pwned', 'allowonly': [], 'skills': {}}

        self.strings = {'name':_LanguageString('None'), 'description':_LanguageString('Add some races'), 'shortname':_LanguageString('None')}

        self.config['categories'] = []

    def execute(self, *args):
        pass

    def usable_by(self, *args):
        return RaceReason.ALLOWED

    def add_to_category(self, *args):
        pass


class RaceSetting(_BaseSetting):
    _module_name = 'races'
    _events = _callbacks

    def __init__(self, name):
        super().__init__(name, RACE_PATH)

        self.config['maximum'] = self.config.get('maximum', 0)

        for name, config in self.config['skills'].items():
            if config.get('maximum') is None:
                config['maximum'] = len(config['variables'][[*config['variables']][0]])

            config['required'] = config.get('required', 0)

            if isinstance(config['required'], int):
                config['required'] = [config['required']] * config['maximum']

            if 'cooldown' in config:
                if not isinstance(config['cooldown'], (list, tuple)):
                    config['cooldown'] = [config['cooldown']] * config['maximum']

            if isinstance(config.get('event'), str):
                config['event'] = [config['event']]

        # Did we not find a shortname in the strings?
        if 'shortname' not in self.strings:
            # Then we just use the race's name instead
            self.strings['shortname'] = self.strings['name']

    def usable_by(self, wcsplayer):
        data = {'reason':None}

        OnIsRaceUsable.manager.notify(wcsplayer, self, data)

        if data['reason'] is not None:
            return data['reason']

        restrictmap = self.config.get('restrictmap')

        if restrictmap:
            if global_vars.map_name in restrictmap:
                return RaceReason.MAP

        allowonly = self.config.get('allowonly')

        if allowonly:
            if wcsplayer._baseplayer.steamid2 in allowonly or wcsplayer._baseplayer.steamid3 in allowonly:
                reason = RaceReason.ALLOWED
            else:
                reason = RaceReason.PRIVATE

            if 'VIP' in allowonly:
                if wcsplayer.privileges.get('vip_raceaccess'):
                    reason = RaceReason.ALLOWED
                else:
                    if reason is not RaceReason.ALLOWED:
                        reason = RaceReason.VIP

            if 'ADMIN' in allowonly:
                if wcsplayer.privileges.get('wcsadmin_raceaccess'):
                    reason = RaceReason.ALLOWED
                else:
                    if reason is not RaceReason.ALLOWED:
                        reason = RaceReason.ADMIN

            if reason is not RaceReason.ALLOWED:
                return reason

        restrictteam = self.config.get('restrictteam')

        if restrictteam:
            ffa_enabled = cfg_ffa_enabled.get_int()

            # If FFA is enabled it should ignore the team restriction
            if not ffa_enabled:
                team = wcsplayer.player.team_index

                if team >= 2 and not restrictteam == team:
                    return RaceReason.TEAM

        restrictbot = self.config.get('restrictbot')

        if restrictbot and wcsplayer.fake_client:
            return RaceReason.BOT

        teamlimit = self.config.get('teamlimit')

        if teamlimit:
            team = wcsplayer.player.team_index

            if team >= 2:
                ffa_enabled = cfg_ffa_enabled.get_int()

                # If FFA is enabled the limit is considered to be for all the players on the server
                if ffa_enabled:
                    limit = list(chain.from_iterable([team_data[i][f'_internal_{self.name}_limit_allowed'] for i in team_data]))
                else:
                    limit = team_data[team].get(f'_internal_{self.name}_limit_allowed', [])

                if teamlimit <= len(limit) and wcsplayer.userid not in limit:
                    return RaceReason.TEAM_LIMIT

        maximum = self.config.get('maximum')

        if maximum:
            if wcsplayer.total_level >= maximum:
                return RaceReason.MAXIMUM_LEVEL

        required = self.config.get('required')

        if required and wcsplayer.total_level < required:
            if wcsplayer.fake_client and cfg_bot_ignore_level_requirement:
                pass
            else:
                return RaceReason.REQUIRED_LEVEL

        return RaceReason.ALLOWED

    def add_to_category(self, category):
        self._add_to_category(race_manager, 1, category, changerace_menu, raceinfo_menu)


class _RaceManager(_BaseManager):
    _instance = RaceSetting
    _module_name = 'races'
    _path = RACE_PATH
    _es_path = RACE_PATH_ES
    _listener = OnPluginRaceLoad

    def __init__(self):
        super().__init__()

        self._default_race = None

    def load_all(self):
        self._move_misplaced_files()

        config = self._get_or_create_config()

        self._load_categories_and_values(config)

        default_race = cfg_default_race.get_string()

        if default_race in self:
            self._default_race = default_race
            return

        if self:
            self._default_race = [*self][0]
            warn(f'Unable to find the default race "{default_race}". Using "{self._default_race}" as temporary default race.')
        else:
            self[None] = _FakeRace()

            warn(f'No races found (ESC: {IS_ESC_SUPPORT_ENABLED}) - limited access.')

    def unload_all(self):
        if None in self:
            del self[None]

        super().unload_all()

    @property
    def default_race(self):
        return self._default_race
race_manager = _RaceManager()
