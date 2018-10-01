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
    'GITHUB_ACCESS_TOKEN',
    'IS_ESC_SUPPORT_ENABLED',
    'IS_GITHUB_ENABLED',
    'TIME_FORMAT',
    'GithubStatus',
    'ItemReason',
    'SkillReason',
    'ModuleType',
    'RaceReason',
)


# ============================================================================
# >> CLASSES
# ============================================================================
class ModuleType(IntEnum):
    SP = 0
    ESP = 1
    ESS = 2
    ESS_OLD = 3


class ItemReason(IntEnum):
    ALLOWED = 0
    TOO_MANY = 1
    CANNOT_AFFORD = 2
    RACE_RESTRICTED = 3
    TOO_MANY_CATEGORY = 4
    WRONG_STATUS = 5
    REQUIRED_LEVEL = 6


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


class GithubStatus(IntEnum):
    INSTALLED = 0
    INSTALLING = 1
    UPDATING = 2
    UNINSTALLING = 3
    UNINSTALLED = 4


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

if (CFG_PATH / 'github.json').isfile():
    with open(CFG_PATH / 'github.json') as inputfile:
        data = load(inputfile)

    GITHUB_ACCESS_TOKEN = data.get('access_token', None)
    GITHUB_REPOSITORIES = data.get('repositories', [])
else:
    with open(CFG_PATH / 'github.json', 'w') as outputfile:
        dump({'access_token':None, 'repositories':[]}, outputfile, indent=4)

    GITHUB_ACCESS_TOKEN = None
    GITHUB_REPOSITORIES = []

GITHUB_REPOSITORIES.insert(0, f'{info.author.replace(" ", "")}/WCS-Contents')

IS_GITHUB_ENABLED = GITHUB_ACCESS_TOKEN is not None

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
