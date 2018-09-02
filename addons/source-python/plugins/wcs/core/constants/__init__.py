# ../wcs/core/constants/__init__.py

# ============================================================================
# >> IMPORTS
# ============================================================================
# Python Imports
#   Enum
from enum import IntEnum
#   JSON
from json import load

# WCS Imports
#   Constants
from .paths import CFG_PATH


# ============================================================================
# >> ALL DECLARATION
# ============================================================================
__all__ = (
    'GITHUB_ACCESS_TOKEN',
    'IS_ESC_SUPPORT_ENABLED',
    'IS_GITHUB_ENABLED',
    'TIME_FORMAT',
    'GithubStatus',
    'ItemReason',
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


class ItemReason(IntEnum):
    ALLOWED = 0
    TOO_MANY = 1
    CANNOT_AFFORD = 2
    RACE_RESTRICTED = 3
    TOO_MANY_CATEGORY = 4
    WRONG_STATUS = 5
    REQUIRED_LEVEL = 6


class RaceReason(IntEnum):
    ALLOWED = 0
    REQUIRED_LEVEL = 1
    MAXIMUM_LEVEL = 2
    TEAM = 3
    PRIVATE = 4
    MAP = 5
    VIP = 6


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

if (CFG_PATH / 'github.json').isfile():
    with open(CFG_PATH / 'github.json') as outputfile:
        GITHUB_ACCESS_TOKEN = load(outputfile).get('access_token', None)
else:
    GITHUB_ACCESS_TOKEN = None

IS_GITHUB_ENABLED = GITHUB_ACCESS_TOKEN is not None

TIME_FORMAT = '%H:%M:%S %d/%m/%Y'
# TODO: Or should it be?
# TIME_FORMAT = '%a %d %b %Y, %H:%M:%S'
