# ../wcs/core/helpers/esc/monkeypatch.py

# ============================================================================
# >> IMPORTS
# ============================================================================
# Python Imports
#   Sys
from sys import modules
#   Types
from types import MethodType

# Source.Python Imports
#   Colors
from colors import Color
#   Messages
from messages import Fade
from messages import FadeFlags
from messages import SayText2
#   Players
from players.helpers import index_from_userid

# EventScripts Imports
#   Cmdlib
from cmdlib import cmd_manager

# WCS Imports
#   Helpers
from .commands import _format_message
#   Players
from ...players.entity import Player


# ============================================================================
# >> ALL DECLARATION
# ============================================================================
__all__ = ()


# ============================================================================
# >> GLOBAL VARIABLES
# ============================================================================
_patched_commands = (
    'wcs_foreach',
    'wcs_nearcoord',
    'wcs_xtell'
)


# ============================================================================
# >> CLASSES
# ============================================================================
class _MockWCSGroup(object):
    @staticmethod
    def addUser(userid):
        # The player is added immediately, so do nothing
        pass

    @staticmethod
    def delUser(userid):
        # The player will be deleted when they leave, so do nothing
        pass

    @staticmethod
    def existsUser(userid):
        try:
            index_from_userid(int(userid))
        except ValueError:
            return False

        return True

    @staticmethod
    def setUser(userid, key, value):
        try:
            player = Player.from_userid(int(userid))
        except ValueError:
            pass
        else:
            player.data[key] = value

    @staticmethod
    def getUser(userid, key):
        try:
            player = Player.from_userid(int(userid))
        except ValueError:
            return None
        else:
            value = player.data.get(key)

            if value is None:
                return value

            if str(value).isdigit():
                return int(value)

            return value


class _MockXTell(object):
    @staticmethod
    def tell(userid, text, tokens={}, extra='', lng=True):
        players, message = _format_message(str(userid), text, ' '.join(f'{x} {y}' for x, y in tokens.items()))

        for player in players:
            SayText2(message[message.get(player.language, 'en')]).send(player.index)


class _MockWCSCommands(object):
    @staticmethod
    def fade(userid, red, green, blue, alpha, time):
        try:
            index = index_from_userid(int(userid))
        except ValueError:
            pass
        else:
            color = Color(red, green, blue, alpha)

            Fade(int(time), int(time), color, FadeFlags.PURGE).send(index)

    @staticmethod
    def damage(userid, damage, attacker=None, armor=False, weapon=None, solo=None):
        try:
            player = Player.from_userid(int(userid))
        except ValueError:
            pass
        else:
            if not player.player.dead:
                try:
                    attacker = index_from_userid(attacker)
                except ValueError:
                    pass
                else:
                    player.take_damage(damage, attacker=attacker)


# ============================================================================
# >> GLOBAL VARIABLES
# ============================================================================
_mock_wcsgroup = _MockWCSGroup()
_mock_xtell = _MockXTell()
_mock_wcscommands = _MockWCSCommands()


# ============================================================================
# >> FUNCTIONS
# ============================================================================
def register_server_command_patch(self, name, callback, description, skipcheck=False):
    if str(name) in _patched_commands:
        return

    _original_register_server_command(name, callback, description, skipcheck)


def unregister_server_command_patch(self, name):
    if str(name) in _patched_commands:
        return

    _original_unregister_server_command(name)


# ============================================================================
# >> COMMAND PATCHING
# ============================================================================
_original_register_server_command = cmd_manager.registerServerCommand
_original_unregister_server_command = cmd_manager.unregisterServerCommand

cmd_manager.registerServerCommand = MethodType(register_server_command_patch, cmd_manager)
cmd_manager.unregisterServerCommand = MethodType(unregister_server_command_patch, cmd_manager)


# ============================================================================
# >> MODULE PATCHING
# ============================================================================
modules['wcs.wcsgroup'] = _mock_wcsgroup
modules['wcs.xtell'] = _mock_xtell
modules['wcs.wcs_commands'] = _mock_wcscommands
