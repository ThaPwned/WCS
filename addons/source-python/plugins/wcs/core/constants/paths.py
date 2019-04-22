# ../wcs/core/constants/__init__.py

# ============================================================================
# >> IMPORTS
# ============================================================================
# Source.Python Imports
#   Paths
from paths import CFG_PATH as _CFG_PATH
from paths import TRANSLATION_PATH as _TRANSLATION_PATH
from paths import PLUGIN_PATH as _PLUGIN_PATH
from paths import PLUGIN_DATA_PATH

# WCS Imports
#   Constants
from .info import info


# ============================================================================
# >> ALL DECLARATION
# ============================================================================
__all__ = (
    'CFG_PATH',
    'DATA_PATH',
    'ITEM_PATH',
    'ITEM_PATH_ES',
    'MODULE_PATH',
    'MODULE_PATH_ES',
    'PLUGIN_PATH',
    'RACE_PATH',
    'RACE_PATH_ES',
    'STRUCTURE_PATH',
    'TRANSLATION_PATH',
)


# ============================================================================
# >> GLOBAL VARIABLES
# ============================================================================
# Configuration path
CFG_PATH = _CFG_PATH / info.name
# Translation path
TRANSLATION_PATH = _TRANSLATION_PATH / info.name
# Data path
DATA_PATH = PLUGIN_DATA_PATH / info.name
# Structure path
STRUCTURE_PATH = DATA_PATH / 'structure'
# Plugin path
PLUGIN_PATH = _PLUGIN_PATH / info.name
# Module path
MODULE_PATH = PLUGIN_PATH / 'modules'
# Race path
RACE_PATH = MODULE_PATH / 'races'
# Item path
ITEM_PATH = MODULE_PATH / 'items'
# EventScripts module path
MODULE_PATH_ES = _PLUGIN_PATH / 'es_emulator' / 'eventscripts' / 'wcs' / 'modules'
# EventScripts race path
RACE_PATH_ES = MODULE_PATH_ES / 'races'
# EventScripts item path
ITEM_PATH_ES = MODULE_PATH_ES / 'items'


# Loop through all our directories
for _name in __all__:
    # Does the name not end with _ES?
    if not _name.endswith('_ES'):
        # Get the path.Path instance
        _path = globals()[_name]

        # Does the directory not exist?
        if not _path.isdir():
            # Create it
            _path.makedirs()
