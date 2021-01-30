# ../wcs/core/players/entity.py

# ============================================================================
# >> IMPORTS
# ============================================================================
# Python Imports
#   Collections
from collections import defaultdict
#   Itertools
from itertools import chain
#   JSON
from json import dump as json_dump
from json import load as json_load
#   Random
from random import choice
from random import randint
from random import uniform
#   Time
from time import time
#   Warnings
from warnings import warn

# Source.Python Imports
#   Commands
from commands import CommandReturn
from commands.say import SayFilter
#   Core
from core import GAME_NAME
#   CVars
from cvars import ConVar
#   Engines
from engines.server import global_vars
from engines.server import execute_server_command
#   Entities
from entities import TakeDamageInfo
from entities.constants import DamageTypes
from entities.helpers import index_from_pointer
from entities.hooks import EntityCondition
from entities.hooks import EntityPreHook
#   Events
from events import Event
#   Filters
from filters.weapons import WeaponClassIter
#   Hooks
from hooks.exceptions import except_hooks
#   Listeners
from listeners.tick import Delay
from listeners.tick import Repeat
from listeners.tick import RepeatStatus
#   Memory
from memory import make_object
#   Menus
from menus.base import _BaseMenu
from menus.base import _PagedMenuBase
#   Players
from players.dictionary import PlayerDictionary
from players.entity import Player as _Player
from players.helpers import index_from_userid
from players.helpers import userid_from_index
#   Weapons
from weapons.manager import weapon_manager
from weapons.restrictions import WeaponRestrictionHandler

# WCS Imports
#   Config
from ..config import cfg_interval
from ..config import cfg_bot_random_race
from ..config import cfg_new_player_bank_bonus
#   Constants
from ..constants import IS_ESC_SUPPORT_ENABLED
from ..constants import ModuleType
from ..constants import RaceReason
from ..constants import SkillReason
from ..constants.paths import CFG_PATH
#   Database
from ..database.manager import database_manager
from ..database.manager import statements
from ..database.thread import _thread
#   Listeners
from ..listeners import OnClientAuthorized
from ..listeners import OnClientDisconnect
from ..listeners import OnIsSkillExecutable
from ..listeners import OnPlayerChangeRace
from ..listeners import OnPlayerDelete
from ..listeners import OnPlayerDestroy
from ..listeners import OnPlayerLevelDown
from ..listeners import OnPlayerLevelUp
from ..listeners import OnPlayerQuery
from ..listeners import OnPlayerReady
from ..listeners import OnTakeDamage
from ..listeners import OnTakeDamageAlive
#   Helpers
from ..helpers.overwrites import SayText2
#   Menus
from ..menus import input_menu
#   Modules
from ..modules.items.calls import _callbacks as _item_callbacks
from ..modules.items.manager import item_manager
from ..modules.races.calls import _callbacks as _race_callbacks
from ..modules.races.manager import race_manager
#   Players
from . import BasePlayer
from . import index_from_accountid
from . import team_data
from . import set_weapon_name
#   Ranks
from ..ranks import rank_manager
#   Translations
from ..translations import chat_strings

# Is ESC supported?
if IS_ESC_SUPPORT_ENABLED:
    # EventScripts Imports
    #   ES
    import es
    #   ESC
    import esc

    # WCS Imports
    #   Helpers
    from ..helpers.esc.vars import cvars
    from ..helpers.esc.vars import cvar_wcs_dices
    from ..helpers.esc.vars import cvar_wcs_userid


# ============================================================================
# >> ALL DECLARATION
# ============================================================================
__all__ = (
    'Player',
)


# ============================================================================
# >> GLOBAL VARIABLES
# ============================================================================
if (CFG_PATH / 'privileges.json').isfile():
    with open(CFG_PATH / 'privileges.json') as inputfile:
        try:
            privileges = json_load(inputfile)
        except:
            warn('Unable to load the privileges.json file.')
            except_hooks.print_exception()

            privileges = {}

    for x in ('players', ):
        if x not in privileges:
            privileges[x] = {}
else:
    privileges = {
        'players':{
            'STEAMID_EXAMPLE1':{
                'wcsadmin': 1,
                'wcsadmin_githubaccess': 1,
                'wcsadmin_managementaccess': 1,
                'wcsadmin_playersmanagement': 1,
                'wcsadmin_raceaccess': 1,
                'vip_raceaccess': 1
            }
        }
    }

    with open(CFG_PATH / 'privileges.json', 'w') as outputfile:
        json_dump(privileges, outputfile, indent=4)


_restrictions = WeaponRestrictionHandler()

# TODO: Should I even be using this?
_players = PlayerDictionary()

_global_bypass = False
_round_started = True
_delays = defaultdict(set)
_save_queue = set()

input_invalid_message = SayText2(chat_strings['input invalid'])


# ============================================================================
# >> CLASSES
# ============================================================================
class _PlayerMeta(type):
    def __new__(mcs, name, bases, odict):
        cls = super().__new__(mcs, name, bases, odict)
        cls._players = {}
        cls._accountid_players = {}
        cls._reconnect_cache = {}

        return cls

    def __call__(cls, index, accountid=None):
        wcsplayer = cls._players.get(index)

        if wcsplayer is None:
            if accountid is not None:
                wcsplayer = cls._accountid_players.get(accountid)

                if wcsplayer is None:
                    wcsplayer = cls._accountid_players[accountid] = super().__call__(None, accountid)
                    wcsplayer._retrieve_data()

                return wcsplayer

            wcsplayer = cls._players[index] = super().__call__(index)

        return wcsplayer


class _RaceContainer(dict):
    def __init__(self, wcsplayer):
        super().__init__()

        self.wcsplayer = wcsplayer

    def __missing__(self, name):
        assert name in race_manager, f'Invalid race: {name}'

        settings = race_manager[name]

        race = self[name] = _Race(self.wcsplayer, name, 0, 1, 1)

        for skill_name, config in settings.config['skills'].items():
            race.skills[skill_name] = _Skill(self.wcsplayer, config, skill_name, 0, name)
            race.skills[skill_name]._type = settings.type

        return race


class _ItemContainer(dict):
    def __init__(self, wcsplayer):
        super().__init__()

        self.wcsplayer = wcsplayer

        self._maxitems = defaultdict(int)

    def __missing__(self, name):
        assert name in item_manager, f'Invalid item: {name}'

        item = self[name] = _Item(self.wcsplayer, name)

        return item


class _Stats(object):
    def __init__(self):
        self._data = defaultdict(int)
        self._modified = set()
        self._not_added = set()

    def __contains__(self, name):
        return name in self._data

    def __getitem__(self, name):
        return self._data[name]

    def __setitem__(self, name, value):
        self._modified.add(name)

        if name not in self._data:
            self._not_added.add(name)

        self._data[name] = value


class Player(object, metaclass=_PlayerMeta):
    def __init__(self, index, accountid=None):
        if index is None:
            self._index = None
            self._baseplayer = None
            self._accountid = accountid
        else:
            self._index = index
            self._baseplayer = BasePlayer(index)

        self._races = _RaceContainer(self)
        self._items = _ItemContainer(self)
        self._stats = _Stats()
        self._ready = False
        self._retrieving = False
        self._privileges = {}

        self._id = None
        self._name = None
        self._current_race = None
        self._lastconnect = None
        self._bank_level = None
        self._rested_xp = None

        self.data = {}

    def _retrieve_data(self):
        if self._retrieving:
            return

        self._retrieving = True

        if self.online:
            name = self._baseplayer.name
        else:
            name = None

        if not _thread.unloading:
            database_manager.execute('player get' + (' bot' if isinstance(self.accountid, str) else ''), (self.accountid, ), callback=self._query_get_player, name=name)

    def _query_get_player(self, result):
        if _thread.unloading:
            return

        data = result.fetchone()

        if data is None:
            database_manager.execute('player insert', (None if isinstance(self.accountid, str) else self.accountid, result['name'], race_manager.default_race, time(), cfg_new_player_bank_bonus.get_int(), 0))
            database_manager.execute('player get' + (' bot' if isinstance(self.accountid, str) else ''), (self.accountid, ), callback=self._query_get_player, name=result['name'])
            return

        self._id = data[0]
        self._name = data[1]
        self._current_race = data[2]
        self._lastconnect = data[3]
        self._bank_level = data[4]
        self._rested_xp = data[5]

        if self._current_race not in race_manager:
            self._current_race = race_manager.default_race

        if result['name'] is not None:
            self._name = result['name']

        if self._bank_level is None:
            self._bank_level = cfg_new_player_bank_bonus.get_int()

        if self._rested_xp is None:
            self._rested_xp = 0

        database_manager.execute('race get', (self.id, ), callback=self._query_get_races)
        database_manager.execute('skill get', (self.id, ), callback=self._query_get_skills)
        database_manager.execute('stat get', (self._id, ), callback=self._query_get_stats)
        database_manager.execute('stat module get', (self._id, ), callback=self._query_get_module_stats, format_args=('races', ), type='races')
        database_manager.execute('stat module get', (self._id, ), callback=self._query_get_module_stats, format_args=('items', ), type='items')
        database_manager.callback(self._query_final)

    def _query_get_races(self, result):
        if _thread.unloading:
            return

        data = result.fetchall()

        if data:
            for name, xp, level, unused in data:
                if name in race_manager:
                    self._races[name] = _Race(self, name, xp, level, unused, _added=True)

    def _query_get_skills(self, result):
        if _thread.unloading:
            return

        data = result.fetchall()

        if data:
            for skill_name, race_name, level in data:
                settings = race_manager.get(race_name)

                if settings is not None:
                    if skill_name in settings.config.get('skills', []):
                        self._races[race_name].skills[skill_name] = _Skill(self, settings.config['skills'][skill_name], skill_name, level, race_name, _added=True)
                        self._races[race_name].skills[skill_name]._type = settings.type

        for race_name, settings in race_manager.items():
            race = self._races.get(race_name)

            if race is not None:
                for skill_name in settings.config.get('skills', []):
                    if skill_name not in race.skills:
                        race.skills[skill_name] = _Skill(self, settings.config['skills'][skill_name], skill_name, 0, race_name)
                        race.skills[skill_name]._type = settings.type

    def _query_get_stats(self, result):
        if _thread.unloading:
            return

        data = result.fetchall()

        if data:
            for key, value in data:
                self.stats._data[key] = value

    def _query_get_module_stats(self, result):
        if _thread.unloading:
            return

        data = result.fetchall()

        if data:
            if result['type'] == 'races':
                for owner, key, value in data:
                    if owner in race_manager:
                        self.races[owner].stats._data[key] = value
            else:
                for owner, key, value in data:
                    if owner in item_manager:
                        self.items[owner].stats._data[key] = value

    def _query_final(self, result):
        if _thread.unloading:
            return

        online = self.online

        if online:
            if self.active_race.settings.usable_by(self) is not RaceReason.ALLOWED or (self.fake_client and cfg_bot_random_race.get_int()):
                usable_races = self.available_races

                if not usable_races:
                    self._ready = False

                    raise RuntimeError(f'Unable to find a usable race to "{self.name}".')

                self._current_race = choice(usable_races)

        self._ready = True

        OnPlayerQuery.manager.notify(self)

        # We need to make sure the player is in the server
        if online:
            team = self.player.team_index

            if team >= 2:
                key = f'_internal_{self._current_race}_limit_allowed'

                if key not in team_data[team]:
                    team_data[team][key] = []

                team_data[team][key].append(self.userid)

            OnPlayerReady.manager.notify(self)

    def _query_save(self, result):
        # We don't want them to have previous data
        # This has to be done here, as it'll cause errors if it's done in OnClientDisconnect
        self.data.clear()

        _save_queue.discard(self.accountid)

        try:
            self._index = index_from_accountid(self.accountid)
        except ValueError:
            OnPlayerDestroy.manager.notify(self)
        else:
            self._baseplayer = BasePlayer(self._index)

            Player._players[self.index] = self

            Player._reconnect_cache[self.accountid] = self

            on_client_authorized(self._baseplayer)

            if self.ready:
                if self.active_race.settings.usable_by(self) is not RaceReason.ALLOWED or (self.fake_client and cfg_bot_random_race.get_int()):
                    usable_races = self.available_races

                    if not usable_races:
                        self._ready = False

                        raise RuntimeError(f'Unable to find a usable race to "{self.name}".')

                    self._current_race = choice(usable_races)

                OnPlayerQuery.manager.notify(self)

                team = self.player.team_index

                if team >= 2:
                    key = f'_internal_{self._current_race}_limit_allowed'

                    if key not in team_data[team]:
                        team_data[team][key] = []

                    team_data[team][key].append(self.userid)

                OnPlayerReady.manager.notify(self)

    def save(self):
        assert self.ready

        # TODO: This could use a hand...

        database_manager.execute('player update', (self.name, self._current_race, self._lastconnect, self._bank_level, self._rested_xp, self._id))

        races = []
        skills = []
        stats = []
        stats_races = []
        stats_items = []

        for race_name, race in self._races.items():
            if not race._added and race._modified:
                race._added = True
                races.append((race_name, self.id))

            for skill_name, skill in race.skills.items():
                if not skill._added and skill._modified:
                    skill._added = True
                    skills.append((skill_name, race_name, self.id))

            for stat in race.stats._not_added:
                stats_races.append((race_name, stat, race.stats[stat], self.id))

            race.stats._not_added.clear()

        for item_name, item in self._items.items():
            for stat in item.stats._not_added:
                stats_items.append((item_name, stat, item.stats[stat], self.id))

            item.stats._not_added.clear()

        for stat in self.stats._not_added:
            stats.append((stat, self.stats[stat], self.id))

        self.stats._not_added.clear()

        if races:
            database_manager.executemany('race insert', races)

        if skills:
            database_manager.executemany('skill insert', skills)

        if stats:
            database_manager.executemany('stat insert', stats)

        if stats_races:
            database_manager.executemany('stat module insert', stats_races, format_args=('races', ))

        if stats_items:
            database_manager.executemany('stat module insert', stats_items, format_args=('items', ))

        reset = False

        if any([race._modified for race in self._races.values()]):
            reset = True

            join = statements['race join']

            xp = ' '.join([join.format(race_name, race.xp) for race_name, race in self._races.items() if race._modified])
            level = ' '.join([join.format(race_name, race.level) for race_name, race in self._races.items() if race._modified])
            unused = ' '.join([join.format(race_name, race.unused) for race_name, race in self._races.items() if race._modified])

            database_manager.execute('race update', (self._id, ), format_args=(xp, level, unused))

        if any([skill._modified for race in self._races.values() for skill in race.skills.values()]):
            reset = True

            join = statements['skill join']

            level = ' '.join([join.format(race_name, skill_name, skill.level) for race_name, race in self._races.items() for skill_name, skill in race.skills.items() if skill._modified])

            database_manager.execute('skill update', (self._id, ), format_args=(level, ))

        if self.stats._modified:
            join = statements['stat join']

            value = ' '.join([join.format(key, self.stats[key]) for key in self.stats._modified])

            database_manager.execute('stat update', (self._id, ), format_args=(value, ))

            self.stats._modified.clear()

        if any([race.stats._modified for race in self._races.values()]):
            join = statements['stat module join']

            value = ' '.join([join.format(race_name, key, race.stats[key]) for race_name, race in self._races.items() for key in race.stats._modified])

            database_manager.execute('stat module update', (self._id, ), format_args=('races', value))

            for race in self._races.values():
                race.stats._modified.clear()

        if any([item.stats._modified for item in self._items.values()]):
            join = statements['stat module join']

            value = ' '.join([join.format(item_name, key, item.stats[key]) for item_name, item in self._items.items() for key in item.stats._modified])

            database_manager.execute('stat module update', (self._id, ), format_args=('items', value))

            for item in self._items.values():
                item.stats._modified.clear()

        if reset:
            for race in self._races.values():
                race._modified = False

                for skill in race.skills.values():
                    skill._modified = False

    def take_damage(self, damage, attacker, weapon=None, skip_hooks=True):
        # TODO: This method should not have been called if the victim is already dead
        assert not self.player.dead

        if not self.player.dead:
            global _global_bypass

            _global_bypass = skip_hooks

            take_damage_info = TakeDamageInfo()
            take_damage_info.attacker = attacker

            if weapon is None:
                index = set_weapon_name('point_hurt', None)
            else:
                index = set_weapon_name(weapon)

            take_damage_info.weapon = index
            take_damage_info.inflictor = index
            take_damage_info.damage = damage
            take_damage_info.type = DamageTypes.GENERIC

            try:
                self.player.on_take_damage(take_damage_info)
            finally:
                _global_bypass = False

    def take_delayed_damage(self, damage, attacker, skip_hooks=True):
        # TODO: This method should not have been called if the victim is already dead
        assert not self.player.dead

        attacker = userid_from_index(attacker)

        delay = Delay(0, self._take_delayed_damage, args=(damage, attacker, skip_hooks))
        delay.args += (delay, )

        _delays[self.userid].add(delay)

    def _take_delayed_damage(self, damage, attacker, skip_hooks, delay):
        _delays[self.userid].discard(delay)

        assert not self.player.dead

        try:
            attacker = index_from_userid(attacker)
        except ValueError:
            attacker = 0

        self.take_damage(damage, attacker, skip_hooks)

    def request_input(self, callback, return_menu=None):
        assert self.data.get('_internal_input_callback') is None

        self.data['_internal_input_callback'] = callback
        self.data['_internal_input_menu'] = return_menu
        self.data['_internal_input_repeat'] = Repeat(self._request_update)
        self.data['_internal_input_repeat'].start(0.25, 39)
        self.data['_internal_input_delay'] = Delay(10, self._request_end)

        return input_menu

    def _request_update(self):
        if self.data['_internal_input_repeat'].status == RepeatStatus.RUNNING:
            input_menu._refresh(self.index)

    def _request_receive(self, value):
        self.data['_internal_input_delay'].cancel()

        try:
            accepted = self.data['_internal_input_callback'](self, value)
        except:
            except_hooks.print_exception()
        else:
            if isinstance(accepted, (_BaseMenu, _PagedMenuBase)):
                accepted.send(self.index)

                self.data['_internal_input_menu'] = None
            elif not accepted:
                input_invalid_message.send(self.index, value=value)
        finally:
            self._request_end()

    def _request_end(self):
        if self.data['_internal_input_repeat'].status == RepeatStatus.RUNNING:
            self.data['_internal_input_repeat'].stop()

        input_menu.close(self.index)

        if self.data['_internal_input_menu'] is not None:
            self.data['_internal_input_menu'].send(self.index)

        del self.data['_internal_input_callback']
        del self.data['_internal_input_menu']
        del self.data['_internal_input_repeat']
        del self.data['_internal_input_delay']

    @property
    def userid(self):
        return self._baseplayer.userid

    @property
    def index(self):
        assert self._index == self._baseplayer.index

        return self._index

    @property
    def fake_client(self):
        return self._baseplayer.fake_client

    @property
    def online(self):
        try:
            return self._baseplayer.connected
        except AttributeError:
            return False

    @property
    def accountid(self):
        try:
            return self._baseplayer.accountid
        except AttributeError:
            return self._accountid

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def lastconnect(self):
        return self._lastconnect

    @property
    def ready(self):
        return self._ready

    @property
    def privileges(self):
        return self._privileges

    @property
    def player(self):
        return _Player(self.index)
        # return _players[self.index]

    @property
    def current_race(self):
        return self._current_race

    @current_race.setter
    def current_race(self, value):
        old = self._current_race

        assert old != value
        assert value in race_manager

        self.execute('changefromcmd', define=True)

        team = self.player.team

        if team >= 2:
            team_data[team][f'_internal_{old}_limit_allowed'].remove(self.userid)

            if not team_data[team][f'_internal_{old}_limit_allowed']:
                del team_data[team][f'_internal_{old}_limit_allowed']

            if f'_internal_{value}_limit_allowed' not in team_data[team]:
                team_data[team][f'_internal_{value}_limit_allowed'] = []

            team_data[team][f'_internal_{value}_limit_allowed'].append(self.userid)

        _restrictions.player_restrictions[self.userid].clear()

        restricted_weapons = race_manager[value].config.get('restrictweapon', [])

        if restricted_weapons:
            weapons = set()

            for weapon in restricted_weapons:
                if weapon.startswith('#'):
                    weapons.update(map(lambda weapon_inst: weapon_inst.name, WeaponClassIter(weapon[1:])))
                elif weapon.startswith('!'):
                    # Objective items will never be restricted unless explicitly told
                    weapons.update(map(lambda weapon_inst: weapon_inst.name, WeaponClassIter(not_filters=['objective', weapon[1:]])))
                else:
                    weapons.add(weapon)

            _restrictions.add_player_restrictions(self.player, *[weapon for weapon in weapons if weapon in weapon_manager])

        self._current_race = value

        self.execute('changeintocmd', define=True)

        OnPlayerChangeRace.manager.notify(self, old, value)

    @property
    def active_race(self):
        return self._races[self.current_race]

    @property
    def races(self):
        return self._races

    @property
    def items(self):
        return self._items

    @property
    def stats(self):
        return self._stats

    @property
    def skills(self):
        return self.active_race.skills

    @property
    def xp(self):
        return self.active_race.xp

    @xp.setter
    def xp(self, value):
        self.active_race.xp = value

    @property
    def required_xp(self):
        return self.active_race.required_xp

    @property
    def level(self):
        return self.active_race.level

    @level.setter
    def level(self, value):
        self.active_race.level = value

    @property
    def total_level(self):
        return sum([race.level for race in self._races.values()])

    @property
    def bank_level(self):
        return self._bank_level

    @bank_level.setter
    def bank_level(self, value):
        self._bank_level = value

    @property
    def rested_xp(self):
        return self._rested_xp

    @rested_xp.setter
    def rested_xp(self, value):
        self._rested_xp = value

    @property
    def unused(self):
        return self.active_race.unused

    @unused.setter
    def unused(self, value):
        self.active_race.unused = value

    @property
    def available_races(self):
        return [race_name for race_name, settings in race_manager.items() if settings.usable_by(self) is RaceReason.ALLOWED]

    @property
    def rank(self):
        return rank_manager.from_accountid(self.accountid)

    @property
    def notify(self):
        assert self.ready
        return self.active_race.notify

    @property
    def execute(self):
        assert self.ready
        return self.active_race.execute

    @classmethod
    def from_userid(cls, userid):
        return cls(index_from_userid(userid))

    @classmethod
    def from_accountid(cls, accountid):
        try:
            index = index_from_accountid(accountid)
        except ValueError:
            return cls(None, accountid)
        else:
            return cls(index)


class _Race(object):
    def __init__(self, wcsplayer, name, xp, level, unused, _added=False):
        self.wcsplayer = wcsplayer
        self.name = name
        self._xp = xp
        self._level = level
        self._unused = unused

        self._added = _added
        self._modified = False
        self._stats = _Stats()

        self.skills = {}
        self.settings = race_manager[name]

    def _upgrade_skills(self):
        skills = [x for x in self.skills.values() if x.level < x.config['maximum']]

        if skills:
            levels = defaultdict(int)
            unused = 0

            for _ in range(self.unused):
                unused += 1

                skill = choice(skills)

                levels[skill] += 1

                if skill.level + levels[skill] == skill.config['maximum']:
                    skills.remove(skill)

                    if not skills:
                        break

            if unused:
                self.unused -= unused

                for skill, level in levels.items():
                    skill.level += level

    def notify(self, event, name=None):
        if name is None:
            name = event.name

        for skill_name, data in self.settings.config['skills'].items():
            if name in data['event']:
                skill = self.skills[skill_name]
                level = skill.level

                if level:
                    variables = {}

                    for variable, values in skill.config['variables'].items():
                        variables[variable] = values[level - 1] if level <= len(values) else values[-1]

                    if skill._type is ModuleType.SP:
                        callback = _race_callbacks.get(self.name, {}).get(skill_name, {}).get(name)

                        if callback is not None:
                            if event is None:
                                callback(self.wcsplayer, variables)
                            else:
                                callback(event, self.wcsplayer, variables)
                    elif skill._type is ModuleType.ESP:
                        callback = es.addons.Blocks.get(f'wcs/modules/races/{self.name}/{skill_name}')

                        if callback is not None:
                            if event is None:
                                callback(self.wcsplayer, variables)
                            else:
                                callback(es.event_var, self.wcsplayer, variables)
                    elif skill._type is ModuleType.ESS:
                        addon = esc.addons.get(f'wcs/modules/races/{self.name}')

                        if addon is not None:
                            executor = addon.blocks.get(skill_name)

                            if executor is not None:
                                for cvar in cvar_wcs_dices:
                                    cvar.set_int(randint(0, 100))

                                for variable, values in variables.items():
                                    variable = f'wcs_{variable}'
                                    cvar = cvars.get(variable)

                                    if cvar is None:
                                        cvar = cvars[variable] = ConVar(variable, '0')

                                    if isinstance(values, list):
                                        if isinstance(values[0], float) or isinstance(values[1], float):
                                            cvar.set_float(uniform(*values))
                                        else:
                                            cvar.set_int(randint(*values))
                                    else:
                                        if isinstance(values, float):
                                            cvar.set_float(values)
                                        else:
                                            cvar.set_int(values)

                                executor.run()
                    elif skill._type is ModuleType.ESS_INI or skill._type is ModuleType.ESS_KEY:
                        for cvar in cvar_wcs_dices:
                            cvar.set_int(randint(0, 100))

                        try:
                            commands = skill.config['cmds']['setting'][level - 1]
                        except IndexError:
                            commands = skill.config['cmds']['setting'][-1]

                        if commands:
                            for cmd in commands.split(';'):
                                try:
                                    execute_server_command('es', cmd)
                                except ValueError:
                                    except_hooks.print_exception()
                                    break

                        for key in ('cmd', 'sfx'):
                            commands = skill.config['cmds'][key]

                            if commands:
                                for cmd in commands.split(';'):
                                    try:
                                        execute_server_command('es', cmd)
                                    except ValueError:
                                        except_hooks.print_exception()
                                        break

        for item in self.wcsplayer.items.values():
            if name in item.settings.config['event']:
                if item.settings.type is ModuleType.SP:
                    callback = _item_callbacks.get(item.name, {}).get(name)

                    if callback is not None:
                        for _ in range(item.count):
                            if event is None:
                                callback(self.wcsplayer)
                            else:
                                callback(event, self.wcsplayer)
                elif item.settings.type is ModuleType.ESP:
                    # Adding an underscore (_) at the end to prevent it from being registered as an event
                    callback = es.addons.Blocks.get(f'wcs/modules/items/{item.name}/{name}_')

                    if callback is not None:
                        for _ in range(item.count):
                            if event is None:
                                callback(self.wcsplayer)
                            else:
                                callback(es.event_var, self.wcsplayer)
                elif item.settings.type is ModuleType.ESS:
                    addon = esc.addons.get(f'wcs/modules/items/{item.name}')

                    if addon is not None:
                        executor = addon.blocks.get(name)

                        if executor is not None:
                            for _ in range(item.count):
                                executor.run()
                elif item.settings.type is ModuleType.ESS_INI or item.settings.type is ModuleType.ESS_KEY:
                    commands = item.settings.cmds.get('activatecmd')

                    if commands is not None and commands:
                        for _ in range(item.count):
                            for cmd in commands.split(';'):
                                try:
                                    execute_server_command('es', cmd)
                                except ValueError:
                                    except_hooks.print_exception()
                                    break

    def execute(self, name, event=None, define=False):
        if self.settings.type is ModuleType.SP:
            callback = _race_callbacks.get(self.name, {}).get(name)

            if callback is not None:
                if event is None:
                    callback(self.wcsplayer)
                else:
                    callback(event, self.wcsplayer)
        elif self.settings.type is ModuleType.ESP:
            callback = es.addons.Blocks.get(f'wcs/modules/races/{self.name}/{name}')

            if callback is not None:
                if event is None:
                    callback(self.wcsplayer)
                else:
                    callback(es.event_var, self.wcsplayer)
        elif self.settings.type is ModuleType.ESS:
            addon = esc.addons.get(f'wcs/modules/races/{self.name}')

            if addon is not None:
                executor = addon.blocks.get(name)

                if executor is not None:
                    if define:
                        cvar_wcs_userid.set_int(self.wcsplayer.userid)

                    executor.run()
        elif self.settings.type is ModuleType.ESS_INI or self.settings.type is ModuleType.ESS_KEY:
            commands = self.settings.cmds.get(name)

            if commands is not None and commands:
                if define:
                    cvar_wcs_userid.set_int(self.wcsplayer.userid)

                for cmd in commands.split(';'):
                    try:
                        execute_server_command('es', cmd)
                    except ValueError:
                        except_hooks.print_exception()
                        break

    @property
    def required_xp(self):
        return cfg_interval.get_int() * self.level

    @property
    def xp(self):
        return self._xp

    @xp.setter
    def xp(self, value):
        maximum_race_level = self.settings.config.get('maximum_race_level', 0)

        if maximum_race_level and self.level >= maximum_race_level:
            raise ValueError('Cannot modify xp of a race which is maxed.')

        self._modified = True

        new_level = self.level

        required_xp = self.required_xp
        interval = cfg_interval.get_int()

        while value >= required_xp:
            value -= required_xp

            new_level += 1

            if new_level == maximum_race_level:
                value = 0
                break

            required_xp += interval

        self._xp = value

        if not new_level == self.level:
            self.level = new_level

    @property
    def level(self):
        return self._level

    @level.setter
    def level(self, value):
        maximum_race_level = self.settings.config.get('maximum_race_level', 0)

        if maximum_race_level and self.level >= maximum_race_level and value >= maximum_race_level:
            raise ValueError('Cannot give levels to a race which is maxed.')

        self._modified = True

        from_level = self.level

        if maximum_race_level:
            value = min(maximum_race_level, value)

        self.unused += value - from_level

        self._level = value

        # TODO: Find a proper sound
        # if self.wcsplayer.current_race == self.name:
        #     player = self.wcsplayer.player

        #     if player.dead:
        #         if not self.wcsplayer.fake_client:
        #             player.play_sound('ambient/machines/teleport1.wav', volume=0.4)
        #     else:
        #         player.emit_sound('ambient/machines/teleport1.wav', volume=0.8, attenuation=0.3)

        if value > from_level:
            OnPlayerLevelUp.manager.notify(self.wcsplayer, self, from_level)

            if self.wcsplayer.fake_client:
                self._upgrade_skills()
        else:
            OnPlayerLevelDown.manager.notify(self.wcsplayer, self, from_level)

    @property
    def unused(self):
        return self._unused

    @unused.setter
    def unused(self, value):
        self._modified = True

        self._unused = value

    @property
    def stats(self):
        return self._stats


class _Skill(object):
    def __init__(self, wcsplayer, config, name, level, race_name, _added=False):
        self.wcsplayer = wcsplayer
        self.name = name
        self.config = config

        self._level = level
        self._cooldown = 0

        self._race_name = race_name
        self._added = _added
        self._modified = False

        self._type = None

    def execute(self, name=None, event=None, define=False):
        if self.level:
            variables = {}

            for variable, values in self.config['variables'].items():
                variables[variable] = values[self.level - 1] if self.level <= len(values) else values[-1]

            if self._type is ModuleType.SP:
                callback = _race_callbacks.get(self._race_name, {}).get(self.name, {}).get(name or event.name)

                if callback is not None:
                    if event is None:
                        callback(self.wcsplayer, variables)
                    else:
                        callback(event, self.wcsplayer, variables)
            elif self._type is ModuleType.ESP:
                callback = es.addons.Blocks.get(f'wcs/modules/races/{self._race_name}/{self.name}')

                if callback is not None:
                    if event is None:
                        callback(self.wcsplayer, variables)
                    else:
                        callback(es.event_var, self.wcsplayer, variables)
            elif self._type is ModuleType.ESS:
                addon = esc.addons.get(f'wcs/modules/races/{self._race_name}')

                if addon is not None:
                    executor = addon.blocks.get(self.name)

                    if executor is not None:
                        if define:
                            cvar_wcs_userid.set_int(self.wcsplayer.userid)

                        for cvar in cvar_wcs_dices:
                            cvar.set_int(randint(0, 100))

                        for variable, values in variables.items():
                            variable = f'wcs_{variable}'
                            cvar = cvars.get(variable)

                            if cvar is None:
                                cvar = cvars[variable] = ConVar(variable, '0')

                            if isinstance(values, list):
                                if isinstance(values[0], float) or isinstance(values[1], float):
                                    cvar.set_float(uniform(*values))
                                else:
                                    cvar.set_int(randint(*values))
                            else:
                                if isinstance(values, float):
                                    cvar.set_float(values)
                                else:
                                    cvar.set_int(values)

                        executor.run()
            elif self._type is ModuleType.ESS_INI or self._type is ModuleType.ESS_KEY:
                if define:
                    cvar_wcs_userid.set_int(self.wcsplayer.userid)

                for cvar in cvar_wcs_dices:
                    cvar.set_int(randint(0, 100))

                try:
                    commands = self.config['cmds']['setting'][self.level - 1]
                except IndexError:
                    commands = self.config['cmds']['setting'][-1]

                if commands:
                    for cmd in commands.split(';'):
                        try:
                            execute_server_command('es', cmd)
                        except ValueError:
                            except_hooks.print_exception()
                            break

                for key in ('cmd', 'sfx'):
                    commands = self.config['cmds'][key]

                    if commands:
                        for cmd in commands.split(';'):
                            try:
                                execute_server_command('es', cmd)
                            except ValueError:
                                except_hooks.print_exception()
                                break

    def is_executable(self):
        data = {'reason':None}

        OnIsSkillExecutable.manager.notify(self.wcsplayer, self, data)

        if data['reason'] is not None:
            return data['reason']

        if not self.level:
            return SkillReason.LEVEL

        if self.wcsplayer.player.team_index < 2 and GAME_NAME not in ('hl2mp', ):
            return SkillReason.TEAM

        if self.wcsplayer.player.dead:
            return SkillReason.DEAD

        if not _round_started:
            return SkillReason.DEACTIVATED

        if self.cooldown_seconds:
            if self.cooldown > time():
                return SkillReason.COOLDOWN

        return SkillReason.ALLOWED

    def reset_cooldown(self, value=None):
        if value is None:
            value = self.cooldown_seconds

        self.cooldown = time() + value

    @property
    def level(self):
        return self._level

    @level.setter
    def level(self, value):
        self._modified = True

        self._level = value

    @property
    def cooldown(self):
        return self._cooldown

    @cooldown.setter
    def cooldown(self, value):
        self._cooldown = value

    @property
    def cooldown_seconds(self):
        if 'cooldown' in self.config:
            try:
                return self.config['cooldown'][self.level - 1]
            except IndexError:
                return self.config['cooldown'][-1]

        return 0


class _Item(object):
    def __init__(self, wcsplayer, name):
        self.wcsplayer = wcsplayer
        self.name = name

        self._count = 0
        self._stats = _Stats()

        self.settings = item_manager[name]

    def execute(self, name, event=None, define=False):
        if self.settings.type is ModuleType.SP:
            callback = _item_callbacks.get(self.name, {}).get(name)

            if callback is not None:
                if event is None:
                    callback(self.wcsplayer)
                else:
                    callback(event, self.wcsplayer)
        elif self.settings.type is ModuleType.ESP:
            callback = es.addons.Blocks.get(f'wcs/modules/items/{self.name}/{name}')

            if callback is not None:
                if event is None:
                    callback(self.wcsplayer)
                else:
                    callback(es.event_var, self.wcsplayer)
        elif self.settings.type is ModuleType.ESS:
            addon = esc.addons.get(f'wcs/modules/items/{self.name}')

            if addon is not None:
                executor = addon.blocks.get(name)

                if executor is not None:
                    if define:
                        cvar_wcs_userid.set_int(self.wcsplayer.userid)

                    executor.run()
        elif self.settings.type is ModuleType.ESS_INI or self.settings.type is ModuleType.ESS_KEY:
            commands = self.settings.cmds.get(name)

            if commands is not None and commands:
                if define:
                    cvar_wcs_userid.set_int(self.wcsplayer.userid)

                for cmd in commands.split(';'):
                    try:
                        execute_server_command('es', cmd)
                    except ValueError:
                        except_hooks.print_exception()
                        break

    @property
    def count(self):
        return self._count

    @count.setter
    def count(self, value):
        assert value >= 0
        assert self.count + value >= 0

        difference = value - self.count

        for category in self.settings.config['categories']:
            self.wcsplayer.items._maxitems[category] += difference

        self._count = value

    @property
    def stats(self):
        return self._stats


# ============================================================================
# >> LISTENERS
# ============================================================================
@OnClientAuthorized
def on_client_authorized(baseplayer):
    wcsplayer = Player._accountid_players.pop(baseplayer.accountid, None)

    if wcsplayer is None:
        wcsplayer = Player._reconnect_cache.pop(baseplayer.accountid, None)

        if wcsplayer is None:
            if baseplayer.accountid in _save_queue:
                return

            wcsplayer = Player(baseplayer.index)

            wcsplayer._privileges = privileges['players'].get(baseplayer.steamid2, {}) or privileges['players'].get(baseplayer.steamid3, {})

            wcsplayer._retrieve_data()
        else:
            wcsplayer._baseplayer = baseplayer
    else:
        Player._players[baseplayer.index] = wcsplayer

        wcsplayer._index = baseplayer.index
        wcsplayer._baseplayer = baseplayer

        # Not really needed...
        del wcsplayer._accountid


@OnClientDisconnect
def on_client_disconnect(baseplayer):
    wcsplayer = Player._players.pop(baseplayer.index, None)

    if baseplayer.accountid in _save_queue or wcsplayer is None:
        return

    OnPlayerDelete.manager.notify(wcsplayer)

    for delay in _delays.pop(baseplayer.userid, []):
        delay.cancel()

    if wcsplayer.ready:
        wcsplayer._lastconnect = time()
        wcsplayer.save()

    _save_queue.add(baseplayer.accountid)

    database_manager.callback(wcsplayer._query_save)


@EntityPreHook(EntityCondition.is_player, 'on_take_damage')
def pre_on_take_damage(stack):
    if _global_bypass:
        return

    info = make_object(TakeDamageInfo, stack[1])

    try:
        attacker = info.attacker
    except ValueError:
        attacker = 0

    if 0 < attacker <= global_vars.max_clients:
        wcsattacker = Player(attacker)
    else:
        wcsattacker = None

    index = index_from_pointer(stack[0])
    wcsvictim = Player(index)

    OnTakeDamage.manager.notify(wcsvictim, wcsattacker, info)


@EntityPreHook(EntityCondition.is_player, 'on_take_damage_alive')
def pre_on_take_damage_alive(stack):
    if _global_bypass:
        return

    info = make_object(TakeDamageInfo, stack[1])

    try:
        attacker = info.attacker
    except ValueError:
        attacker = 0

    if 0 < attacker <= global_vars.max_clients:
        wcsattacker = Player(attacker)
    else:
        wcsattacker = None

    index = index_from_pointer(stack[0])
    wcsvictim = Player(index)

    OnTakeDamageAlive.manager.notify(wcsvictim, wcsattacker, info)


# ============================================================================
# >> EVENTS
# ============================================================================
@Event('round_prestart')
def round_prestart(event):
    for delay in chain.from_iterable(_delays.values()):
        delay.cancel()

    _delays.clear()


@Event('round_start')
def round_start(event):
    if IS_ESC_SUPPORT_ENABLED:
        cvars['wcs_wardencounter'].set_int(cvars['wcs_wardencounter'].get_int() + 1)


@Event('round_freeze_end')
def round_freeze_end(event):
    global _round_started
    _round_started = True

    if IS_ESC_SUPPORT_ENABLED:
        cvars['wcs_gamestarted'].set_int(1)


@Event('round_end')
def round_end(event):
    global _round_started
    _round_started = False

    if IS_ESC_SUPPORT_ENABLED:
        cvars['wcs_wardencounter'].set_int(cvars['wcs_wardencounter'].get_int() - 1)
        cvars['wcs_roundcounter'].set_int(cvars['wcs_roundcounter'].get_int() + 1)
        cvars['wcs_gamestarted'].set_int(1)


@Event('player_death')
def player_death(event):
    userid = event['userid']

    for delay in _delays[userid]:
        delay.cancel()

    del _delays[userid]


# ============================================================================
# >> COMMANDS
# ============================================================================
@SayFilter
def say_filter(command, index, team_only):
    wcsplayer = Player(index)
    menu = wcsplayer.data.get('_internal_input_menu')

    if menu is not None:
        wcsplayer._request_receive(command.command_string)

        return CommandReturn.BLOCK
