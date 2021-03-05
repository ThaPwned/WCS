# ../wcs/core/helpers/esc/__init__.py

# ============================================================================
# >> IMPORTS
# ============================================================================
# Source.Python Imports
#   Commands
from commands.server import get_server_command
#   Core
from core import GAME_NAME
#   Events
from events import Event
#   Listeners
from listeners import OnLevelInit

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
if GAME_NAME == 'cstrike':
    _disabled_autokick = set()
    _mp_disable_autokick = get_server_command('mp_disable_autokick')

for x in (ITEM_PATH_ES, MODULE_PATH_ES, RACE_PATH_ES):
    if not x.isdir():
        x.makedirs()


wcsuserdata = es_C.user_groups.find_key('WCSuserdata', True)
wcstmp = es_C.user_groups.find_key('WCStmp', True)


if GAME_NAME == 'cstrike':
    # ============================================================================
    # >> EVENTS
    # ============================================================================
    @Event('player_spawn')
    def player_spawn(event):
        userid = event['userid']

        if userid in _disabled_autokick:
            return

        _mp_disable_autokick(userid)

        _disabled_autokick.add(userid)

    @Event('player_disconnect')
    def player_disconnect(event):
        userid = event['userid']

        _disabled_autokick.discard(userid)

    # ============================================================================
    # >> LISTENERS
    # ============================================================================
    @OnLevelInit
    def on_level_init(mapname):
        _disabled_autokick.clear()
