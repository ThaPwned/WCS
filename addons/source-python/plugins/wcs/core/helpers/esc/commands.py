# ../wcs/core/helpers/esc/commands.py

# ============================================================================
# >> IMPORTS
# ============================================================================
# Python Imports
#   Collections
from collections import defaultdict
#   Random
from random import choice
from random import randint
#   Shlex
from shlex import split
#   String
from string import Template
#   Time
from time import time
#   Warnings
from warnings import warn

# Source.Python Imports
#   Colors
from colors import Color
#   Commands
from commands.typed import InvalidArgumentValue
from commands.typed import TypedServerCommand
#   Core
from core import GAME_NAME
#   CVars
from cvars import ConVar
#   Engines
from engines.precache import Model
from engines.server import execute_server_command
from engines.server import global_vars
from engines.trace import ContentMasks
from engines.trace import engine_trace
from engines.trace import GameTrace
from engines.trace import Ray
from engines.trace import TraceFilterSimple
#   Entities
from entities.constants import DamageTypes
from entities.constants import MoveType
from entities.constants import TakeDamage
from entities.entity import Entity
#   Events
from events import Event
from events.hooks import PreEvent
#   Filters
from filters.players import PlayerIter
from filters.weapons import WeaponClassIter
#   Keyvalues
from _keyvalues import KeyValues
# NOTE: Have to prefix it with a _ otherwise it'd import KeyValues from ES Emulator if it's loaded
#   Listeners
from listeners import OnPlayerRunCommand
from listeners.tick import Delay
from listeners.tick import Repeat
from listeners.tick import RepeatStatus
#   Mathlib
from mathlib import NULL_VECTOR
from mathlib import QAngle
from mathlib import Vector
#   Messages
from messages import Fade
from messages import FadeFlags
from messages import HudMsg
from messages import KeyHintText
from messages import SayText2
from messages import Shake
#   Players
from players.dictionary import PlayerDictionary
from players.entity import Player
from players.helpers import index_from_userid
#   Translations
from translations.strings import LangStrings
#   Weapons
from weapons.dictionary import WeaponDictionary
from weapons.manager import weapon_manager
from weapons.restrictions import WeaponRestrictionHandler

# EventScripts Imports
#   Playerlib
from playerlib import Player as _PLPlayer
from playerlib import getPlayer

# WCS Imports
#   Constants
from ...constants import COLOR_DARKGREEN
from ...constants import COLOR_DEFAULT
from ...constants import COLOR_GREEN
from ...constants import COLOR_LIGHTGREEN
from ...constants.paths import CFG_PATH
from ...constants.paths import TRANSLATION_PATH
#   Helpers
from .converts import valid_userid
from .converts import valid_userid_and_team
from .converts import convert_userid_to_player
from .converts import convert_userid_to_wcsplayer
from .converts import convert_identifier_to_players
from .converts import convert_userid_identifier_to_players
from .converts import any_value
from .converts import valid_operators
from .converts import convert_to_vector
from .converts import split_str
from .converts import deprecated
from .est.commands import armor_command  # Just to load it
from .est.effects import effect101  # Just to load it
from ..wards import DamageWard
from ..wards import ward_manager
#   Listeners
from ...listeners import OnPlayerChangeRace
from ...listeners import OnPlayerDelete
from ...listeners import OnTakeDamageAlive
#   Modules
from ...modules.races.manager import race_manager
#   Players
from ...players import set_weapon_name
from ...players import team_data
from ...players.entity import Player as WCSPlayer


# ============================================================================
# >> GLOBAL VARIABLES
# ============================================================================
_aliases = {}

if (TRANSLATION_PATH / 'strings.ini').isfile():
    _strings = LangStrings(TRANSLATION_PATH / 'strings')

    for key in _strings:
        for language, message in _strings[key].items():
            _strings[key][language] = message.replace('#default', COLOR_DEFAULT).replace('#green', COLOR_GREEN).replace('#lightgreen', COLOR_LIGHTGREEN).replace('#darkgreen', COLOR_DARKGREEN)
else:
    _strings = None

_restrictions = WeaponRestrictionHandler()
_all_weapons = set([x.basename for x in WeaponClassIter('all', ['melee', 'objective'])])

if (CFG_PATH / 'es_WCSlanguage_db.txt').isfile():
    _languages = KeyValues.load_from_file(CFG_PATH / 'es_WCSlanguage_db.txt').as_dict()
else:
    _languages = {}

_repeats = defaultdict(list)
_delays = defaultdict(list)
_attackspeed = {}
_norecoil = set()
_player_instances = PlayerDictionary()
_weapon_instances = WeaponDictionary()
_recoil_cvars_default = {}
_recoil_cvars_modified = {
    'weapon_accuracy_nospread': 1,
    'weapon_air_spread_scale': 0,
    'weapon_recoil_cooldown': 0,
    'weapon_recoil_decay1_exp': 99999,
    'weapon_recoil_decay2_exp': 99999,
    'weapon_recoil_decay2_lin': 99999,
    'weapon_recoil_decay_coefficient': 0,
    'weapon_recoil_scale': 0,
    'weapon_recoil_scale_motion_controller': 0,
    'weapon_recoil_suppression_factor': 0,
    'weapon_recoil_suppression_shots': 500,
    'weapon_recoil_variance': 0,
    'weapon_recoil_vel_decay': 0,
    'weapon_recoil_view_punch_extra': 0
}

_models = {2:[], 3:[]}

if GAME_NAME == 'cstrike':
    _models[2].extend(
        [
            't_arctic',
            't_guerilla',
            't_leet',
            't_phoenix'
        ]
    )
    _models[3].extend(
        [
            'ct_gign',
            'ct_gsg9',
            'ct_sas',
            'ct_urban'
        ]
    )

    _recoil_cvars_modified.clear()

    weapon_fire_post_properties = (
        'localdata.m_Local.m_vecPunchAngle',
        'localdata.m_Local.m_vecPunchAngleVel'
    )
elif GAME_NAME == 'csgo':
    _models[2].extend(
        [
            'tm_leet_varianta',
            'tm_leet_variantb',
            'tm_leet_variantc',
            'tm_leet_variantd',
            'tm_phoenix_varianta',
            'tm_phoenix_variantb',
            'tm_phoenix_variantc',
            'tm_phoenix_variantd'
        ]
    )
    _models[3].extend(
        [
            'ctm_gign_varianta',
            'ctm_gign_variantb',
            'ctm_gign_variantc',
            'ctm_gign_variantd',
            'ctm_gsg9_varianta',
            'ctm_gsg9_variantb',
            'ctm_gsg9_variantc',
            'ctm_gsg9_variantd'
        ]
    )

    for cvar in _recoil_cvars_modified:
        _recoil_cvars_default[cvar] = ConVar(cvar).default

    _weapon_fire_post_properties = (
        'localdata.m_Local.m_aimPunchAngle',
        'localdata.m_Local.m_aimPunchAngleVel',
        'localdata.m_Local.m_viewPunchAngle'
    )


# ============================================================================
# >> HELPER FUNCTIONS
# ============================================================================
def validate_userid_after_delay(callback, userid, operator, value, delay, validator=convert_userid_to_player):
    _delays[userid].remove(delay)

    callback(None, validator(userid), operator, value)


def _format_message(userid, name, args):
    if _strings is None:
        return tuple(), None

    text = _strings.get(name)

    if text is None:
        return tuple(), None

    if userid.isdigit():
        try:
            players = (Player.from_userid(int(userid)), )
        except ValueError:
            return tuple(), None
    else:
        players = convert_identifier_to_players(userid)

    if args:
        tokens = {}

        for i in range(0, len(args), 2):
            tokens[args[i]] = args[i + 1]

        for language, message in text.items():
            text[language] = Template(message).substitute(tokens)

    return players, text


# ============================================================================
# >> FUNCTIONS
# ============================================================================
def _remove_overlay(userid):
    try:
        player = Player.from_userid(userid)
    except ValueError:
        pass
    else:
        player.client_command('r_screenoverlay 0')


def _remove_drunk(userid):
    try:
        player = Player.from_userid(userid)
    except ValueError:
        pass
    else:
        player.default_fov = 90
        player.fov = 90


def _regeneration_repeat(userid, value, maxhealth, radius):
    try:
        player = Player.from_userid(userid)
    except ValueError:
        repeats = _repeats.pop(userid, [])

        for repeat in repeats:
            if repeat.status == RepeatStatus.RUNNING:
                repeat.stop()
    else:
        if player.team not in (2, 3):
            repeats = _repeats.pop(userid, [])

            for repeat in repeats:
                if repeat.status == RepeatStatus.RUNNING:
                    repeat.stop()

            return

        if player.health < maxhealth:
            player.health = min(player.health + value, maxhealth)

        if radius:
            origin = player.origin

            for target in PlayerIter(['alive', 't' if player.team == 2 else 'ct']):
                if not target == player:
                    if target.origin.get_distance(origin) <= radius:
                        if target.health < maxhealth:
                            target.health = min(target.health + value, maxhealth)


# ============================================================================
# >> COMMANDS
# ============================================================================
@TypedServerCommand(['wcs_setfx', 'freeze'])
def wcs_setfx_freeze_command(command_info, player:convert_userid_to_player, operator:valid_operators('='), value:int, time:float=0):
    if player is None:
        return

    if value:
        player.move_type = MoveType.NONE
    else:
        player.move_type = MoveType.WALK

    if time > 0:
        delay = Delay(time, validate_userid_after_delay, (wcs_setfx_freeze_command, player.userid, '=', not value))
        delay.args += (delay, )
        _delays[player.userid].append(delay)


@TypedServerCommand(['wcs_setfx', 'jetpack'])
def wcs_setfx_jetpack_command(command_info, player:convert_userid_to_player, operator:valid_operators('='), value:int, time:float=0):
    if player is None:
        return

    if value:
        player.move_type = MoveType.FLY
    else:
        player.move_type = MoveType.WALK

    if time > 0:
        delay = Delay(time, validate_userid_after_delay, (wcs_setfx_jetpack_command, player.userid, '=', not value))
        delay.args += (delay, )
        _delays[player.userid].append(delay)


@TypedServerCommand(['wcs_setfx', 'god'])
def wcs_setfx_god_command(command_info, player:convert_userid_to_player, operator:valid_operators('='), value:int, time:float=0):
    if player is None:
        return

    player.godmode = value

    if time > 0:
        delay = Delay(time, validate_userid_after_delay, (wcs_setfx_god_command, player.userid, '=', not value))
        delay.args += (delay, )
        _delays[player.userid].append(delay)


@TypedServerCommand(['wcs_setfx', 'noblock'])
def wcs_setfx_noblock_command(command_info, player:convert_userid_to_player, operator:valid_operators('='), value:int, time:float=0):
    if player is None:
        return

    player.noblock = value

    if time > 0:
        delay = Delay(time, validate_userid_after_delay, (wcs_setfx_noblock_command, player.userid, '=', not value))
        delay.args += (delay, )
        _delays[player.userid].append(delay)


@TypedServerCommand(['wcs_setfx', 'burn'])
def wcs_setfx_burn_command(command_info, player:convert_userid_to_player, operator:valid_operators('='), value:int, time:float=0):
    if player is None:
        return

    player.ignite_lifetime((time if time else 999) if value else 0)


@TypedServerCommand(['wcs_setfx', 'speed'])
def wcs_setfx_speed_command(command_info, player:convert_userid_to_player, operator:valid_operators(), value:float, time:float=0):
    if player is None:
        return

    if operator == '=':
        old_value = player.speed
        player.speed = value
        value = old_value - value
    elif operator == '+':
        player.speed += value
        value *= -1
    else:
        player.speed -= value

    if time > 0:
        delay = Delay(time, validate_userid_after_delay, (wcs_setfx_speed_command, player.userid, '+', value))
        delay.args += (delay, )
        _delays[player.userid].append(delay)


@TypedServerCommand(['wcs_setfx', 'invis'])
def wcs_setfx_invis_command(command_info, player:convert_userid_to_player, operator:valid_operators(), value:int, time:float=0):
    if player is None:
        return

    color = player.color

    if operator == '=':
        old_value = color.a
        player.color = color.with_alpha(value)
        value = old_value - value
    elif operator == '+':
        player.color = color.with_alpha(min(color.a + value, 255))
        value *= -1
    else:
        player.color = color.with_alpha(max(color.a - value, 0))

    if time > 0:
        delay = Delay(time, validate_userid_after_delay, (wcs_setfx_invis_command, player.userid, '+', value))
        delay.args += (delay, )
        _delays[player.userid].append(delay)


@TypedServerCommand(['wcs_setfx', 'invisp'])
def wcs_setfx_invisp_command(command_info, player:convert_userid_to_player, operator:valid_operators(), value:float, time:float=0):
    pass  # TODO


@TypedServerCommand(['wcs_setfx', 'health'])
def wcs_setfx_health_command(command_info, player:convert_userid_to_player, operator:valid_operators(), value:int, time:float=0):
    if player is None:
        return

    if operator == '=':
        old_value = player.health
        player.health = value
        value = old_value - value
    elif operator == '+':
        player.health += value
        value *= -1
    else:
        # TODO: Minimum 1 health?
        player.health -= value

    if time > 0:
        delay = Delay(time, validate_userid_after_delay, (wcs_setfx_health_command, player.userid, '+', value))
        delay.args += (delay, )
        _delays[player.userid].append(delay)


@TypedServerCommand(['wcs_setfx', 'armor'])
def wcs_setfx_armor_command(command_info, player:convert_userid_to_player, operator:valid_operators(), value:int, time:float=0):
    if player is None:
        return

    if operator == '=':
        old_value = player.armor
        player.armor = value
        value = old_value - value
    elif operator == '+':
        player.armor += value
        value *= -1
    else:
        player.armor = max(player.armor - value, 0)

    if time > 0:
        delay = Delay(time, validate_userid_after_delay, (wcs_setfx_armor_command, player.userid, '+', value))
        delay.args += (delay, )
        _delays[player.userid].append(delay)


@TypedServerCommand(['wcs_setfx', 'cash'])
def wcs_setfx_cash_command(command_info, player:convert_userid_to_player, operator:valid_operators(), value:int, time:float=0):
    if player is None:
        return

    if operator == '=':
        old_value = player.cash
        player.cash = value
        value = old_value - value
    elif operator == '+':
        player.cash += value
        value *= -1
    else:
        player.cash = max(player.cash - value, 0)

    if time > 0:
        delay = Delay(time, validate_userid_after_delay, (wcs_setfx_cash_command, player.userid, '+', value))
        delay.args += (delay, )
        _delays[player.userid].append(delay)


@TypedServerCommand(['wcs_setfx', 'gravity'])
def wcs_setfx_gravity_command(command_info, player:convert_userid_to_player, operator:valid_operators(), value:float, time:float=0):
    if player is None:
        return

    if operator == '=':
        old_value = player.gravity
        player.gravity = value
        value = old_value - value
    elif operator == '+':
        player.gravity += value
        value *= -1
    else:
        player.gravity = max(player.gravity - value, 0)

    if time > 0:
        delay = Delay(time, validate_userid_after_delay, (wcs_setfx_gravity_command, player.userid, '+', value))
        delay.args += (delay, )
        _delays[player.userid].append(delay)


@TypedServerCommand(['wcs_setfx', 'ulti_immunity'])
def wcs_setfx_ulti_immunity_command(command_info, wcsplayer:convert_userid_to_wcsplayer, operator:valid_operators(), value:int, time:float=0):
    if wcsplayer is None:
        return

    if operator == '=':
        old_value = wcsplayer.data.get('ulti_immunity', 0)
        wcsplayer.data['ulti_immunity'] = value
        value = old_value - value
    elif operator == '+':
        wcsplayer.data['ulti_immunity'] = wcsplayer.data.get('ulti_immunity', 0)
        value *= -1
    else:
        old_value = wcsplayer.data.get('ulti_immunity', 0)

        # This is here to prevent them from gaining if there was a time set
        if not old_value:
            return

        wcsplayer.data['ulti_immunity'] = max(old_value - value, 0)

    if time > 0:
        delay = Delay(time, validate_userid_after_delay, (wcs_setfx_ulti_immunity_command, wcsplayer.userid, '+', value), {'validator':convert_userid_to_wcsplayer})
        delay.args += (delay, )
        _delays[wcsplayer.userid].append(delay)


@TypedServerCommand(['wcs_setfx', 'disguiser'])
def wcs_setfx_disguiser_command(command_info, player:convert_userid_to_player, operator:valid_operators('='), value:int, time:float=0):
    if player is None:
        return

    if value:
        models = _models.get(5 - player.team)
    else:
        models = _models.get(player.team)

    if not models:
        return

    player.model = Model('models/player/' + choice(models) + '.mdl')

    if time:
        delay = Delay(time, validate_userid_after_delay, (wcs_setfx_disguiser_command, player.userid, '=', not value), {'validator':convert_userid_to_player})
        delay.args += (delay, )
        _delays[player.userid].append(delay)


@TypedServerCommand(['wcs_setfx', 'disguise'])
def wcs_setfx_disguise_command(command_info, player:convert_userid_to_player, operator:valid_operators('='), value:int, time:float=0):
    wcs_setfx_disguiser_command(command_info, player, operator, value, time)


@TypedServerCommand(['wcs_setfx', 'longjump'])
def wcs_setfx_longjump_command(command_info, wcsplayer:convert_userid_to_wcsplayer, operator:valid_operators(), value:float, time:float=0):
    if wcsplayer is None:
        return

    if operator == '=':
        old_value = wcsplayer.data.get('longjump', 0)
        wcsplayer.data['longjump'] = value
        value = old_value - value
    elif operator == '+':
        wcsplayer.data['longjump'] = wcsplayer.data.get('longjump', 0)
        value *= -1
    else:
        old_value = wcsplayer.data.get('longjump', 0)

        # This is here to prevent them from gaining if there was a time set
        if not old_value:
            return

        wcsplayer.data['longjump'] = max(old_value - value, 0)

    if time > 0:
        delay = Delay(time, validate_userid_after_delay, (wcs_setfx_longjump_command, wcsplayer.userid, '+', value), {'validator':convert_userid_to_wcsplayer})
        delay.args += (delay, )
        _delays[wcsplayer.userid].append(delay)


@TypedServerCommand(['wcs_setfx', '1stclip'])
def wcs_setfx_1stclip_command(command_info, player:convert_userid_to_player, operator:valid_operators(), value:int, time:float=0):
    if player is None:
        return

    weapon = player.get_weapon(is_filters='primary')

    if weapon is None:
        return

    if operator == '=':
        old_value = weapon.clip
        weapon.clip = value
        value = old_value - value
    elif operator == '+':
        weapon.clip += value
        value *= -1
    else:
        old_value = weapon.clip

        if not old_value:
            return

        weapon.clip = max(old_value - value, 0)

    if time > 0:
        delay = Delay(time, validate_userid_after_delay, (wcs_setfx_1stclip_command, player.userid, '+', value), {'validator':convert_userid_to_player})
        delay.args += (delay, )
        _delays[player.userid].append(delay)


@TypedServerCommand(['wcs_setfx', '2ndclip'])
def wcs_setfx_2ndclip_command(command_info, player:convert_userid_to_player, operator:valid_operators(), value:int, time:float=0):
    if player is None:
        return

    weapon = player.get_weapon(is_filters='secondary')

    if weapon is None:
        return

    if operator == '=':
        old_value = weapon.clip
        weapon.clip = value
        value = old_value - value
    elif operator == '+':
        weapon.clip += value
        value *= -1
    else:
        old_value = weapon.clip

        if not old_value:
            return

        weapon.clip = max(old_value - value, 0)

    if time > 0:
        delay = Delay(time, validate_userid_after_delay, (wcs_setfx_2ndclip_command, player.userid, '+', value), {'validator':convert_userid_to_player})
        delay.args += (delay, )
        _delays[player.userid].append(delay)


@TypedServerCommand(['wcs_setfx', '1stammo'])
def wcs_setfx_1stammo_command(command_info, player:convert_userid_to_player, operator:valid_operators(), value:int, time:float=0):
    if player is None:
        return

    weapon = player.get_weapon(is_filters='secondary')

    if weapon is None:
        return

    if operator == '=':
        old_value = weapon.ammo
        weapon.ammo = value
        value = old_value - value
    elif operator == '+':
        weapon.ammo += value
        value *= -1
    else:
        old_value = weapon.ammo

        if not old_value:
            return

        weapon.ammo = max(old_value - value, 0)

    if time > 0:
        delay = Delay(time, validate_userid_after_delay, (wcs_setfx_1stammo_command, player.userid, '+', value), {'validator':convert_userid_to_player})
        delay.args += (delay, )
        _delays[player.userid].append(delay)


@TypedServerCommand(['wcs_setfx', '2ndammo'])
def wcs_setfx_2ndammo_command(command_info, player:convert_userid_to_player, operator:valid_operators(), value:int, time:float=0):
    if player is None:
        return

    weapon = player.get_weapon(is_filters='secondary')

    if weapon is None:
        return

    if operator == '=':
        old_value = weapon.ammo
        weapon.ammo = value
        value = old_value - value
    elif operator == '+':
        weapon.ammo += value
        value *= -1
    else:
        old_value = weapon.ammo

        if not old_value:
            return

        weapon.ammo = max(old_value - value, 0)

    if time > 0:
        delay = Delay(time, validate_userid_after_delay, (wcs_setfx_2ndammo_command, player.userid, '+', value), {'validator':convert_userid_to_player})
        delay.args += (delay, )
        _delays[player.userid].append(delay)


@TypedServerCommand(['wcs_setfx', 'flicker'])
def wcs_setfx_flicker_command(command_info, player:convert_userid_to_player, operator:valid_operators(), value:int, time:float=0):
    warn('"wcs_setfx flicker" will be removed in the future. Use "wcs_getplayerindex" together with "es_entitysetvalue <index> renderfx 13/0" instead.', PendingDeprecationWarning)

    if player is None:
        return

    player.set_key_value_int('renderfx', 13 if value else 0)

    if time > 0:
        delay = Delay(time, validate_userid_after_delay, (wcs_setfx_flicker_command, player.userid, '=', not value), {'validator':convert_userid_to_player})
        delay.args += (delay, )
        _delays[player.userid].append(delay)


@TypedServerCommand(['wcs_setfx', 'attackspeed'])
def wcs_setfx_attackspeed_command(command_info, player:convert_userid_to_player, operator:valid_operators(), value:float, time:float=0):
    if player is None:
        return

    userid = player.userid

    if operator == '=':
        old_value = _attackspeed.get(userid, 1)
        _attackspeed[userid] = value
        value = old_value - value
    elif operator == '+':
        _attackspeed[userid] = _attackspeed.get(userid, 1) + value
        value *= -1
    else:
        old_value = _attackspeed.get(userid, 1)

        _attackspeed[userid] = max(old_value - value, 0)

    if _attackspeed[userid] in (0, 1):
        del _attackspeed[userid]

    cur_time = global_vars.current_time

    for index in player.weapon_indexes():
        _weapon_instances[index].set_network_property_float('LocalActiveWeaponData.m_flNextPrimaryAttack', cur_time)

    if time > 0:
        delay = Delay(time, validate_userid_after_delay, (wcs_setfx_attackspeed_command, userid, '+', value), {'validator':convert_userid_to_player})
        delay.args += (delay, )
        _delays[userid].append(delay)


@TypedServerCommand(['wcs_setfx', 'norecoil'])
def wcs_setfx_norecoil_command(command_info, player:convert_userid_to_player, operator:valid_operators('='), value:int, time:float=0):
    if player is None:
        return

    userid = player.userid

    if value:
        _norecoil.add(userid)

        for cvar in _recoil_cvars_modified:
            player.send_convar_value(cvar, _recoil_cvars_modified[cvar])
    else:
        _norecoil.discard(userid)

        for cvar in _recoil_cvars_modified:
            player.send_convar_value(cvar, _recoil_cvars_default[cvar])

    if time > 0:
        delay = Delay(time, validate_userid_after_delay, (wcs_setfx_norecoil_command, userid, '=', not value), {'validator':convert_userid_to_player})
        delay.args += (delay, )
        _delays[userid].append(delay)


@TypedServerCommand('wcs_removefx')
def wcs_removefx_freeze_command(command_info, *args):
    raise NotImplementedError(args)


@TypedServerCommand(['wcsgroup', 'get'])
def wcsgroup_get_command(command_info, key:str, var:ConVar, userid:valid_userid_and_team):
    if userid is None:
        var.set_int(0)
        return

    if isinstance(userid, str):
        value = team_data[{'T':2, 'CT':3}[userid]].get(key, '0')
    else:
        wcsplayer = WCSPlayer.from_userid(userid)

        value = wcsplayer.data.get(key, '0')

    var.set_string(str(value))


@TypedServerCommand(['wcsgroup', 'set'])
def wcsgroup_set_command(command_info, key:str, userid:valid_userid_and_team, value:any_value):
    if userid is None:
        return

    if isinstance(userid, str):
        team_data[{'T':2, 'CT':3}[userid]][key] = value
    else:
        wcsplayer = WCSPlayer.from_userid(userid)

        wcsplayer.data[key] = value


@TypedServerCommand(['wcs', 'damage'])
def wcs_sub_damaget_command(command_info, wcsplayer:convert_userid_to_wcsplayer, damage:int, attacker:int=None, armor:deprecated=None, weapon:deprecated=None, solo:deprecated=None):
    if wcsplayer is None:
        return

    wcsplayer.take_damage(damage, attacker)


@TypedServerCommand(['wcs', 'spawn'])
def wcs_sub_spawn_command(command_info, player:convert_userid_to_player, force:int=0):
    if player is None:
        return

    player.spawn(force)


@TypedServerCommand(['wcs', 'strip'])
def wcs_sub_strip_command(command_info, player:convert_userid_to_player):
    if player is None:
        return

    entity = Entity.create('player_weaponstrip')
    entity.call_input('Strip', activator=player)
    entity.remove()


@TypedServerCommand(['wcs', 'drop'])
def wcs_sub_drop_command(command_info, player:convert_userid_to_player, slot:str):
    if player is None:
        return

    if slot.isdigit():
        slot = int(slot)

        if slot not in range(1, 6):
            raise InvalidArgumentValue(f'"{slot}" is an invalid value for "slot:str".')

        if slot == 1:
            slot = 'primary'
        elif slot == 2:
            slot = 'secondary'
        elif slot == 3:
            slot = 'melee'
        elif slot == 4:
            slot = 'grenade'
        else:
            slot = 'objective'

        for weapon in player.weapons(is_filters=slot):
            player.drop_weapon(weapon)

        return

    try:
        name = weapon_manager[slot].name
    except KeyError:
        raise InvalidArgumentValue(f'"{slot}" is an invalid value for "slot:str".')

    for weapon in player.weapons():
        if weapon.classname == name:
            player.drop_weapon(weapon)
            break


@TypedServerCommand(['wcs', 'push'])
def wcs_sub_push_command(command_info, player:convert_userid_to_player, x:float, y:float=0, z:float=0):
    if player is None:
        return

    vector = Vector(x, y, z)

    player.base_velocity = vector


@TypedServerCommand(['wcs', 'pushto'])
def wcs_sub_pushto_command(command_info, player:convert_userid_to_player, vector:convert_to_vector, force:float):
    if player is None:
        return

    player.teleport(velocity=vector - player.origin)


@TypedServerCommand(['wcs', 'gravity'])
def wcs_sub_gravity_command(command_info, player:convert_userid_to_player, value:float):
    if player is None:
        return

    player.gravity = value


@TypedServerCommand(['wcs', 'removeweapon'])
def wcs_sub_removeweapon_command(command_info, player:convert_userid_to_player, slot:str):
    if player is None:
        return

    if slot.isdigit():
        slot = int(slot)

        if slot not in range(1, 6):
            raise InvalidArgumentValue(f'"{slot}" is an invalid value for "slot:str".')

        if slot == 1:
            slot = 'primary'
        elif slot == 2:
            slot = 'secondary'
        elif slot == 3:
            slot = 'melee'
        elif slot == 4:
            slot = 'grenade'
        else:
            slot = 'objective'

        for weapon in player.weapons(is_filters=slot):
            player.drop_weapon(weapon)

            weapon.remove()

        return

    try:
        name = weapon_manager[slot].name
    except KeyError:
        raise InvalidArgumentValue(f'"{slot}" is an invalid value for "slot:str".')

    for weapon in player.weapons():
        if weapon.classname == name:
            player.drop_weapon(weapon)

            weapon.remove()
            break


@TypedServerCommand(['wcs', 'getviewplayer'])
def wcs_sub_getviewplayer_command(command_info, player:convert_userid_to_player, var:ConVar):
    if player is None:
        var.set_int(-1)
        return

    target = player.view_player

    if target is None:
        var.set_int(-1)
        return

    var.set_int(target.userid)


@TypedServerCommand(['wcs', 'getviewentity'])
def wcs_sub_getviewentity_command(command_info, player:convert_userid_to_player, var:ConVar):
    if player is None:
        var.set_int(-1)
        return

    target = player.view_entity

    if target is None:
        var.set_int(-1)
        return

    var.set_int(target.entity)


@TypedServerCommand(['wcs', 'keyhint'])
def wcs_sub_keyhint_command(command_info, player:convert_userid_to_player, text:str):
    if player is None:
        return

    KeyHintText(text).send(player.index)


@TypedServerCommand(['wcs', 'give'])
def wcs_sub_give_command(command_info, player:convert_userid_to_player, entity:str):
    warn('"wcs give" will be removed in the future. Use "es_give" instead.', PendingDeprecationWarning)

    if player is None:
        return

    # entity = Entity.create(entity)
    # entity.origin = player.origin
    # entity.spawn()


@TypedServerCommand(['wcs', 'fire'])
def wcs_sub_fire_command(command_info, player:convert_userid_to_player, time:float):
    warn('"wcs fire" will be removed in the future. Use "wcs_setfx burn" instead.', PendingDeprecationWarning)

    if player is None:
        return

    player.ignite_lifetime(time if time else 999)


@TypedServerCommand(['wcs', 'extinguish'])
def wcs_sub_extinguish_command(command_info, player:convert_userid_to_player):
    warn('"wcs extinguish" will be removed in the future. Use "wcs_setfx burn" instead.', PendingDeprecationWarning)

    if player is None:
        return

    player.ignite_lifetime(0.0)


@TypedServerCommand(['wcs', 'drug'])
def wcs_sub_drug_command(command_info, player:convert_userid_to_player, duration:float=0):
    warn('"wcs drug" will be removed in the future. Use "es_cexec" with "r_screenoverlay" and "es_delayed" instead.', PendingDeprecationWarning)

    if player is None:
        return

    player.client_command('r_screenoverlay effects/tp_eyefx/tp_eyefx')

    if duration:
        player.delay(duration, _remove_overlay, (player.userid, ))


@TypedServerCommand(['wcs', 'drunk'])
def wcs_sub_drunk_command(command_info, player:convert_userid_to_player, duration:float=0, value:int=155):
    warn('"wcs drunk" will be removed in the future. Use "es_setplayerprop" with "CBasePlayer.m_iDefaultFOV", "CBasePlayer.m_iFOV" and "es_delayed" instead.', PendingDeprecationWarning)

    if player is None:
        return

    player.default_fov = value
    player.fov = value

    if time:
        player.delay(duration, _remove_drunk, (player.userid, ))


# @TypedServerCommand(['wcs', 'poison'])
# def wcs_sub_poison_command(command_info, player:convert_userid_to_player):
#     if player is None:
#         return


# @TypedServerCommand(['wcs', 'timed_damage'])
# def wcs_sub_timed_damage_command(command_info, player:convert_userid_to_player):
#     if player is None:
#         return


@TypedServerCommand(['wcs', 'changeteam'])
def wcs_sub_changeteam_command(command_info, player:convert_userid_to_player, team:int):
    if player is None:
        return

    player.set_team(team)


@TypedServerCommand(['wcsx', 'get'])
def wcsx_get_command(command_info, key:str, var:ConVar, userid:valid_userid):
    if userid is None:
        var.set_int(-1)
        return

    player = getPlayer(userid)

    if not hasattr(player, key):
        var.set_int(-1)
        return

    value = getattr(player, key)

    if callable(value):
        if isinstance(value, _PLPlayer.ReturnValue):
            var.set_string(str(value))
            return
        else:
            value = value()

    if key not in ('weapon', 'primary', 'secondary'):
        if hasattr(value, '__iter__'):
            if hasattr(value[0], '__iter__'):
                if len(value[0]) == 1:
                    value = value[0][0]
                else:
                    value = ','.join([str(x) for x in value[0]])
            else:
                value = value[0]

    var.set_string(str(value))


@TypedServerCommand(['wcsx', 'set'])
def wcsx_set_command(command_info, key:str, userid:valid_userid, *value:str):
    if userid is None:
        return

    player = getPlayer(userid)

    if not hasattr(player, key):
        return

    if not value:
        return

    if hasattr(value, '__iter__'):
        if hasattr(value[0], '__iter__'):
            if len(value[0]) == 1:
                value = value[0][0]
            else:
                value = ','.join([str(x) for x in value[0]])
        else:
            value = value[0]

    if hasattr(value, '__iter__') and not key == 'location':
        value = value[0]

    if key == 'location' and not hasattr(value, '__iter__'):
        value = value.split(',')

    method = getattr(player, key)

    if callable(method):
        method(value)
    else:
        setattr(player, key, value)


@TypedServerCommand(['wcsx', 'math'])
def wcsx_math_command(command_info, key:str, userid:valid_userid, operator:valid_operators(), value:any_value):
    if userid is None:
        return

    player = getPlayer(userid)

    if not hasattr(player, key):
        return

    if operator == '+':
        value = getattr(player, key) + value
    elif operator == '-':
        value = getattr(player, key) - value

    setattr(player, key, value)


@TypedServerCommand(['wcsx', 'call'])
def wcsx_call_command(command_info, key:str, userid:valid_userid):
    if userid is None:
        return

    player = getPlayer(userid)

    if not hasattr(player, key):
        return

    method = getattr(player, key)

    if not callable(method):
        return

    method()


@TypedServerCommand(['wcsx', 'create'])
def wcsx_create_command(command_info, var:ConVar, *args:str):
    var.set_string(','.join(args))


@TypedServerCommand(['wcsx', 'split'])
def wcsx_split_command(command_info, value:str, *var:ConVar):
    for i, x in enumerate(value.split(',')):
        var[i].set_string(x)


@TypedServerCommand('wcs_get_skill_level')
def wcs_get_skill_level_command(command_info, wcsplayer:convert_userid_to_wcsplayer, var:ConVar, index:int):
    if wcsplayer is None:
        var.set_int(0)
        return

    active_race = wcsplayer.active_race

    skills = [*active_race.settings.config['skills']]

    if index >= len(skills):
        var.set_int(0)
        return

    var.set_int(active_race.skills[skills[index]].level)


@TypedServerCommand(['wcs_foreach', 'player'])
def wcs_foreach_command(command_info, var:str, players:convert_identifier_to_players, command:str):
    for player in players:
        for cmd in [f'es_xset {var} {player.userid}'] + command.split(';'):
            execute_server_command(*split(cmd))


@TypedServerCommand('wcs_nearcoord')
def wcs_nearcoord_command(command_info, var:str, players:convert_identifier_to_players, x:float, y:float, z:float, distance:float, command:str):
    vector = Vector(x, y, z)

    for player in players:
        if vector.get_distance(player.origin) <= distance:
            for cmd in [f'es_xset {var} {player.userid}'] + command.split(';'):
                execute_server_command(*split(cmd))


@TypedServerCommand('wcs_color')
def wcs_color_command(command_info, player:convert_userid_to_player, red:int, green:int, blue:int, alpha:int=255, weapons:int=0):
    if player is None:
        return

    color = Color(red, green, blue, alpha)

    player.color = color

    if weapons:
        for weapon in player.weapons():
            weapon.color = color


@TypedServerCommand('wcs_changerace')
def wcs_changerace_command(command_info, wcsplayer:convert_userid_to_wcsplayer, *name:str):
    if wcsplayer is None:
        return

    name = ' '.join(name)

    if name not in race_manager:
        for settings in race_manager.values():
            if settings.strings['name'].get_string('en') == name:
                name = settings.name
                break
        else:
            return

    if wcsplayer.current_race == name:
        return

    wcsplayer.current_race = name


@TypedServerCommand('wcs_givexp')
def wcs_givexp_command(command_info, wcsplayer:convert_userid_to_wcsplayer, value:int, reason:deprecated=None, forced:deprecated=None):
    if wcsplayer is None:
        return

    wcsplayer.xp += value


@TypedServerCommand('wcs_givelevel')
def wcs_givelevel_command(command_info, wcsplayer:convert_userid_to_wcsplayer, value:int, reason:deprecated=None, forced:deprecated=None):
    if wcsplayer is None:
        return

    wcsplayer.level += value


@TypedServerCommand('wcs_xalias')
def wcs_xalias_command(command_info, alias:str, command:str=None):
    if command is None:
        for cmd in _aliases[alias].split(';'):
            execute_server_command(*split(cmd))
    else:
        _aliases[alias] = command


@TypedServerCommand('wcs_dalias')
def wcs_dalias_command(command_info, alias:str, *args:str):
    for i, value in enumerate(args, 1):
        ConVar(f'wcs_tmp{i}').set_string(value)

    for cmd in _aliases[alias].split(';'):
        execute_server_command(*split(cmd))


@TypedServerCommand('wcs_decimal')
def wcs_decimal_command(command_info, var:ConVar, value:float):
    var.set_int(int(round(value)))


@TypedServerCommand('wcs_xtell')
def wcs_xtell_command(command_info, userid:str, name:str, *args:str):
    players, message = _format_message(userid, name, args)

    for player in players:
        SayText2(message[message.get(player.language, 'en')]).send(player.index)


@TypedServerCommand('wcs_xcentertell')
def wcs_xcentertell_command(command_info, userid:str, name:str, *args:str):
    players, message = _format_message(userid, name, args)

    for player in players:
        HudMsg(message[message.get(player.language, 'en')], y=0.2).send(player.index)


@TypedServerCommand('wcs_centermsg')
def wcs_centermsg_command(command_info, *message:str):
    HudMsg(' '.join(message), y=0.2).send()


@TypedServerCommand('wcs_centertell')
def wcs_centertell_command(command_info, player:convert_userid_to_player, *message:str):
    if player is None:
        return

    HudMsg(' '.join(message), y=0.2).send(player.index)


@TypedServerCommand('wcs_dealdamage')
def wcs_dealdamage_command(command_info, wcstarget:convert_userid_to_wcsplayer, attacker:valid_userid, damage:int, weapon:str=None):
    if wcstarget is None:
        return

    if wcstarget.player.dead:
        return

    if attacker is None:
        attacker = 0
    else:
        attacker = index_from_userid(attacker)

    wcstarget.take_damage(damage, attacker=attacker, weapon=weapon)


@TypedServerCommand('wcs_getcolors')
def wcs_getcolors_command(command_info, player:convert_userid_to_player, red:ConVar, green:ConVar, blue:ConVar, alpha:ConVar):
    if player is None:
        return

    color = player.color

    red.set_int(color.r)
    green.set_int(color.g)
    blue.set_int(color.b)
    alpha.set_int(color.a)


@TypedServerCommand('wcs_getinfo')
def wcs_getinfo_command(command_info, wcsplayer:convert_userid_to_wcsplayer, var:ConVar, attribute:str, key:str):
    if wcsplayer is None:
        var.set_int(-1)
        return

    if not wcsplayer.ready:
        var.set_int(-1)
        return

    if key == 'race':
        if attribute == 'shortname':
            var.set_string(wcsplayer.active_race.name)
        elif attribute == 'name':
            var.set_string(wcsplayer.active_race.settings.strings['name'])
        elif attribute == 'level':
            var.set_int(wcsplayer.active_race.level)
        elif attribute == 'xp':
            var.set_int(wcsplayer.active_race.xp)
        elif attribute == 'unused':
            var.set_int(wcsplayer.active_race.unused)
    elif key == 'player':
        if attribute == 'shortcurrace':
            var.set_string(wcsplayer.active_race.name)
        elif attribute == 'currace':
            var.set_string(wcsplayer.active_race.settings.strings['name'])
        elif attribute == 'totallevel':
            var.set_int(wcsplayer.total_level)


@TypedServerCommand('wcs_restrict')
def wcs_restrict_command(command_info, player:convert_userid_to_player, weapons:split_str(), reverse:int=0):
    if player is None:
        return

    if weapons[0] == 'all':
        _restrictions.add_player_restrictions(player, *_all_weapons)
        return

    if 'only' in weapons:
        weapons.remove('only')

        weapons = _all_weapons.difference(weapons)

        _restrictions.player_restrictions[player.userid].clear()

    _restrictions.add_player_restrictions(player, *weapons)


@TypedServerCommand('wcs_unrestrict')
def wcs_unrestrict_command(command_info, player:convert_userid_to_player, weapons:split_str()):
    if player is None:
        return

    if weapons[0] == 'all':
        _restrictions.remove_player_restrictions(player, *_all_weapons)
        return

    _restrictions.remove_player_restrictions(player, *weapons)


@TypedServerCommand('wcs_getlanguage')
def wcs_getlanguage_command(command_info, var:ConVar, id_:str, language:str='en'):
    var.set_string(_languages.get(language, {}).get(id_, 'n/a'))


@TypedServerCommand('wcs_randplayer')
def wcs_randplayer_command(command_info, var:ConVar, players:convert_identifier_to_players):
    players = list(players)

    if players:
        var.set_int(choice(players).userid)
    else:
        var.set_int(0)


@TypedServerCommand('wcs_get_cooldown')
def wcs_get_cooldown_command(command_info, wcsplayer:convert_userid_to_wcsplayer, var:ConVar):
    if wcsplayer is None:
        var.set_int(-1)
        return

    if not wcsplayer.ready:
        var.set_int(-1)
        return

    active_race = wcsplayer.active_race

    for skill in active_race.skills.values():
        if 'player_ultimate' in skill.config['event']:
            var.set_float(max(skill.cooldown - time(), 0))
            break
    else:
        var.set_int(-1)


@TypedServerCommand('wcs_getcooldown')
def wcs_getcooldown_command(command_info, wcsplayer:convert_userid_to_wcsplayer, var:ConVar):
    wcs_get_cooldown_command(command_info, wcsplayer, var)


@TypedServerCommand('wcs_set_cooldown')
def wcs_set_cooldown_command(command_info, wcsplayer:convert_userid_to_wcsplayer, value:float):
    if wcsplayer is None:
        return

    if not wcsplayer.ready:
        return

    active_race = wcsplayer.active_race

    for skill in active_race.skills.values():
        if 'player_ultimate' in skill.config['event']:
            skill.reset_cooldown(value)
            break


@TypedServerCommand('wcs_setcooldown')
def wcs_setcooldown_command(command_info, wcsplayer:convert_userid_to_wcsplayer, value:float):
    wcs_set_cooldown_command(command_info, wcsplayer, value)


@TypedServerCommand('wcs_cancelulti')
def wcs_cancelulti_command(command_info, wcsplayer:convert_userid_to_wcsplayer):
    wcs_set_cooldown_command(command_info, wcsplayer, 0)


@TypedServerCommand('wcs_get_ability_cooldown')
def wcs_get_ability_cooldown_command(command_info, wcsplayer:convert_userid_to_wcsplayer, var:ConVar, ability:int=None):
    if wcsplayer is None:
        var.set_int(-1)
        return

    if not wcsplayer.ready:
        var.set_int(-1)
        return

    active_race = wcsplayer.active_race

    if ability is None:
        for skill in active_race.skills.values():
            if 'player_ability' in skill.config['event']:
                var.set_float(max(skill.cooldown - time(), 0))
                break
        else:
            var.set_int(-1)
    else:
        i = 1

        for skill_name in active_race.settings.config['skills']:
            skill = active_race.skills[skill_name]

            if 'player_ability_on' in skill.config['event']:
                if ability == i:
                    var.set_float(max(skill.cooldown - time(), 0))
                    break

                i += 1


@TypedServerCommand('wcs_set_ability_cooldown')
def wcs_set_ability_cooldown_command(command_info, wcsplayer:convert_userid_to_wcsplayer, value:float, ability:int=None):
    if wcsplayer is None:
        return

    if not wcsplayer.ready:
        return

    active_race = wcsplayer.active_race

    if ability is None:
        for skill in active_race.skills.values():
            if 'player_ability' in skill.config['event']:
                skill.reset_cooldown(value)
                break
    else:
        i = 1

        for skill_name in active_race.settings.config['skills']:
            skill = active_race.skills[skill_name]

            if 'player_ability_on' in skill.config['event']:
                if ability == i:
                    skill.reset_cooldown(value)
                    break

                i += 1


@TypedServerCommand('wcs_cancel_ability')
def wcs_cancel_ability_command(command_info, wcsplayer:convert_userid_to_wcsplayer, ability:int=None):
    wcs_set_ability_cooldown_command(command_info, wcsplayer, 0, ability)


@TypedServerCommand('wcs_getviewcoords')
def wcs_getviewcoords_command(command_info, player:convert_userid_to_player, x:ConVar, y:ConVar, z:ConVar):
    if player is None:
        x.set_int(0)
        y.set_int(0)
        z.set_int(0)
        return

    view_coordinates = player.view_coordinates

    x.set_float(view_coordinates[0])
    y.set_float(view_coordinates[1])
    z.set_float(view_coordinates[2])


@TypedServerCommand('wcs_getdistance')
def wcs_getdistance_command(command_info, var:ConVar, x:float, y:float, z:float, x2:float, y2:float, z2:float):
    vector = Vector(x, y, z)
    vector2 = Vector(x2, y2, z2)

    var.set_float(vector.get_distance(vector2))


@TypedServerCommand('wcs_pushto')
def wcs_pushto_command(command_info, *args):
    if len(args) == 5:
        execute_server_command('_wcs_pushto', args[0], ','.join(args[1:3]), args[4])
    else:
        execute_server_command('_wcs_pushto', *args)


@TypedServerCommand('_wcs_pushto')
def _wcs_pushto_command(command_info, player:convert_userid_to_player, vector:convert_to_vector, force:float):
    if player is None:
        return

    position = player.origin
    vector -= position
    vector *= force

    player.base_velocity = vector


@TypedServerCommand('wcs_pushed')
def wcs_pushed_command(command_info, player:convert_userid_to_player, x:float, y:float, z:float):
    if player is None:
        return

    vector = Vector(x, y, z)

    player.base_velocity = vector


@TypedServerCommand('wcs_explosion')
def wcs_explosion_command(command_info, player:convert_userid_to_player, magnitude:int, radius:int, deal_damage:int=1):
    if player is None:
        return

    entity = Entity.create('env_explosion')
    entity.set_property_int('m_iMagnitude', magnitude)
    entity.set_property_int('m_iRadiusOverride', radius)

    entity.spawn_flags = 8 if deal_damage else 1
    entity.owner_handle = player.inthandle
    entity.origin = player.origin

    entity.spawn()

    entity.call_input('Explode')


@TypedServerCommand('wcs_getrandomrace')
def wcs_getrandomrace_command(command_info, wcsplayer:convert_userid_to_wcsplayer, var:ConVar):
    if wcsplayer is None:
        var.set_int(0)
        return

    available_races = list(wcsplayer.available_races)

    if available_races:
        var.set_string(choice(available_races))
    else:
        var.set_int(0)


@TypedServerCommand('wcs_getwallbetween')
def wcs_getwallbetween_command(command_info, var:ConVar, player:convert_userid_to_player, target:convert_userid_to_player):
    if player is None or target is None:
        var.set_int(-1)
        return

    vector = player.origin
    vector2 = target.origin

    trace = GameTrace()
    ray = Ray(vector, vector2)

    engine_trace.trace_ray(ray, ContentMasks.ALL, None, trace)

    var.set_int(trace.did_hit_world())


@TypedServerCommand('wcs_getviewentity')
def wcs_getviewentity_command(command_info, player:convert_userid_to_player, var:ConVar):
    if player is None:
        var.set_int(-1)
        return

    target = player.view_entity

    if target is None:
        var.set_int(-1)
        return

    var.set_int(target.index)


@TypedServerCommand('wcs_getviewplayer')
def wcs_getviewplayer_command(command_info, player:convert_userid_to_player, var:ConVar):
    if player is None:
        var.set_int(-1)
        return

    target = player.view_player

    if target is None:
        var.set_int(-1)
        return

    var.set_int(target.userid)


@TypedServerCommand('wcs_removeweapon')
def wcs_removeweapon_command(command_info, player:convert_userid_to_player, slot:str):
    if player is None:
        return

    if slot.isdigit():
        slot = int(slot)

        if slot not in range(1, 6):
            raise InvalidArgumentValue(f'"{slot}" is an invalid value for "slot:str".')

        if slot == 1:
            slot = 'primary'
        elif slot == 2:
            slot = 'secondary'
        elif slot == 3:
            slot = 'melee'
        elif slot == 4:
            slot = 'grenade'
        else:
            slot = 'objective'

        for weapon in player.weapons(is_filters=slot):
            player.drop_weapon(weapon)

            weapon.remove()

        return

    try:
        name = weapon_manager[slot].name
    except KeyError:
        raise InvalidArgumentValue(f'"{slot}" is an invalid value for "slot:str".')

    for weapon in player.weapons():
        if weapon.classname == name:
            player.drop_weapon(weapon)

            weapon.remove()
            break


@TypedServerCommand('wcs_drop')
def wcs_drop_command(command_info, player:convert_userid_to_player, slot:str):
    if player is None:
        return

    if slot.isdigit():
        slot = int(slot)

        if slot not in range(1, 6):
            raise InvalidArgumentValue(f'"{slot}" is an invalid value for "slot:str".')

        if slot == 1:
            slot = 'primary'
        elif slot == 2:
            slot = 'secondary'
        elif slot == 3:
            slot = 'melee'
        elif slot == 4:
            slot = 'grenade'
        else:
            slot = 'objective'

        for weapon in player.weapons(is_filters=slot):
            player.drop_weapon(weapon)

        return

    try:
        name = weapon_manager[slot].name
    except KeyError:
        raise InvalidArgumentValue(f'"{slot}" is an invalid value for "slot:str".')

    for weapon in player.weapons():
        if weapon.classname == name:
            player.drop_weapon(weapon)
            break


@TypedServerCommand('wcs_spawn')
def wcs_spawn_command(command_info, player:convert_userid_to_player, force:int=0):
    if player is None:
        return

    player.spawn(force)


@TypedServerCommand('wcs_evasion')
def wcs_evasion_command(command_info, wcsplayer:convert_userid_to_wcsplayer, toggle:int, chance:int):
    warn('"wcs_evasion" will be removed in the future. Use "wcsgroup set evasion" and "wcsgroup set evasion_chance" instead.', PendingDeprecationWarning)

    if wcsplayer is None:
        return

    wcsplayer.data['evasion'] = toggle
    wcsplayer.data['evasion_chance'] = chance


@TypedServerCommand('wcs_absorb')
def wcs_absorb_command(command_info, wcsplayer:convert_userid_to_wcsplayer, value:float):
    warn('"wcs_absorb" will be removed in the future. Use "wcsgroup set absorb" instead.', PendingDeprecationWarning)

    if wcsplayer is None:
        return

    wcsplayer.data['absorb'] = value


@TypedServerCommand('wcs_getplayerindex')
def wcs_getplayerindex_command(command_info, player:convert_userid_to_player, var:ConVar):
    if player is None:
        var.set_int(-1)
        return

    var.set_int(player.index)


@TypedServerCommand('wcs_overlay')
def wcs_overlay_command(command_info, player:convert_userid_to_player, overlay:str, duration:float=0):
    warn('"wcs_overlay" will be removed in the future. Use "es_cexec" with "r_screenoverlay" and "es_delayed" instead.', PendingDeprecationWarning)

    if player is None:
        return

    player.client_command(f'r_screenoverlay {overlay}')

    if duration:
        player.delay(duration, _remove_overlay, (player.userid, ))


@TypedServerCommand('wcs_noflash')
def wcs_noflash_command(command_info, wcsplayer:convert_userid_to_wcsplayer, value:int):
    warn('"wcs_noflash" will be removed in the future. Use "wcsgroup set noflash" instead.', PendingDeprecationWarning)

    if wcsplayer is None:
        return

    wcsplayer.data['noflash'] = value


@TypedServerCommand('wcs_drug')
def wcs_drug_command(command_info, player:convert_userid_to_player, duration:float=0):
    warn('"wcs_drug" will be removed in the future. Use "es_cexec" with "r_screenoverlay" and "es_delayed" instead.', PendingDeprecationWarning)

    if player is None:
        return

    player.client_command('r_screenoverlay effects/tp_eyefx/tp_eyefx')

    if duration:
        player.delay(duration, _remove_overlay, (player.userid, ))


@TypedServerCommand('wcs_setresist')
def wcs_setresist_command(command_info, wcsplayer:convert_userid_to_wcsplayer, value:float, weapon:str):
    warn('"wcs_setresist" will be removed in the future. Use "wcsgroup set resist_<weapon>" instead.', PendingDeprecationWarning)

    if wcsplayer is None:
        return

    wcsplayer.data[f'resist_{weapon}'] = value


@TypedServerCommand('wcs_create_prop')
def wcs_create_prop_command(command_info, player:convert_userid_to_player, path:str, health:int):
    if player is None:
        return

    if not path.startswith('models/'):
        path = f'models/{path}'

    entity = Entity.create('prop_physics_multiplayer')
    entity.origin = player.view_coordinates
    entity.model = Model(path)
    entity.spawn()
    entity.set_property_uchar('m_takedamage', TakeDamage.YES)
    entity.health = health


@TypedServerCommand('wcs_fade')
def wcs_fade_command(command_info, player:convert_userid_to_player, red:int, green:int, blue:int, alpha:int, time:float, mode:int=None):
    if player is None:
        return

    color = Color(red, green, blue, alpha)

    mode = FadeFlags.values.get(mode, FadeFlags.IN)

    Fade(int(time), int(time), color, mode).send(player.index)


@TypedServerCommand('wcs_shake')
def wcs_shake_command(command_info, player:convert_userid_to_player, amplitude:float, frequency:float, duration:float):
    if player is None:
        return

    Shake(amplitude, duration, frequency).send(player.index)


@TypedServerCommand('wcs_teleport')
def wcs_teleport_command(command_info, player:convert_userid_to_player, x:float, y:float, z:float):
    if player is None:
        return

    location = Vector(x, y, z)
    origin = player.origin
    angles = QAngle(*player.get_property_vector('m_angAbsRotation'))

    forward = Vector()
    right = Vector()
    up = Vector()
    angles.get_angle_vectors(forward, right, up)

    forward.normalize()
    forward *= 10

    playerinfo = player.playerinfo
    mins, maxs = playerinfo.mins, playerinfo.maxs
    players = TraceFilterSimple(PlayerIter())

    for _ in range(100):
        ray = Ray(location, location, mins, maxs)
        trace = GameTrace()
        engine_trace.trace_ray(ray, ContentMasks.PLAYER_SOLID, players, trace)

        if not trace.did_hit():
            player.teleport(origin=location)
            break

        location -= forward

        if location.get_distance(origin) <= 10.0:
            break


@TypedServerCommand('wcs_regeneration')
def wcs_regeneration_command(command_info, player:convert_userid_to_player, value:int, duration:float, maxhealth:int, maxheal:deprecated, radius:float):
    if player is None:
        return

    repeat = Repeat(_regeneration_repeat, (player.userid, value, maxhealth, radius))
    repeat.start(duration)

    _repeats[player.userid].append(repeat)


@TypedServerCommand('wcs_warden')
def wcs_warden_command(command_info, wcsplayer:convert_userid_to_wcsplayer, duration:int, damage:int, radius:float, team_target:int, team_target_name:deprecated, x:float, y:float, z:float, round:deprecated):
    if wcsplayer is None:
        return

    ward = DamageWard(wcsplayer, Vector(x, y, z), radius, duration, damage)
    ward.team_target = team_target

    ward_manager.append(ward)


# ============================================================================
# >> EVENTS
# ============================================================================
@PreEvent('player_hurt')
def pre_player_hurt(event):
    if event['attacker']:
        wcsplayer = WCSPlayer.from_userid(event['userid'])

        absorb = wcsplayer.data.get('absorb')

        if absorb is not None and absorb > 0:
            health = int(event['dmg_health'] * absorb)

            if health > 0:
                wcsplayer.player.health += health

        resist = wcsplayer.data.get(f'resist_{event["weapon"]}')

        if resist is not None and resist > 0:
            health = int(event['dmg_health'] * resist)

            if health > 0:
                wcsplayer.player.health += health

        evasion = wcsplayer.data.get('evasion')

        if evasion is not None and evasion:
            chance = wcsplayer.data.get('evasion_chance')

            if chance is not None and chance > 0:
                if randint(0, 100) <= chance:
                    wcsplayer.player.health += int(event['dmg_health'])


@PreEvent('weapon_fire')
def weapon_fire_pre(event):
    userid = event['userid']

    if userid not in _norecoil:
        return

    player = _player_instances.from_userid(userid)
    weapon = _weapon_instances.from_inthandle(player.active_weapon_handle)

    player.set_network_property_uchar('cslocaldata.m_iShotsFired', 0)
    weapon.set_network_property_float('m_fAccuracyPenalty', 0.0)


@PreEvent('player_spawn')
def player_spawn(event):
    repeats = _repeats.pop(event['userid'], [])

    for repeat in repeats:
        if repeat.status == RepeatStatus.RUNNING:
            repeat.stop()

    delays = _delays.pop(event['userid'], [])

    for delay in delays:
        if delay.running:
            delay.cancel()

    _attackspeed.pop(event['userid'], None)
    _norecoil.discard(event['userid'])


@Event('player_death')
def player_death(event):
    repeats = _repeats.pop(event['userid'], [])

    for repeat in repeats:
        if repeat.status == RepeatStatus.RUNNING:
            repeat.stop()

    delays = _delays.pop(event['userid'], [])

    for delay in delays:
        if delay.running:
            delay.cancel()

    _attackspeed.pop(event['userid'], None)
    _norecoil.discard(event['userid'])


@Event('player_blind')
def player_blind(event):
    wcsplayer = WCSPlayer.from_userid(event['userid'])

    if wcsplayer.data.get('noflash'):
        player = wcsplayer.player

        player.flash_duration = 0
        player.flash_alpha = 0


@Event('weapon_fire')
def weapon_fire(event):
    userid = event['userid']

    if _attackspeed.get(userid) is None and userid not in _norecoil:
        return

    player = _player_instances.from_userid(userid)
    weapon = _weapon_instances.from_inthandle(player.active_weapon_handle)
    player.delay(0, weapon_fire_post, (player, userid, weapon))


def weapon_fire_post(player, userid, weapon):
    if userid in _norecoil:
        for prop in _weapon_fire_post_properties:
            player.set_network_property_vector(prop, NULL_VECTOR)

    fire_rate = _attackspeed.get(userid)

    if fire_rate is None:
        return

    cur_time = global_vars.current_time

    next_attack = weapon.get_datamap_property_float('m_flNextPrimaryAttack')
    next_attack = (next_attack - cur_time) * 1.0 / fire_rate + cur_time

    weapon.set_datamap_property_float('m_flNextPrimaryAttack', next_attack)
    player.set_datamap_property_float('m_flNextAttack', cur_time)


# ============================================================================
# >> LISTENERS
# ============================================================================
@OnPlayerRunCommand
def on_player_run_command(player, user_cmd):
    if player.get_datamap_property_bool('pl.deadflag'):
        return

    if player.userid not in _norecoil:
        return

    user_cmd.random_seed = 0


@OnPlayerChangeRace
def on_player_change_race(wcsplayer, old, new):
    _restrictions.player_restrictions[wcsplayer.userid].clear()


@OnPlayerDelete
def on_player_delete(wcsplayer):
    userid = wcsplayer.userid

    _attackspeed.pop(userid, None)
    _norecoil.discard(userid)

    repeats = _repeats.pop(userid, [])

    for repeat in repeats:
        if repeat.status == RepeatStatus.RUNNING:
            repeat.stop()

    delays = _delays.pop(userid, [])

    for delay in delays:
        if delay.running:
            delay.cancel()


@OnTakeDamageAlive
def on_take_damage_alive(wcsvictim, wcsattacker, info):
    if info.type & DamageTypes.BURN:
        fire_owner = wcsvictim.data.get('fire_owner')

        if fire_owner is not None:
            try:
                info.attacker = index_from_userid(fire_owner)
            except ValueError:
                del wcsvictim.data['fire_owner']
            else:
                info.inflictor = set_weapon_name('fire')
