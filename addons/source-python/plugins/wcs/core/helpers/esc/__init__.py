# ../wcs/core/helpers/esc/__init__.py

# ============================================================================
# >> IMPORTS
# ============================================================================
# WCS Imports
#   Constants
from ...constants.paths import ITEM_PATH_ES
from ...constants.paths import MODULE_PATH_ES
from ...constants.paths import RACE_PATH_ES


# ============================================================================
# >> ALL DECLARATION
# ============================================================================
__all__ = ()


# ============================================================================
# >> GLOBAL VARIABLES
# ============================================================================
for x in (ITEM_PATH_ES, MODULE_PATH_ES, RACE_PATH_ES):
    if not x.isdir():
        x.makedirs()
