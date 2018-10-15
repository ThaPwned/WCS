# ../wcs/core/menus/menus.py

# ============================================================================
# >> IMPORTS
# ============================================================================
# Python Imports
#   Time
from time import time

# Source.Python Imports
#   Menus
from menus import PagedOption
from menus import SimpleOption
from menus import Text
from menus.radio import BUTTON_BACK
from menus.radio import BUTTON_CLOSE_SLOT

# WCS Imports
#   Constants
from ..constants import GithubStatus
#   Listeners
from ..listeners import OnGithubRefresh
from ..listeners import OnGithubRefreshed
from ..listeners import OnGithubInstalled
from ..listeners import OnGithubUpdated
from ..listeners import OnGithubUninstalled
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
from . import raceinfo_menu
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
from . import wcsadmin_menu
from . import wcsadmin_management_menu
from . import wcsadmin_management_races_menu
from . import wcsadmin_management_items_menu
from . import wcsadmin_management_races_add_menu
from . import wcsadmin_management_items_add_menu
from . import wcsadmin_management_races_editor_menu
from . import wcsadmin_management_items_editor_menu
from . import wcsadmin_github_menu
from . import wcsadmin_github_races_menu
from . import wcsadmin_github_items_menu
from . import wcsadmin_github_options_menu
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
raceinfo_menu.title = menu_strings['raceinfo_menu title']
raceinfo_skills_menu.title = menu_strings['raceinfo_skills_menu title']
playerinfo_menu.title = menu_strings['playerinfo_menu title']
playerinfo_detail_skills_menu.title = menu_strings['playerinfo_detail_skills_menu title']
wcstop_menu.title = menu_strings['wcstop_menu title']
wcsadmin_management_races_menu.title = menu_strings['wcsadmin_management_races_menu title']
wcsadmin_management_items_menu.title = menu_strings['wcsadmin_management_items_menu title']
wcsadmin_management_races_add_menu.title = menu_strings['wcsadmin_management_races_add_menu title']
wcsadmin_management_items_add_menu.title = menu_strings['wcsadmin_management_items_add_menu title']
wcsadmin_github_races_menu.title = menu_strings['wcsadmin_github_races_menu title']
wcsadmin_github_items_menu.title = menu_strings['wcsadmin_github_items_menu title']


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
        Text('-' * 25),
        Text(menu_strings['playerinfo_detail_menu line 1']),
        Text(menu_strings['playerinfo_detail_menu line 2']),
        Text(menu_strings['playerinfo_detail_menu line 3']),
        Text(menu_strings['playerinfo_detail_menu line 4']),
        Text(menu_strings['playerinfo_detail_menu line 5']),
        Text(menu_strings['playerinfo_detail_menu line 6']),
        Text('-' * 25),
        SimpleOption(1, menu_strings['playerinfo_detail_menu line 7'], playerinfo_detail_skills_menu),
        SimpleOption(2, menu_strings['playerinfo_detail_menu line 8'], playerinfo_detail_stats_menu),
        Text('-' * 25),
        SimpleOption(BUTTON_BACK, menu_strings['back'], playerinfo_menu),
        Text(' '),
        SimpleOption(BUTTON_CLOSE_SLOT, menu_strings['close'], highlight=False)
    ]
)

playerinfo_detail_stats_menu.extend(
    [
        Text(menu_strings['playerinfo_detail_stats_menu title']),
        Text('-' * 25),
        Text(menu_strings['playerinfo_detail_stats_menu line 1']),
        Text(menu_strings['playerinfo_detail_stats_menu line 2']),
        Text(menu_strings['playerinfo_detail_stats_menu line 3']),
        Text(menu_strings['playerinfo_detail_stats_menu line 4']),
        Text(menu_strings['playerinfo_detail_stats_menu line 5']),
        Text('-' * 25),
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

welcome_menu[15].text.tokens['slot'] = BUTTON_CLOSE_SLOT


# ============================================================================
# >> ADMIN MENU FILLER
# ============================================================================
wcsadmin_menu.extend(
    [
        Text(menu_strings['wcsadmin_menu title']),
        Text(' '),
        SimpleOption(1, menu_strings['wcsadmin_menu management'], wcsadmin_management_menu),
        SimpleOption(2, menu_strings['wcsadmin_menu github'], wcsadmin_github_menu),
        Text(' '),
        Text(' '),
        Text(' '),
        Text(' '),
        Text(' '),
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
        Text(' '),
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

wcsadmin_github_menu.extend(
    [
        Text(menu_strings['wcsadmin_github_menu title']),
        Text(' '),
        SimpleOption(1, menu_strings['wcsadmin_github_menu races'], wcsadmin_github_races_menu, selectable=False, highlight=False),
        SimpleOption(2, menu_strings['wcsadmin_github_menu items'], wcsadmin_github_items_menu, selectable=False, highlight=False),
        Text(' '),
        Text(' '),
        Text(' '),
        Text(' '),
        SimpleOption(BUTTON_BACK, menu_strings['back'], wcsadmin_menu),
        Text(' '),
        SimpleOption(BUTTON_CLOSE_SLOT, menu_strings['close'], highlight=False)
    ]
)

wcsadmin_github_options_menu.extend(
    [
        Text(menu_strings['wcsadmin_github_options_menu title']),
        Text(' '),
        SimpleOption(1, menu_strings['wcsadmin_github_options_menu install'], GithubStatus.INSTALLING),
        SimpleOption(2, menu_strings['wcsadmin_github_options_menu update'], GithubStatus.UPDATING),
        SimpleOption(3, menu_strings['wcsadmin_github_options_menu uninstall'], GithubStatus.UNINSTALLING),
        Text(menu_strings['wcsadmin_github_options_menu status 4']),
        Text(menu_strings['wcsadmin_github_options_menu last updated']),
        Text(menu_strings['wcsadmin_github_options_menu last modified']),
        SimpleOption(BUTTON_BACK, menu_strings['back']),
        Text(' '),
        SimpleOption(BUTTON_CLOSE_SLOT, menu_strings['close'], highlight=False)
    ]
)


# ============================================================================
# >> LISTENERS
# ============================================================================
@OnGithubRefresh
def on_github_refresh():
    wcsadmin_github_races_menu.clear()
    wcsadmin_github_items_menu.clear()

    wcsadmin_github_menu.send(set([*wcsadmin_github_races_menu._player_pages] + [*wcsadmin_github_items_menu._player_pages]))

    wcsadmin_github_races_menu.close([*wcsadmin_github_races_menu._player_pages])
    wcsadmin_github_items_menu.close([*wcsadmin_github_items_menu._player_pages])


@OnGithubRefreshed
def on_github_refreshed(races, items):
    for name, data in races.items():
        option = PagedOption(name, name)

        if data['last_updated'] is None:
            option.text = f'+{option.text}'
        else:
            if data['last_updated'] < data['last_modified']:
                option.text = f'*{option.text}'

        wcsadmin_github_races_menu.append(option)

    for name, data in items.items():
        option = PagedOption(name, name)

        if data['last_updated'] is None:
            option.text = f'+{option.text}'
        else:
            if data['last_updated'] < data['last_modified']:
                option.text = f'*{option.text}'

        wcsadmin_github_items_menu.append(option)

    wcsadmin_github_menu[2].selectable = wcsadmin_github_menu[2].highlight = bool(races)
    wcsadmin_github_menu[3].selectable = wcsadmin_github_menu[3].highlight = bool(items)


@OnGithubInstalled
def on_github_installed(module, name, userid):
    _update_menu(module, name, time())


@OnGithubUpdated
def on_github_updated(module, name, userid):
    _update_menu(module, name, time())


@OnGithubUninstalled
def on_github_uninstalled(module, name, userid):
    _update_menu(module, name, None)


@OnPlayerQuery
def on_player_query(wcsplayer):
    for index in playerinfo_detail_menu._player_pages:
        if playerinfo_detail_menu.is_active_menu(index):
            playerinfo_detail_menu._refresh(index)


# ============================================================================
# >> FUNCTIONS
# ============================================================================
def _update_menu(module, name, now):
    from ..helpers.github import github_manager

    menu = wcsadmin_github_races_menu if module == 'races' else wcsadmin_github_items_menu

    for option in menu:
        if option.value == name:
            github_manager[module][name]['last_updated'] = now

            option.text = ('+' if now is None else '') + name

            break

    for index in menu._player_pages:
        if menu.is_active_menu(index):
            menu._refresh(index)
