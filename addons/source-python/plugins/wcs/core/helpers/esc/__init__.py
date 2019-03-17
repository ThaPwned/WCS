# ../wcs/core/helpers/esc/__init__.py

# ============================================================================
# >> IMPORTS
# ============================================================================
# EventScripts Imports
#   es_C
import es_C

# WCS Imports
#   Constants
from ...constants.paths import ITEM_PATH_ES
from ...constants.paths import MODULE_PATH_ES
from ...constants.paths import RACE_PATH_ES


# ============================================================================
# >> ALL DECLARATION
# ============================================================================
__all__ = (
    'wcstmp',
    'wcsuserdata',
)


# ============================================================================
# >> GLOBAL VARIABLES
# ============================================================================
for x in (ITEM_PATH_ES, MODULE_PATH_ES, RACE_PATH_ES):
    if not x.isdir():
        x.makedirs()


wcsuserdata = es_C.user_groups.find_key('WCSuserdata', True)
wcstmp = es_C.user_groups.find_key('WCStmp', True)
