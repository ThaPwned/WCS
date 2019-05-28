# ../wcs/core/helpers/esc/est/commands.py

# ============================================================================
# >> IMPORTS
# ============================================================================
# Source.Python Imports
#   CVars
from cvars import ConVar

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
