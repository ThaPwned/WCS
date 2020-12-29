# ../wcs/core/constants/__init__.py

# ============================================================================
# >> IMPORTS
# ============================================================================
# Python Imports
#   Enum
from enum import IntEnum
#   JSON
from json import dump
from json import load
#   Warnings
from warnings import warn

# Source.Python Imports
#   Core
from core import SOURCE_ENGINE_BRANCH

# WCS Imports
#   Constants
from .info import info
from .paths import CFG_PATH


# ============================================================================
# >> ALL DECLARATION
# ============================================================================
__all__ = (
    'COLOR_DARKGREEN',
    'COLOR_DEFAULT',
    'COLOR_GREEN',
    'COLOR_LIGHTGREEN',
    'COMMANDS',
    'GITHUB_ACCESS_TOKEN',
    'GITHUB_PASSWORD',
    'GITHUB_USERNAME',
    'IS_ESC_SUPPORT_ENABLED',
    'TIME_FORMAT',
    'GithubStatus',
    'GithubModuleStatus',
    'ItemReason',
    'NodeType',
    'SkillReason',
    'ModuleType',
    'RaceReason',
    'DatabaseVersion',
)


# ============================================================================
# >> CLASSES
# ============================================================================
class ModuleType(IntEnum):
    SP = 0
    ESP = 1
    ESS = 2
    ESS_INI = 3
    ESS_KEY = 4


class ItemReason(IntEnum):
    ALLOWED = 0
    TOO_MANY = 1
    CANNOT_AFFORD = 2
    RACE_RESTRICTED = 3
    TOO_MANY_CATEGORY = 4
    WRONG_STATUS = 5
    REQUIRED_LEVEL = 6
    ROUND_RESTART = 7


class SkillReason(IntEnum):
    ALLOWED = 0
    LEVEL = 1
    COOLDOWN = 2
    DEACTIVATED = 3
    DEAD = 4
    TEAM = 5


class RaceReason(IntEnum):
    ALLOWED = 0
    REQUIRED_LEVEL = 1
    MAXIMUM_LEVEL = 2
    TEAM_LIMIT = 3
    TEAM = 4
    PRIVATE = 5
    MAP = 6
    VIP = 7
    ADMIN = 8
    BOT = 9


class GithubStatus(IntEnum):
    PREPARING = 0
    CONNECTING = 1
    DOWNLOADING = 2
    UNZIPPING = 3
    EXTRACTING = 4
    COPYING = 5
    FINISHING = 6


class GithubModuleStatus(IntEnum):
    INSTALLED = 0
    INSTALLING = 1
    UPDATING = 2
    UNINSTALLING = 3
    UNINSTALLED = 4


class NodeType(IntEnum):
    QUERY = 0
    QUERY_MANY = 1
    CALLBACK = 2
    CONNECT = 3
    USE = 4
    CLOSE = 5


class DatabaseVersion(IntEnum):
    INITIAL = 0
    UPDATE1 = 1
    UPDATE2 = 2
    UPDATE3 = 3
    CURRENT = UPDATE3


# ============================================================================
# >> CONSTANTS
# ============================================================================
# Allow ESC races/items
IS_ESC_SUPPORT_ENABLED = True

try:
    import es
    import esc
except ImportError:
    IS_ESC_SUPPORT_ENABLED = False

    warn('IS_ESC_SUPPORT_ENABLED was set to True but EventScripts was not found')

if (CFG_PATH / 'github.json').isfile():
    with open(CFG_PATH / 'github.json') as inputfile:
        data = load(inputfile)

    GITHUB_USERNAME = data.get('username')
    GITHUB_PASSWORD = data.get('password')
    GITHUB_ACCESS_TOKEN = data.get('access_token')
    GITHUB_REPOSITORIES = data.get('repositories', [])
else:
    with open(CFG_PATH / 'github.json', 'w') as outputfile:
        dump({'username':None, 'password':None, 'access_token':None, 'repositories':[]}, outputfile, indent=4)

    GITHUB_USERNAME = None
    GITHUB_PASSWORD = None
    GITHUB_ACCESS_TOKEN = None
    GITHUB_REPOSITORIES = []

GITHUB_REPOSITORIES.insert(0, f'{info.author.replace(" ", "")}/WCS-Contents')

TIME_FORMAT = '%H:%M:%S %d/%m/%Y'
# TODO: Or should it be?
# TIME_FORMAT = '%a %d %b %Y, %H:%M:%S'

# Copied from EventScripts Emulator (es_emulator/helpers.py#90-99)
if SOURCE_ENGINE_BRANCH == 'csgo':
    COLOR_DEFAULT = '\1'
    COLOR_GREEN = '\4'
    COLOR_LIGHTGREEN = '\5'
    COLOR_DARKGREEN = '\6'
else:
    COLOR_DEFAULT = '\1'
    COLOR_GREEN = '\4'
    COLOR_LIGHTGREEN = '\3'
    COLOR_DARKGREEN = '\5'

if not (CFG_PATH / 'commands.json').isfile():
    with open(CFG_PATH / 'commands.json', 'w') as outputfile:
        dump({
            'wcs':['wcs', 'wcsmenu'],
            'shopmenu':['shopmenu'],
            'shopinfo':['shopinfo'],
            'showskills':['showskills'],
            'resetskills':['resetskills'],
            'spendskills':['spendskills'],
            'changerace':['changerace'],
            'raceinfo':['raceinfo'],
            'myraceinfo':['myraceinfo'],
            'myinfo':['myinfo'],
            'playerinfo':['playerinfo'],
            'wcstop':['wcstop'],
            'wcsrank':['wcsrank'],
            'wcshelp':['wcshelp'],
            'wcsadmin':['wcsadmin'],
            'showxp':['showxp'],
            'levelbank':['levelbank', 'wcsbank']
        },
            outputfile, indent=4)

with open(CFG_PATH / 'commands.json') as inputfile:
    COMMANDS = load(inputfile)

if 'levelbank' not in COMMANDS:
    COMMANDS['levelbank'] = ['levelbank', 'wcsbank']

    with open(CFG_PATH / 'commands.json', 'w') as outputfile:
        dump(COMMANDS, outputfile, indent=4)

if 'myinfo' not in COMMANDS:
    COMMANDS['myinfo'] = ['myinfo']

    with open(CFG_PATH / 'commands.json', 'w') as outputfile:
        dump(COMMANDS, outputfile, indent=4)
