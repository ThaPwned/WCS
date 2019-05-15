# ../wcs/core/menus/close.py

# ============================================================================
# >> IMPORTS
# ============================================================================
# WCS Imports
#   Menus
from . import raceinfo_detail_menu
from . import raceinfo_skills_menu
from . import raceinfo_skills_detail_menu
from . import raceinfo_race_detail_menu
from . import shopinfo_detail_menu
from . import input_menu
#   Players
from ..players.entity import Player


# ============================================================================
# >> ALL DECLARATION
# ============================================================================
__all__ = ()


# ============================================================================
# >> CLOSE CALLBACKS
# ============================================================================
@raceinfo_detail_menu.register_close_callback
@raceinfo_skills_menu.register_close_callback
@raceinfo_skills_detail_menu.register_close_callback
@raceinfo_race_detail_menu.register_close_callback
def raceinfo_menu_close(menu, client):
    Player.from_index(client).data.pop('_internal_raceinfo_category', None)


@shopinfo_detail_menu.register_close_callback
def shopinfo_menu_close(menu, client):
    Player.from_index(client).data.pop('_internal_shopinfo_category', None)


@input_menu.register_close_callback
def input_menu_menu_close(menu, client):
    Player.from_index(client).data['_internal_input_delay']()
