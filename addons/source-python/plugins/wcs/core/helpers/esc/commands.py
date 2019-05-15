# ../wcs/core/helpers/esc/commands.py

# ============================================================================
# >> IMPORTS
# ============================================================================
# Python Imports
#   Random
from random import choice
#   Shlex
from shlex import split
#   String
from string import Template
#   Time
from time import time

# Source.Python Imports
#   Colors
from colors import Color
#   Commands
from commands.typed import TypedServerCommand
#   CVars
from cvars import ConVar
#   Engines
from engines.server import execute_server_command
#   Entities
from entities.constants import MoveType
#   Filters
from filters.weapons import WeaponClassIter
#   Keyvalues
from _keyvalues import KeyValues
# NOTE: Have to prefix it with a _ otherwise it'd import KeyValues from ES Emulator if it's loaded
#   Listeners
from listeners.tick import Delay
#   Mathlib
from mathlib import Vector
#   Messages
from messages import HudMsg
from messages import SayText2
#   Players
from players.entity import Player
from players.helpers import index_from_userid
#   Translations
from translations.strings import LangStrings
#   Weapons
from weapons.restrictions import WeaponRestrictionHandler

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
from .converts import real_value
from .converts import valid_operators
from .converts import split_str
from .converts import deprecated
#   Players
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


# ============================================================================
# >> HELPER FUNCTIONS
# ============================================================================
def validate_userid_after_delay(callback, userid, *args, validator=convert_userid_to_player):
    callback(None, validator(userid), *args)


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
        Delay(time, validate_userid_after_delay, (wcs_setfx_freeze_command, player.userid, '=', not value))


@TypedServerCommand(['wcs_setfx', 'jetpack'])
def wcs_setfx_jetpack_command(command_info, player:convert_userid_to_player, operator:valid_operators('='), value:int, time:float=0):
    if player is None:
        return

    if value:
        player.move_type = MoveType.FLY
    else:
        player.move_type = MoveType.WALK

    if time > 0:
        Delay(time, validate_userid_after_delay, (wcs_setfx_jetpack_command, player.userid, '=', not value))


@TypedServerCommand(['wcs_setfx', 'god'])
def wcs_setfx_god_command(command_info, player:convert_userid_to_player, operator:valid_operators('='), value:int, time:float=0):
    if player is None:
        return

    player.godmode = value

    if time > 0:
        Delay(time, validate_userid_after_delay, (wcs_setfx_god_command, player.userid, '=', not value))


@TypedServerCommand(['wcs_setfx', 'noblock'])
def wcs_setfx_noblock_command(command_info, player:convert_userid_to_player, operator:valid_operators('='), value:int, time:float=0):
    if player is None:
        return

    player.noblock = value

    if time > 0:
        Delay(time, validate_userid_after_delay, (wcs_setfx_noblock_command, player.userid, '=', not value))


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
        Delay(time, validate_userid_after_delay, (wcs_setfx_speed_command, player.userid, '+', value))


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
        Delay(time, validate_userid_after_delay, (wcs_setfx_invis_command, player.userid, '+', value))


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
        Delay(time, validate_userid_after_delay, (wcs_setfx_health_command, player.userid, '+', value))


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
        Delay(time, validate_userid_after_delay, (wcs_setfx_armor_command, player.userid, '+', value))


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
        Delay(time, validate_userid_after_delay, (wcs_setfx_cash_command, player.userid, '+', value))


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
        Delay(time, validate_userid_after_delay, (wcs_setfx_gravity_command, player.userid, '+', value))


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
        Delay(time, validate_userid_after_delay, (wcs_setfx_ulti_immunity_command, wcsplayer.userid, '+', value), {'validator':convert_userid_to_wcsplayer})


@TypedServerCommand(['wcs_setfx', 'disguise'])
def wcs_setfx_disguise_command(command_info, wcsplayer:convert_userid_to_player, operator:valid_operators(), value:int, time:float=0):
    pass  # TODO


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
        Delay(time, validate_userid_after_delay, (wcs_setfx_longjump_command, wcsplayer.userid, '+', value), {'validator':convert_userid_to_wcsplayer})


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
def wcsgroup_set_command(command_info, key:str, userid:valid_userid_and_team, value:real_value):
    if userid is None:
        return

    if isinstance(userid, str):
        team_data[{'T':2, 'CT':3}[userid]][key] = value
    else:
        wcsplayer = WCSPlayer.from_userid(userid)

        wcsplayer.data[key] = value


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
def wcs_foreach_command(command_info, var:str, players:convert_userid_identifier_to_players, command:str):
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
def wcs_changerace_command(command_info, wcsplayer:convert_userid_to_wcsplayer, name:str):
    if wcsplayer is None:
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
        var.set_int(0)
        return

    if key == 'race':
        if attribute == 'realname':
            var.set_string(wcsplayer.active_race.name)
        elif attribute == 'name':
            var.set_string(wcsplayer.active_race.settings.strings['name'])
    elif key == 'player':
        if attribute == 'realcurrace':
            var.set_string(wcsplayer.active_race.name)
        elif attribute == 'currace':
            var.set_string(wcsplayer.active_race.settings.strings['name'])


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

    _restrictions.remove_player_restrictions(player, *weapons)


@TypedServerCommand('wcs_getlanguage')
def wcs_getlanguage_command(command_info, var:ConVar, id_:str, language:str='en'):
    var.set_string(_languages.get(language, {}).get(id_, 'n/a'))


@TypedServerCommand('wcs_randplayer')
def wcs_randplayer_command(command_info, var:ConVar, players:convert_identifier_to_players):
    players = list(players)

    if players:
        var.set_int(choice(list(players)).userid)
    else:
        var.set_int(0)


@TypedServerCommand('wcs_get_cooldown')
def wcs_get_cooldown_command(command_info, wcsplayer:convert_userid_to_wcsplayer, var:ConVar):
    if wcsplayer is None:
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
    wcs_set_cooldown_command(command_info, wcsplayer, time())
