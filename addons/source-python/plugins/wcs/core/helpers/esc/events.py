# ../wcs/core/helpers/esc/events.py

# ============================================================================
# >> IMPORTS
# ============================================================================
# Source.Python Imports
#   Events
from events import Event

# EventScripts Imports
#   ESC
import esc

# WCS Imports
#   Constants
from ...constants import ModuleType
#   Helpers
from . import wcstmp
from . import wcsuserdata
from .vars import cvar_wcs_userid
#   Listeners
from ...listeners import OnPlayerDelete
from ...listeners import OnPlayerReady
#   Players
from ...players.entity import Player


# ============================================================================
# >> ALL DECLARATION
# ============================================================================
__all__ = ()


# ============================================================================
# >> LISTENERS
# ============================================================================
@OnPlayerReady
def on_player_ready(wcsplayer):
    wcstmp.find_key(str(wcsplayer.userid), True)
    wcsuserdata.find_key(str(wcsplayer.userid), True)


@OnPlayerDelete
def on_player_delete(wcsplayer):
    wcstmp.remove_sub_key(wcstmp.find_key(str(wcsplayer.userid)))
    wcsuserdata.remove_sub_key(wcsuserdata.find_key(str(wcsplayer.userid)))


# ============================================================================
# >> EVENTS
# ============================================================================
@Event('player_spawn')
def player_spawn(event):
    userid = event['userid']
    wcsplayer = Player.from_userid(userid)

    if wcsplayer.ready:
        wcsplayer.data.pop('ability', None)


# ============================================================================
# >> FUNCTIONS
# ============================================================================
# Totally out of place...
def _execute_ability(wcsplayer):
    active_race = wcsplayer.active_race

    if active_race.settings.type is ModuleType.ESS_INI:
        ability = wcsplayer.data.get('ability')

        if ability is not None:
            addon = esc.addons.get(f'wcs/tools/abilitys/{ability}')

            if addon is not None:
                executor = addon.blocks.get(ability)

                if executor is not None:
                    cvar_wcs_userid.set_int(wcsplayer.userid)

                    executor.run()
    elif active_race.settings.type is ModuleType.ESS_KEY:
        pass
