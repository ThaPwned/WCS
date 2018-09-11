# ../wcs/core/helpers/esc/commands.py

# ============================================================================
# >> IMPORTS
# ============================================================================
# Source.Python Imports
#   Commands
from commands.typed import TypedServerCommand
#   CVars
from cvars import ConVar
#   Engines
from engines.server import queue_command_string
#   Entities
from entities.constants import MoveType
#   Filters
from filters.players import PlayerIter
#   Listeners
from listeners.tick import Delay
#   Mathlib
from mathlib import Vector
#   Players
from players.entity import Player
from players.helpers import index_from_userid

# WCS Imports
#   Players
from ...players import team_data
from ...players.entity import Player as WCSPlayer


# ============================================================================
# >> HELPER FUNCTIONS
# ============================================================================
def valid_userid(userid):
    try:
        userid = int(userid)
        index_from_userid(userid)
    except ValueError:
        return None

    return userid


def valid_userid_and_team(userid):
    new_userid = valid_userid(userid)

    if new_userid is None:
        if userid in ('T', 'CT'):
            return userid

        return None

    return new_userid


def convert_userid_to_player(userid):
    userid = valid_userid(userid)

    if userid is None:
        return None

    player = Player.from_userid(userid)

    if player.dead:
        return None

    return player


def convert_userid_to_wcsplayer(userid):
    userid = valid_userid(userid)

    if userid is None:
        return None

    return WCSPlayer.from_userid(userid)


def convert_identifier_to_players(filter_):
    filter_ = filter_.split(',')
    is_filters = [x.replace('#', '') for x in filter_ if x.startswith('#')]
    not_filters = [x.replace('!', '') for x in filter_ if x.startswith('!')]

    for player in PlayerIter(is_filters=is_filters, not_filters=not_filters):
        yield player


def real_value(value):
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            return value


def valid_operators(operators=('=', '+', '-')):
    def validate_operator(value):
        return value if value in operators else '='

    return validate_operator


def validate_userid_after_delay(callback, userid, *args, validator=convert_userid_to_player):
    callback(None, validator(userid), *args)


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
def wcs_setfx_invis_command(command_info, player:convert_userid_to_player, operator:valid_operators(), value:float, time:float=0):
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


@TypedServerCommand('wcs_nearcoord')
def wcs_nearcoord_command(command_info, var:str, players:convert_identifier_to_players, x:float, y:float, z:float, distance:float, command:str):
    vector = Vector(x, y, z)

    for player in players:
        if vector.get_distance(player.origin) <= distance:
            queue_command_string(f'es_xset {var} {player.userid};{command}')
