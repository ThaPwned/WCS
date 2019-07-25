# ../wcs/core/menus/menus.py

# ============================================================================
# >> IMPORTS
# ============================================================================
# Python Imports
#   Copy
from copy import deepcopy
#   Textwrap
from textwrap import wrap

# Source.Python Imports
#   Core
from core import GAME_NAME
#   Menus
from menus import PagedOption
from menus import SimpleOption
from menus import Text
from menus.radio import BUTTON_BACK
from menus.radio import BUTTON_CLOSE_SLOT

# WCS Imports
#   Constants
from ..constants import GithubStatus
from ..constants.info import info
#   Listeners
from ..listeners import OnGithubCommitsRefresh
from ..listeners import OnGithubCommitsRefreshed
from ..listeners import OnGithubModuleInstalled
from ..listeners import OnGithubModuleUpdated
from ..listeners import OnGithubModuleUninstalled
from ..listeners import OnGithubModulesRefresh
from ..listeners import OnGithubModulesRefreshed
from ..listeners import OnGithubNewVersionChecked
from ..listeners import OnGithubNewVersionInstalled
from ..listeners import OnPlayerQuery
#   Menus
from . import main_menu
from . import shopmenu_menu
from . import shopinfo_menu
from . import shopinfo_detail_menu
from . import showskills_menu
from . import resetskills_menu
from . import spendskills_menu
from . import changerace_menu
from . import changerace_search_menu
from . import raceinfo_menu
from . import raceinfo_search_menu
from . import raceinfo_detail_menu
from . import raceinfo_skills_menu
from . import raceinfo_skills_detail_menu
from . import raceinfo_race_detail_menu
from . import playerinfo_menu
from . import playerinfo_detail_menu
from . import playerinfo_detail_skills_menu
from . import playerinfo_detail_stats_menu
from . import wcstop_menu
from . import wcstop_detail_menu
from . import wcshelp_menu
from . import welcome_menu
from . import input_menu
from . import wcsadmin_menu
from . import wcsadmin_players_menu
from . import wcsadmin_players_sub_menu
from . import wcsadmin_players_sub_xp_menu
from . import wcsadmin_players_sub_levels_menu
from . import wcsadmin_management_menu
from . import wcsadmin_management_races_menu
from . import wcsadmin_management_items_menu
from . import wcsadmin_management_races_add_menu
from . import wcsadmin_management_items_add_menu
from . import wcsadmin_management_races_editor_menu
from . import wcsadmin_management_items_editor_menu
from . import wcsadmin_management_races_editor_modify_menu
from . import wcsadmin_management_races_editor_modify_from_selection_menu
from . import wcsadmin_management_races_editor_modify_restricted_team_menu
from . import wcsadmin_github_menu
from . import wcsadmin_github_races_menu
from . import wcsadmin_github_races_options_menu
from . import wcsadmin_github_races_repository_menu
from . import wcsadmin_github_items_menu
from . import wcsadmin_github_items_options_menu
from . import wcsadmin_github_items_repository_menu
from . import wcsadmin_github_info_menu
from . import wcsadmin_github_info_confirm_menu
from . import wcsadmin_github_info_confirm_commits_menu
from . import wcsadmin_github_info_commits_menu
from .base import PagedMenu
from .select import _request_required
from .select import _request_maximum
from .select import _request_team_limit
#   Translations
from ..translations import menu_strings


# ============================================================================
# >> ALL DECLARATION
# ============================================================================
__all__ = ()


# ============================================================================
# >> MENU TITLES
# ============================================================================
shopmenu_menu.title = menu_strings['shopmenu_menu title']
shopinfo_menu.title = menu_strings['shopinfo_menu title']
showskills_menu.title = menu_strings['showskills_menu title']
showskills_menu.description = menu_strings['showskills_menu description']
spendskills_menu.title = menu_strings['spendskills_menu title']
spendskills_menu.description = menu_strings['spendskills_menu description']
changerace_menu.title = menu_strings['changerace_menu title']
changerace_search_menu.title = menu_strings['changerace_menu title']
raceinfo_menu.title = menu_strings['raceinfo_menu title']
raceinfo_search_menu.title = menu_strings['raceinfo_menu title']
raceinfo_skills_menu.title = menu_strings['raceinfo_skills_menu title']
playerinfo_menu.title = menu_strings['playerinfo_menu title']
playerinfo_detail_skills_menu.title = menu_strings['playerinfo_detail_skills_menu title']
wcstop_menu.title = menu_strings['wcstop_menu title']
wcsadmin_players_menu.title = menu_strings['wcsadmin_players_menu title']
wcsadmin_management_races_menu.title = menu_strings['wcsadmin_management_races_menu title']
wcsadmin_management_items_menu.title = menu_strings['wcsadmin_management_items_menu title']
wcsadmin_management_races_add_menu.title = menu_strings['wcsadmin_management_races_add_menu title']
wcsadmin_management_items_add_menu.title = menu_strings['wcsadmin_management_items_add_menu title']
wcsadmin_management_races_editor_modify_menu.title = menu_strings['wcsadmin_management_races_editor_modify_menu title']
wcsadmin_management_races_editor_modify_from_selection_menu.title = menu_strings['wcsadmin_management_races_editor_modify_from_selection_menu title']
wcsadmin_github_races_menu.title = menu_strings['wcsadmin_github_races_menu title']
wcsadmin_github_races_repository_menu.title = menu_strings['wcsadmin_github_races_repository_menu title']
wcsadmin_github_items_menu.title = menu_strings['wcsadmin_github_items_menu title']
wcsadmin_github_items_repository_menu.title = menu_strings['wcsadmin_github_items_repository_menu title']
wcsadmin_github_info_confirm_commits_menu.title = menu_strings['wcsadmin_github_info_confirm_commits_menu title']
wcsadmin_github_info_commits_menu.title = menu_strings['wcsadmin_github_info_commits_menu title']

wcsadmin_github_races_menu._cycle = None
wcsadmin_github_items_menu._cycle = None
wcsadmin_github_info_menu._checking_cycle = None
wcsadmin_github_info_menu._installing_cycle = None


# ============================================================================
# >> MENU FILLER
# ============================================================================
main_menu.extend(
    [
        Text(menu_strings['main_menu title']),
        SimpleOption(1, menu_strings['main_menu line 1'], shopmenu_menu),
        SimpleOption(2, menu_strings['main_menu line 2'], shopinfo_menu),
        Text('-------------------'),
        SimpleOption(3, menu_strings['main_menu line 3'], showskills_menu),
        SimpleOption(4, menu_strings['main_menu line 4'], resetskills_menu),
        SimpleOption(5, menu_strings['main_menu line 5'], spendskills_menu),
        Text('-------------------'),
        SimpleOption(6, menu_strings['main_menu line 6'], changerace_menu),
        SimpleOption(7, menu_strings['main_menu line 7'], raceinfo_menu),
        Text('-------------------'),
        SimpleOption(8, menu_strings['main_menu line 8'], playerinfo_menu),
        Text('-------------------'),
        SimpleOption(BUTTON_CLOSE_SLOT, menu_strings['close'], highlight=False)
    ]
)

shopinfo_detail_menu.extend(
    [
        Text(menu_strings['shopinfo_detail_menu title']),
        Text(menu_strings['shopinfo_detail_menu line 1']),
        Text(menu_strings['shopinfo_detail_menu line 2']),
        Text(menu_strings['shopinfo_detail_menu line 3 0']),
        Text(menu_strings['shopinfo_detail_menu line 4 0']),
        Text(' '),
        Text(' '),
        SimpleOption(BUTTON_BACK, menu_strings['back']),
        Text(' '),
        SimpleOption(BUTTON_CLOSE_SLOT, menu_strings['close'], highlight=False)
    ]
)

resetskills_menu.extend(
    [
        Text(menu_strings['resetskills_menu title']),
        Text(menu_strings['resetskills_menu line 1']),
        Text(menu_strings['resetskills_menu line 2']),
        SimpleOption(1, menu_strings['yes']),
        SimpleOption(2, menu_strings['no'], main_menu),
        SimpleOption(BUTTON_BACK, menu_strings['back'], main_menu),
        Text(' '),
        SimpleOption(BUTTON_CLOSE_SLOT, menu_strings['close'], highlight=False)
    ]
)

raceinfo_detail_menu.extend(
    [
        Text(menu_strings['raceinfo_detail_menu title']),
        Text(menu_strings['raceinfo_detail_menu required']),
        Text(menu_strings['raceinfo_detail_menu maximum']),
        Text(menu_strings['raceinfo_detail_menu author']),
        Text(menu_strings['raceinfo_detail_menu public']),
        SimpleOption(1, menu_strings['raceinfo_detail_menu skills'], raceinfo_skills_menu),
        SimpleOption(2, menu_strings['raceinfo_detail_menu description'], raceinfo_race_detail_menu),
        SimpleOption(3, menu_strings['raceinfo_detail_menu back'], -1),
        SimpleOption(4, menu_strings['raceinfo_detail_menu next'], 1),
        SimpleOption(BUTTON_BACK, menu_strings['back'], raceinfo_menu),
        Text(' '),
        SimpleOption(BUTTON_CLOSE_SLOT, menu_strings['close'], highlight=False)
    ]
)

raceinfo_skills_detail_menu.extend(
    [
        Text(menu_strings['raceinfo_skills_detail_menu title']),
        Text(menu_strings['raceinfo_skills_detail_menu description']),
        SimpleOption(BUTTON_BACK, menu_strings['back'], raceinfo_skills_menu),
        Text(' '),
        SimpleOption(BUTTON_CLOSE_SLOT, menu_strings['close'], highlight=False)
    ]
)

raceinfo_race_detail_menu.extend(
    [
        Text(menu_strings['raceinfo_race_detail_menu title']),
        Text(' '),
        SimpleOption(BUTTON_BACK, menu_strings['back'], raceinfo_detail_menu),
        Text(' '),
        SimpleOption(BUTTON_CLOSE_SLOT, menu_strings['close'], highlight=False)
    ]
)

playerinfo_menu.extend(
    [
        Text(menu_strings['playerinfo_menu online']),
        Text(menu_strings['playerinfo_menu offline']),
    ]
)

playerinfo_detail_menu.extend(
    [
        Text(menu_strings['playerinfo_detail_menu title']),
        Text(menu_strings['playerinfo_detail_menu line 1']),
        Text(menu_strings['playerinfo_detail_menu line 2']),
        Text(menu_strings['playerinfo_detail_menu line 3']),
        Text(menu_strings['playerinfo_detail_menu line 4']),
        Text(menu_strings['playerinfo_detail_menu line 5']),
        Text(menu_strings['playerinfo_detail_menu line 6']),
        SimpleOption(1, menu_strings['playerinfo_detail_menu line 7'], playerinfo_detail_skills_menu),
        SimpleOption(2, menu_strings['playerinfo_detail_menu line 8'], playerinfo_detail_stats_menu),
        SimpleOption(BUTTON_BACK, menu_strings['back'], playerinfo_menu),
        Text(' '),
        SimpleOption(BUTTON_CLOSE_SLOT, menu_strings['close'], highlight=False)
    ]
)

playerinfo_detail_stats_menu.extend(
    [
        Text(menu_strings['playerinfo_detail_stats_menu title']),
        Text(' '),
        Text(menu_strings['playerinfo_detail_stats_menu line 1']),
        Text(menu_strings['playerinfo_detail_stats_menu line 2']),
        Text(menu_strings['playerinfo_detail_stats_menu line 3']),
        Text(menu_strings['playerinfo_detail_stats_menu line 4']),
        Text(menu_strings['playerinfo_detail_stats_menu line 5']),
        Text(' '),
        Text(' '),
        SimpleOption(BUTTON_BACK, menu_strings['back'], playerinfo_detail_menu),
        Text(' '),
        SimpleOption(BUTTON_CLOSE_SLOT, menu_strings['close'], highlight=False)
    ]
)

wcstop_detail_menu.extend(
    [
        Text(menu_strings['wcstop_detail_menu title']),
        Text(' '),
        Text(menu_strings['wcstop_detail_menu line 1']),
        Text(menu_strings['wcstop_detail_menu line 2']),
        Text(menu_strings['wcstop_detail_menu line 3']),
        Text(' '),
        Text(' '),
        Text(' '),
        SimpleOption(BUTTON_BACK, menu_strings['back'], wcstop_menu),
        Text(' '),
        SimpleOption(BUTTON_CLOSE_SLOT, menu_strings['close'], highlight=False)
    ]
)

wcshelp_menu.extend(
    [
        Text(menu_strings['wcshelp_menu title']),
        Text(menu_strings['wcshelp_menu line 1']),
        Text(menu_strings['wcshelp_menu line 2']),
        Text(menu_strings['wcshelp_menu line 3']),
        Text(menu_strings['wcshelp_menu line 4']),
        Text(menu_strings['wcshelp_menu line 5']),
        Text(menu_strings['wcshelp_menu line 6']),
        Text(menu_strings['wcshelp_menu line 7']),
        Text(menu_strings['wcshelp_menu line 8']),
        Text(menu_strings['wcshelp_menu line 9']),
        Text(menu_strings['wcshelp_menu line 10']),
        Text(menu_strings['wcshelp_menu line 11']),
        Text(menu_strings['wcshelp_menu line 12']),
        Text(menu_strings['wcshelp_menu line 13']),
        SimpleOption(BUTTON_CLOSE_SLOT, menu_strings['close'], highlight=False)
    ]
)

welcome_menu.extend(
    [
        Text(menu_strings['welcome_menu title']),
        Text(' '),
        SimpleOption(1, menu_strings['welcome_menu line 1']),
        Text(menu_strings['welcome_menu line 2']),
        Text(menu_strings['welcome_menu line 3']),
        Text(menu_strings['welcome_menu line 4']),
        Text(' '),
        SimpleOption(2, menu_strings['welcome_menu line 5']),
        Text(menu_strings['welcome_menu line 6']),
        Text(menu_strings['welcome_menu line 7']),
        Text(menu_strings['welcome_menu line 8']),
        Text(menu_strings['welcome_menu line 9']),
        Text(' '),
        SimpleOption(3, menu_strings['welcome_menu line 10']),
        Text(' '),
        SimpleOption(BUTTON_CLOSE_SLOT, menu_strings['welcome_menu line 11']),
    ]
)

input_menu.extend(
    [
        Text(menu_strings['input_menu title']),
        Text(menu_strings['input_menu timeleft']),
        SimpleOption(BUTTON_CLOSE_SLOT, menu_strings['cancel']),
    ]
)


# ============================================================================
# >> ADMIN MENU FILLER
# ============================================================================
wcsadmin_menu.extend(
    [
        Text(menu_strings['wcsadmin_menu title']),
        Text(' '),
        SimpleOption(1, menu_strings['wcsadmin_menu players'], wcsadmin_players_menu),
        SimpleOption(2, menu_strings['wcsadmin_menu management'], wcsadmin_management_menu),
        SimpleOption(3, menu_strings['wcsadmin_menu github'], wcsadmin_github_menu),
        Text(' '),
        Text(' '),
        Text(' '),
        Text(' '),
        Text(' '),
        SimpleOption(BUTTON_CLOSE_SLOT, menu_strings['close'], highlight=False)
    ]
)

wcsadmin_players_menu.extend(
    [
        PagedOption(menu_strings['wcsadmin_players_menu all']),
        Text(menu_strings['wcsadmin_players_menu online']),
        Text(menu_strings['wcsadmin_players_menu offline']),
    ]
)

wcsadmin_players_sub_menu.extend(
    [
        Text(menu_strings['wcsadmin_players_sub_menu title']),
        Text(' '),
        SimpleOption(1, menu_strings['wcsadmin_players_sub_menu line 1'], wcsadmin_players_sub_xp_menu),
        SimpleOption(2, menu_strings['wcsadmin_players_sub_menu line 2'], wcsadmin_players_sub_levels_menu),
        SimpleOption(3, menu_strings['wcsadmin_players_sub_menu line 3'], selectable=False, highlight=False),
        Text(' '),
        Text(' '),
        Text(' '),
        SimpleOption(BUTTON_BACK, menu_strings['back'], wcsadmin_players_menu),
        Text(' '),
        SimpleOption(BUTTON_CLOSE_SLOT, menu_strings['close'], highlight=False)
    ]
)

wcsadmin_players_sub_xp_menu.extend(
    [
        Text(menu_strings['wcsadmin_players_sub_xp_menu title']),
        Text(' '),
        SimpleOption(1, deepcopy(menu_strings['wcsadmin_players_sub_xp_menu line']), 1),
        SimpleOption(2, deepcopy(menu_strings['wcsadmin_players_sub_xp_menu line']), 10),
        SimpleOption(3, deepcopy(menu_strings['wcsadmin_players_sub_xp_menu line']), 100),
        SimpleOption(4, deepcopy(menu_strings['wcsadmin_players_sub_xp_menu line']), 1000),
        SimpleOption(5, deepcopy(menu_strings['wcsadmin_players_sub_xp_menu line']), 10000),
        SimpleOption(6, menu_strings['wcsadmin_players_sub_xp_menu custom']),
        SimpleOption(BUTTON_BACK, menu_strings['back'], wcsadmin_players_sub_menu),
        Text(' '),
        SimpleOption(BUTTON_CLOSE_SLOT, menu_strings['close'], highlight=False)
    ]
)

wcsadmin_players_sub_levels_menu.extend(
    [
        Text(menu_strings['wcsadmin_players_sub_levels_menu title']),
        Text(' '),
        SimpleOption(1, deepcopy(menu_strings['wcsadmin_players_sub_levels_menu line']), 1),
        SimpleOption(2, deepcopy(menu_strings['wcsadmin_players_sub_levels_menu line']), 10),
        SimpleOption(3, deepcopy(menu_strings['wcsadmin_players_sub_levels_menu line']), 100),
        SimpleOption(4, deepcopy(menu_strings['wcsadmin_players_sub_levels_menu line']), 1000),
        SimpleOption(5, deepcopy(menu_strings['wcsadmin_players_sub_levels_menu line']), 10000),
        SimpleOption(6, menu_strings['wcsadmin_players_sub_levels_menu custom']),
        SimpleOption(BUTTON_BACK, menu_strings['back'], wcsadmin_players_sub_menu),
        Text(' '),
        SimpleOption(BUTTON_CLOSE_SLOT, menu_strings['close'], highlight=False)
    ]
)

wcsadmin_management_menu.extend(
    [
        Text(menu_strings['wcsadmin_management_menu title']),
        Text(' '),
        SimpleOption(1, menu_strings['wcsadmin_management_menu races'], wcsadmin_management_races_menu),
        SimpleOption(2, menu_strings['wcsadmin_management_menu items'], wcsadmin_management_items_menu),
        Text(' '),
        Text(' '),
        Text(' '),
        Text(' '),
        SimpleOption(BUTTON_BACK, menu_strings['back'], wcsadmin_menu),
        Text(' '),
        SimpleOption(BUTTON_CLOSE_SLOT, menu_strings['close'], highlight=False)
    ]
)

wcsadmin_management_races_editor_menu.extend(
    [
        Text(menu_strings['wcsadmin_management_races_editor_menu title']),
        Text(' '),
        SimpleOption(1, menu_strings['wcsadmin_management_races_editor_menu toggle 0']),
        SimpleOption(2, menu_strings['wcsadmin_management_races_editor_menu remove']),
        SimpleOption(3, menu_strings['wcsadmin_management_races_editor_menu modify'], wcsadmin_management_races_editor_modify_menu),
        Text(' '),
        Text(' '),
        Text(' '),
        SimpleOption(BUTTON_BACK, menu_strings['back'], wcsadmin_management_races_menu),
        Text(' '),
        SimpleOption(BUTTON_CLOSE_SLOT, menu_strings['close'], highlight=False)
    ]
)

wcsadmin_management_items_editor_menu.extend(
    [
        Text(menu_strings['wcsadmin_management_items_editor_menu title']),
        Text(' '),
        SimpleOption(1, menu_strings['wcsadmin_management_items_editor_menu toggle 0']),
        SimpleOption(2, menu_strings['wcsadmin_management_items_editor_menu remove']),
        Text(' '),
        Text(' '),
        Text(' '),
        Text(' '),
        SimpleOption(BUTTON_BACK, menu_strings['back'], wcsadmin_management_items_menu),
        Text(' '),
        SimpleOption(BUTTON_CLOSE_SLOT, menu_strings['close'], highlight=False)
    ]
)

wcsadmin_management_races_editor_modify_menu.extend(
    [
        PagedOption(menu_strings['wcsadmin_management_races_editor_modify_menu line 1'], _request_required),
        PagedOption(menu_strings['wcsadmin_management_races_editor_modify_menu line 2'], _request_maximum),
        PagedOption(menu_strings['wcsadmin_management_races_editor_modify_menu line 3'], 'restrictmap'),
        PagedOption(menu_strings['wcsadmin_management_races_editor_modify_menu line 4'], 'restrictitem'),
        PagedOption(menu_strings['wcsadmin_management_races_editor_modify_menu line 5'], 'restrictweapon'),
        PagedOption(menu_strings['wcsadmin_management_races_editor_modify_menu line 6'], wcsadmin_management_races_editor_modify_restricted_team_menu),
        PagedOption(menu_strings['wcsadmin_management_races_editor_modify_menu line 7'], _request_team_limit),
        PagedOption(menu_strings['wcsadmin_management_races_editor_modify_menu line 8'], 'allowonly'),
        PagedOption(menu_strings['wcsadmin_management_races_editor_modify_menu line 9'], selectable=False, highlight=False)
    ]
)

wcsadmin_management_races_editor_modify_from_selection_menu.extend(
    [
        PagedOption(menu_strings['wcsadmin_management_races_editor_modify_from_selection_menu line'])
    ]
)

wcsadmin_management_races_editor_modify_restricted_team_menu.extend(
    [
        Text(menu_strings['wcsadmin_management_races_editor_modify_restricted_team_menu title']),
        Text(' '),
        Text(menu_strings['wcsadmin_management_races_editor_modify_restricted_team_menu line 1']),
        SimpleOption(1, menu_strings['wcsadmin_management_races_editor_modify_restricted_team_menu 0'], 0),
        SimpleOption(2, menu_strings['wcsadmin_management_races_editor_modify_restricted_team_menu 2'], 2),
        SimpleOption(3, menu_strings['wcsadmin_management_races_editor_modify_restricted_team_menu 3'], 3),
        Text(' '),
        Text(' '),
        Text(' '),
        SimpleOption(BUTTON_BACK, menu_strings['back'], wcsadmin_management_races_editor_modify_menu),
        Text(' '),
        SimpleOption(BUTTON_CLOSE_SLOT, menu_strings['close'], highlight=False)
    ]
)

wcsadmin_github_menu.extend(
    [
        Text(menu_strings['wcsadmin_github_menu title']),
        Text(' '),
        SimpleOption(1, menu_strings['wcsadmin_github_menu races'], wcsadmin_github_races_menu),
        SimpleOption(2, menu_strings['wcsadmin_github_menu items'], wcsadmin_github_items_menu),
        SimpleOption(3, menu_strings['wcsadmin_github_menu info'], wcsadmin_github_info_menu),
        Text(' '),
        Text(' '),
        Text(' '),
        SimpleOption(BUTTON_BACK, menu_strings['back'], wcsadmin_menu),
        Text(' '),
        SimpleOption(BUTTON_CLOSE_SLOT, menu_strings['close'], highlight=False)
    ]
)

wcsadmin_github_races_options_menu.extend(
    [
        Text(menu_strings['wcsadmin_github_options_menu title']),
        Text(' '),
        SimpleOption(1, menu_strings['wcsadmin_github_options_menu install'], GithubStatus.INSTALLING),
        SimpleOption(2, menu_strings['wcsadmin_github_options_menu update'], GithubStatus.UPDATING),
        SimpleOption(3, menu_strings['wcsadmin_github_options_menu uninstall'], GithubStatus.UNINSTALLING),
        Text(menu_strings['wcsadmin_github_options_menu status 4']),
        Text(menu_strings['wcsadmin_github_options_menu last updated']),
        Text(menu_strings['wcsadmin_github_options_menu last modified']),
        SimpleOption(BUTTON_BACK, menu_strings['back'], wcsadmin_github_races_menu),
        Text(' '),
        SimpleOption(BUTTON_CLOSE_SLOT, menu_strings['close'], highlight=False)
    ]
)

wcsadmin_github_items_options_menu.extend(
    [
        Text(menu_strings['wcsadmin_github_options_menu title']),
        Text(' '),
        SimpleOption(1, menu_strings['wcsadmin_github_options_menu install'], GithubStatus.INSTALLING),
        SimpleOption(2, menu_strings['wcsadmin_github_options_menu update'], GithubStatus.UPDATING),
        SimpleOption(3, menu_strings['wcsadmin_github_options_menu uninstall'], GithubStatus.UNINSTALLING),
        Text(menu_strings['wcsadmin_github_options_menu status 4']),
        Text(menu_strings['wcsadmin_github_options_menu last updated']),
        Text(menu_strings['wcsadmin_github_options_menu last modified']),
        SimpleOption(BUTTON_BACK, menu_strings['back'], wcsadmin_github_items_menu),
        Text(' '),
        SimpleOption(BUTTON_CLOSE_SLOT, menu_strings['close'], highlight=False)
    ]
)

wcsadmin_github_info_menu.extend(
    [
        Text(menu_strings['wcsadmin_github_info_menu title']),
        Text(' '),
        Text(menu_strings['wcsadmin_github_info_menu version']),
        SimpleOption(1, menu_strings['wcsadmin_github_info_menu check']),
        Text(' '),
        SimpleOption(3, menu_strings['wcsadmin_github_info_menu commits'], wcsadmin_github_info_commits_menu),
        Text(' '),
        Text(' '),
        SimpleOption(BUTTON_BACK, menu_strings['back'], wcsadmin_github_menu),
        Text(' '),
        SimpleOption(BUTTON_CLOSE_SLOT, menu_strings['close'], highlight=False)
    ]
)

wcsadmin_github_info_confirm_menu.extend(
    [
        Text(menu_strings['wcsadmin_github_info_confirm_menu title']),
        Text(' '),
        Text(menu_strings['wcsadmin_github_info_confirm_menu line 1']),
        Text(menu_strings['wcsadmin_github_info_confirm_menu line 2']),
        SimpleOption(1, menu_strings['yes']),
        SimpleOption(2, menu_strings['no'], wcsadmin_github_info_menu),
        SimpleOption(3, menu_strings['wcsadmin_github_info_confirm_menu line 3'], wcsadmin_github_info_confirm_commits_menu),
        Text(' '),
        SimpleOption(BUTTON_BACK, menu_strings['back'], wcsadmin_github_info_menu),
        Text(' '),
        SimpleOption(BUTTON_CLOSE_SLOT, menu_strings['close'], highlight=False)
    ]
)


# ============================================================================
# >> MENU ENHANCEMENTS
# ============================================================================
welcome_menu[3].text.tokens['game'] = 'CS:S' if GAME_NAME == 'cstrike' else 'CS:GO' if GAME_NAME == 'csgo' else GAME_NAME
welcome_menu[15].text.tokens['slot'] = BUTTON_CLOSE_SLOT
wcsadmin_github_info_menu[2].text.tokens['version'] = info.version

if BUTTON_BACK == 8:
    wcsadmin_menu.insert(-3, Text(' '))
    wcsadmin_players_sub_menu.insert(-3, Text(' '))
    wcsadmin_players_sub_xp_menu.insert(-3, Text(' '))
    wcsadmin_players_sub_levels_menu.insert(-3, Text(' '))
    wcsadmin_management_menu.insert(-3, Text(' '))
    wcsadmin_management_races_editor_menu.insert(-3, Text(' '))
    wcsadmin_management_items_editor_menu.insert(-3, Text(' '))
    wcsadmin_github_menu.insert(-3, Text(' '))
    wcsadmin_github_races_options_menu.insert(-3, Text(' '))
    wcsadmin_github_items_options_menu.insert(-3, Text(' '))
    wcsadmin_github_info_menu.insert(-3, Text(' '))
    wcsadmin_github_info_confirm_menu.insert(-3, Text(' '))


for i in range(2, 7):
    wcsadmin_players_sub_xp_menu[i].text.tokens['value'] = wcsadmin_players_sub_xp_menu[i].value
    wcsadmin_players_sub_levels_menu[i].text.tokens['value'] = wcsadmin_players_sub_levels_menu[i].value


# ============================================================================
# >> LISTENERS
# ============================================================================
@OnGithubCommitsRefresh
def on_github_commits_refresh():
    wcsadmin_github_info_commits_menu.clear()

    wcsadmin_github_info_commits_menu._cycle = 0
    wcsadmin_github_info_commits_menu.append(menu_strings['wcsadmin_github_info_commits_menu querying'])

    for index in wcsadmin_github_info_commits_menu._player_pages:
        if wcsadmin_github_info_commits_menu.is_active_menu(index):
            wcsadmin_github_info_commits_menu._refresh(index)


@OnGithubCommitsRefreshed
def on_github_commits_refreshed(commits):
    wcsadmin_github_info_commits_menu._cycle = None
    wcsadmin_github_info_commits_menu.clear()

    for commit in commits:
        menu = PagedMenu(title=menu_strings['wcsadmin_github_info_commits_detail_menu title'], parent_menu=wcsadmin_github_info_commits_menu)
        menu.append(Text(deepcopy(menu_strings['wcsadmin_github_info_commits_detail_menu line 1'])))
        menu.append(Text(deepcopy(menu_strings['wcsadmin_github_info_commits_detail_menu line 2'])))
        menu.append(Text(menu_strings['wcsadmin_github_info_commits_detail_menu line 3']))

        menu[0].text.tokens['name'] = commit['author']
        menu[1].text.tokens['date'] = commit['date']

        for message in commit['messages'].splitlines():
            for text in wrap('   ' + message, 50):
                menu.append(Text(text))

        wcsadmin_github_info_commits_menu.append(PagedOption(commit['date'], value=menu))

    for index in wcsadmin_github_info_commits_menu._player_pages:
        if wcsadmin_github_info_commits_menu.is_active_menu(index):
            wcsadmin_github_info_commits_menu._refresh(index)


@OnGithubModulesRefresh
def on_github_modules_refresh():
    wcsadmin_github_races_menu.clear()
    wcsadmin_github_items_menu.clear()

    wcsadmin_github_races_menu._cycle = 0
    wcsadmin_github_items_menu._cycle = 0
    wcsadmin_github_races_menu.append(menu_strings['wcsadmin_github_races_menu querying'])
    wcsadmin_github_items_menu.append(menu_strings['wcsadmin_github_items_menu querying'])

    for index in wcsadmin_github_races_menu._player_pages:
        if wcsadmin_github_races_menu.is_active_menu(index):
            wcsadmin_github_races_menu._refresh(index)

    for index in wcsadmin_github_items_menu._player_pages:
        if wcsadmin_github_items_menu.is_active_menu(index):
            wcsadmin_github_items_menu._refresh(index)


@OnGithubModulesRefreshed
def on_github_modules_refreshed(races, items):
    wcsadmin_github_races_menu.clear()
    wcsadmin_github_items_menu.clear()
    wcsadmin_github_races_menu._cycle = None
    wcsadmin_github_items_menu._cycle = None

    for name, data in races.items():
        option = PagedOption(name, name)
        repository = data['repository']

        if repository is None or data['last_updated'] is None:
            option.text = f'+{option.text}'
        else:
            if data['last_updated'] < data['repositories'][repository]['last_modified']:
                option.text = f'*{option.text}'

        wcsadmin_github_races_menu.append(option)

    for name, data in items.items():
        option = PagedOption(name, name)
        repository = data['repository']

        if repository is None or data['last_updated'] is None:
            option.text = f'+{option.text}'
        else:
            if data['last_updated'] < data['repositories'][repository]['last_modified']:
                option.text = f'*{option.text}'

        wcsadmin_github_items_menu.append(option)

    wcsadmin_github_menu[2].selectable = wcsadmin_github_menu[2].highlight = bool(races)
    wcsadmin_github_menu[3].selectable = wcsadmin_github_menu[3].highlight = bool(items)

    if not races:
        wcsadmin_github_menu.send([*wcsadmin_github_races_menu._player_pages])

        wcsadmin_github_races_menu.close([*wcsadmin_github_races_menu._player_pages])

    if not items:
        wcsadmin_github_menu.send([*wcsadmin_github_items_menu._player_pages])

        wcsadmin_github_items_menu.close([*wcsadmin_github_items_menu._player_pages])


@OnGithubModuleInstalled
def on_github_module_installed(repository, module, name, userid):
    _update_menu(module, name, True)


@OnGithubModuleUpdated
def on_github_module_updated(repository, module, name, userid):
    _update_menu(module, name, True)


@OnGithubModuleUninstalled
def on_github_module_uninstalled(repository, module, name, userid):
    _update_menu(module, name, False)


@OnGithubNewVersionChecked
def on_github_new_version_checked(version, commits):
    wcsadmin_github_info_menu._checking_cycle = None
    wcsadmin_github_info_menu[3] = SimpleOption(1, menu_strings['wcsadmin_github_info_menu check'])

    wcsadmin_github_info_confirm_commits_menu.clear()

    if version is None:
        wcsadmin_github_info_menu[4] = Text(' ')
        wcsadmin_github_info_confirm_menu[2].text.tokens['version'] = ''
    else:
        wcsadmin_github_info_menu[4] = SimpleOption(2, menu_strings['wcsadmin_github_info_menu update'])
        wcsadmin_github_info_menu[4].text.tokens['version'] = version
        wcsadmin_github_info_confirm_menu[2].text.tokens['version'] = version

        for commit in commits:
            menu = PagedMenu(title=menu_strings['wcsadmin_github_info_commits_detail_menu title'], parent_menu=wcsadmin_github_info_confirm_commits_menu)
            menu.append(Text(deepcopy(menu_strings['wcsadmin_github_info_commits_detail_menu line 1'])))
            menu.append(Text(deepcopy(menu_strings['wcsadmin_github_info_commits_detail_menu line 2'])))
            menu.append(Text(menu_strings['wcsadmin_github_info_commits_detail_menu line 3']))

            menu[0].text.tokens['name'] = commit['author']
            menu[1].text.tokens['date'] = commit['date']

            for message in commit['messages'].splitlines():
                for text in wrap('   ' + message, 50):
                    menu.append(Text(text))

            wcsadmin_github_info_confirm_commits_menu.append(PagedOption(commit['date'], value=menu))

        for index in wcsadmin_github_info_confirm_commits_menu._player_pages:
            if wcsadmin_github_info_confirm_commits_menu.is_active_menu(index):
                wcsadmin_github_info_confirm_commits_menu._refresh(index)


@OnGithubNewVersionInstalled
def on_github_new_version_installed():
    wcsadmin_github_info_menu._installing_cycle = None
    wcsadmin_github_info_menu[3] = SimpleOption(1, menu_strings['wcsadmin_github_info_menu check'])
    wcsadmin_github_info_menu[4] = Text(' ')


@OnPlayerQuery
def on_player_query(wcsplayer):
    for index in playerinfo_detail_menu._player_pages:
        if playerinfo_detail_menu.is_active_menu(index):
            playerinfo_detail_menu._refresh(index)


# ============================================================================
# >> FUNCTIONS
# ============================================================================
def _update_menu(module, name, updated):
    menu = wcsadmin_github_races_menu if module == 'races' else wcsadmin_github_items_menu

    for option in menu:
        if option.value == name:
            option.text = ('' if updated else '+') + name

            break

    for index in menu._player_pages:
        if menu.is_active_menu(index):
            menu._refresh(index)
