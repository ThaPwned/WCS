# ../wcs/core/helpers/esc/est/commands.py

# ============================================================================
# >> IMPORTS
# ============================================================================
# Source.Python Imports
#   CVars
from cvars import ConVar
#   Engines
from engines.trace import ContentMasks
from engines.trace import engine_trace
from engines.trace import GameTrace
from engines.trace import Ray
#   Mathlib
from mathlib import Vector

# WCS Imports
#   Helpers
from .converts import convert_userid_identifier_to_players
from .converts import convert_operator
from .overwrites import ESTCommand
from ..converts import convert_userid_to_player


# ============================================================================
# >> ALL DECLARATION
# ============================================================================
__all__ = ()


# ============================================================================
# >> COMMANDS
# ============================================================================
@ESTCommand('Armor')
def armor_command(command_info, filter_:convert_userid_identifier_to_players, operator:convert_operator, amount:int):
    for player in filter_:
        player.armor = operator(player.armor, amount)


@ESTCommand('ArmorAdd')
def armor_add_command(command_info, filter_:convert_userid_identifier_to_players, amount:int):
    for player in filter_:
        player.armor += amount


@ESTCommand('ArmorSet')
def armor_set_command(command_info, filter_:convert_userid_identifier_to_players, amount:int):
    for player in filter_:
        player.armor = amount


@ESTCommand('ArmorGet')
def armor_get_command(command_info, var:ConVar, player:convert_userid_to_player):
    if player is None:
        var.set_int(0)
        return

    var.set_int(player.armor)


@ESTCommand('Health')
def health_command(command_info, filter_:convert_userid_identifier_to_players, operator:convert_operator, amount:int):
    for player in filter_:
        player.health = operator(player.health, amount)


@ESTCommand('HealthAdd')
def health_add_command(command_info, filter_:convert_userid_identifier_to_players, amount:int):
    for player in filter_:
        player.health += amount


@ESTCommand('HealthSet')
def health_set_command(command_info, filter_:convert_userid_identifier_to_players, amount:int):
    for player in filter_:
        player.health = amount


@ESTCommand('HealthGet')
def health_get_command(command_info, var:ConVar, player:convert_userid_to_player):
    if player is None:
        var.set_int(0)
        return

    var.set_int(player.health)


@ESTCommand('Cash')
def cash_command(command_info, filter_:convert_userid_identifier_to_players, operator:convert_operator, amount:int):
    for player in filter_:
        player.cash = operator(player.cash, amount)


@ESTCommand('CashAdd')
def cash_add_command(command_info, filter_:convert_userid_identifier_to_players, amount:int):
    for player in filter_:
        player.cash += amount


@ESTCommand('CashSet')
def cash_set_command(command_info, filter_:convert_userid_identifier_to_players, amount:int):
    for player in filter_:
        player.cash = amount


@ESTCommand('CashGet')
def cash_get_command(command_info, var:ConVar, player:convert_userid_to_player):
    if player is None:
        var.set_int(0)
        return

    var.set_int(player.cash)


@ESTCommand('GetWallBetween')
def get_wall_between_command(command_info, var:ConVar, x:float, y:float, z:float, x2:float, y2:float, z2:float):
    vector = Vector(x, y, z)
    vector2 = Vector(x, y, z)

    trace = GameTrace()
    ray = Ray(vector, vector2)

    engine_trace.trace_ray(ray, ContentMasks.ALL, None, trace)

    var.set_int(trace.did_hit_world())
