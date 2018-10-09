# ../wcs/core/menus/select.py

# ============================================================================
# >> IMPORTS
# ============================================================================
# Python Imports
#   JSON
from json import dump
from json import load

# Source.Python Imports
#   Menus
from menus import PagedMenu
from menus import PagedOption
from menus.radio import BUTTON_BACK
from menus.radio import MAX_ITEM_COUNT
#   Players
from players.helpers import userid_from_index

# WCS Imports
#   Constants
from ..constants import IS_GITHUB_ENABLED
from ..constants import GithubStatus
from ..constants import ItemReason
from ..constants import RaceReason
from ..constants.paths import CFG_PATH
#   Helpers
from ..helpers.overwrites import SayText2
#   Menus
from . import main_menu
from . import shopmenu_menu
from . import shopinfo_menu
from . import shopinfo_detail_menu
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
from . import playerinfo_detail_stats_menu
from . import wcstop_menu
from . import wcstop_detail_menu
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
#   Modules
from ..modules.items.manager import item_manager
from ..modules.races.manager import race_manager
#   Players
from ..players.entity import Player
#   Translations
from ..translations import chat_strings

# Is Github available?
if IS_GITHUB_ENABLED:
    #   Helpers
    from ..helpers.github import github_manager


# ============================================================================
# >> ALL DECLARATION
# ============================================================================
__all__ = ()


# ============================================================================
# >> GLOBAL VARIABLES
# ============================================================================
skills_reset_message = SayText2(chat_strings['skills reset'])
changerace_message = SayText2(chat_strings['changerace'])
skill_upgrade_message = SayText2(chat_strings['skill upgrade'])
item_bought_message = SayText2(chat_strings['item bought'])
github_installing_message = SayText2(chat_strings['github installing'])
github_updating_message = SayText2(chat_strings['github updating'])
github_uninstalling_message = SayText2(chat_strings['github uninstalling'])


# ============================================================================
# >> SELECT CALLBACKS
# ============================================================================
@main_menu.register_select_callback
def main_menu_select(menu, client, option):
    return option.value


@shopmenu_menu.register_select_callback
def shopmenu_menu_select(menu, client, option):
    wcsplayer = Player.from_index(client)

    if isinstance(option.value, PagedMenu):
        wcsplayer.data['_internal_shopmenu'] = option.value.name

        return option.value

    settings = item_manager[option.value]

    if settings.usable_by(wcsplayer) is ItemReason.ALLOWED:
        wcsplayer.player.cash -= settings.config['cost']

        item_bought_message.send(client, name=settings.strings['name'])

        wcsplayer.items[option.value].count += 1
        wcsplayer.items[option.value].execute('buycmd', define=True)

    return menu


@shopinfo_menu.register_select_callback
def shopinfo_menu_select(menu, client, option):
    wcsplayer = Player.from_index(client)

    if isinstance(option.value, PagedMenu):
        wcsplayer.data['_internal_shopinfo_category'] = option.value

        return option.value

    wcsplayer.data['_internal_shopinfo'] = option.value

    return shopinfo_detail_menu


@shopinfo_detail_menu.register_select_callback
def shopinfo_detail_menu_select(menu, client, option):
    if option.choice_index == BUTTON_BACK:
        wcsplayer = Player.from_index(client)

        return wcsplayer.data['_internal_shopinfo_category']


@resetskills_menu.register_select_callback
def resetskills_menu_select(menu, client, option):
    wcsplayer = Player.from_index(client)

    if option.choice_index == 1:
        unused = 0
        maximum = 0

        for skill in wcsplayer.skills.values():
            unused += skill.level
            skill.level = 0

            maximum += skill.config['maximum']

        unused = wcsplayer.unused = min(wcsplayer.unused + unused, maximum)

        player = wcsplayer.player

        if not player.dead:
            player.client_command('kill', True)

        skills_reset_message.send(client, unused=unused)

        return

    return option.value


@spendskills_menu.register_select_callback
def spendskills_menu_select(menu, client, option):
    race, skill = option.value

    wcsplayer = Player.from_index(client)
    active_race = wcsplayer.active_race

    if not active_race.name == race:
        if active_race.unused > 0:
            if any([skill.level < skill.config['maximum'] for skill in active_race.skills.values()]):
                return menu

        return

    active_race.skills[skill].level += 1
    active_race.unused -= 1

    skill_upgrade_message.send(client, name=active_race.settings.strings[skill], level=active_race.skills[skill].level)

    if active_race.unused > 0:
        if any([skill.level < skill.config['maximum'] for skill in active_race.skills.values()]):
            return menu


@changerace_menu.register_select_callback
def changerace_menu_select(menu, client, option):
    wcsplayer = Player.from_index(client)

    if isinstance(option.value, PagedMenu):
        return option.value

    settings = race_manager[option.value]

    if settings.usable_by(wcsplayer) is RaceReason.ALLOWED:
        changerace_message.send(client, name=settings.strings['name'])

        wcsplayer.current_race = option.value

        player = wcsplayer.player

        if not player.dead:
            player.godmode = False

            player.client_command('kill', True)
    else:
        return menu


@raceinfo_menu.register_select_callback
def raceinfo_menu_select(menu, client, option):
    wcsplayer = Player.from_index(client)

    if isinstance(option.value, PagedMenu):
        wcsplayer.data['_internal_raceinfo_category'] = option.value.name

        return option.value

    wcsplayer.data['_internal_raceinfo'] = option.value

    return raceinfo_detail_menu


@raceinfo_detail_menu.register_select_callback
def raceinfo_detail_menu_select(menu, client, option):
    if option.choice_index in (3, 4, BUTTON_BACK):
        wcsplayer = Player.from_index(client)
        name = wcsplayer.data.get('_internal_raceinfo')
        category = wcsplayer.data.get('_internal_raceinfo_category')

        all_races = race_manager._category_to_values[category]

        if name not in all_races:
            category = None
            all_races = race_manager._category_to_values[None]

        index = all_races.index(name)

        if option.choice_index == BUTTON_BACK:
            if category is None:
                option.value.set_player_page(client, index // MAX_ITEM_COUNT)
                return option.value

            race_manager._info_category_menus[category].set_player_page(client, index // MAX_ITEM_COUNT)

            return race_manager._info_category_menus[category]

        index += option.value

        wcsplayer.data['_internal_raceinfo'] = all_races[index]

        return menu

    return option.value


@raceinfo_skills_menu.register_select_callback
def raceinfo_skills_menu_select(menu, client, option):
    wcsplayer = Player.from_index(client)

    wcsplayer.data['_internal_raceinfo_skill'] = option.value

    return raceinfo_skills_detail_menu


@raceinfo_skills_detail_menu.register_select_callback
def raceinfo_skills_detail_menu_select(menu, client, option):
    return option.value


@raceinfo_race_detail_menu.register_select_callback
def raceinfo_race_detail_menu_select(menu, client, option):
    return option.value


@playerinfo_menu.register_select_callback
def playerinfo_menu_select(menu, client, option):
    wcsplayer = Player.from_index(client)

    wcsplayer.data['_internal_playerinfo'] = option.value
    wcsplayer.data['_internal_playerinfo_name'] = option.text

    return playerinfo_detail_menu


@playerinfo_detail_menu.register_select_callback
def playerinfo_detail_menu_select(menu, client, option):
    return option.value


@playerinfo_detail_stats_menu.register_select_callback
def playerinfo_detail_stats_menu_select(menu, client, option):
    return option.value


@wcstop_menu.register_select_callback
def wcstop_menu_select(menu, client, option):
    wcsplayer = Player.from_index(client)

    wcsplayer.data['_internal_wcstop'] = option.value

    return wcstop_detail_menu


@wcstop_detail_menu.register_select_callback
def wcstop_detail_menu_select(menu, client, option):
    return option.value


# ============================================================================
# >> ADMIN SELECT CALLBACKS
# ============================================================================
@wcsadmin_menu.register_select_callback
def wcsadmin_menu_select(menu, client, option):
    return option.value


@wcsadmin_management_menu.register_select_callback
def wcsadmin_management_menu_select(menu, client, option):
    return option.value


@wcsadmin_management_races_menu.register_select_callback
def wcsadmin_management_races_menu_select(menu, client, option):
    wcsplayer = Player.from_index(client)

    if isinstance(option.value, str):
        wcsplayer.data['_internal_wcsadmin_editor_value'] = option.value

        return wcsadmin_management_races_editor_menu

    return wcsadmin_management_races_add_menu


@wcsadmin_management_items_menu.register_select_callback
def wcsadmin_management_items_menu_select(menu, client, option):
    wcsplayer = Player.from_index(client)

    if isinstance(option.value, str):
        wcsplayer.data['_internal_wcsadmin_editor_value'] = option.value

        return wcsadmin_management_items_editor_menu

    return wcsadmin_management_items_add_menu


@wcsadmin_management_races_add_menu.register_select_callback
def wcsadmin_management_races_add_menu_select(menu, client, option):
    with open(CFG_PATH / 'races.json') as inputfile:
        data = load(inputfile)

    data['races'].append(option.value)

    with open(CFG_PATH / 'races.json', 'w') as outputfile:
        dump(data, outputfile, indent=4)

    menu.remove(option)

    wcsadmin_management_races_menu.append(PagedOption(option.value, option.value))

    if not menu:
        return menu.parent_menu

    return menu


@wcsadmin_management_items_add_menu.register_select_callback
def wcsadmin_management_items_add_menu_select(menu, client, option):
    with open(CFG_PATH / 'items.json') as inputfile:
        data = load(inputfile)

    data['items'].append(option.value)

    with open(CFG_PATH / 'items.json', 'w') as outputfile:
        dump(data, outputfile, indent=4)

    menu.remove(option)

    wcsadmin_management_items_menu.append(PagedOption(option.value, option.value))

    if not menu:
        return menu.parent_menu

    return menu


@wcsadmin_management_races_editor_menu.register_select_callback
def wcsadmin_management_races_editor_menu_select(menu, client, option):
    wcsplayer = Player.from_index(client)

    if option.choice_index == 1:
        value = wcsplayer.data['_internal_wcsadmin_editor_value']

        if value.startswith('_'):
            new_value = value[1:]
        else:
            new_value = '_' + value

        with open(CFG_PATH / 'races.json') as inputfile:
            data = load(inputfile)

        for i, name in enumerate(data['races']):
            if name == value:
                data['races'].pop(i)
                data['races'].insert(i, new_value)
                break

        with open(CFG_PATH / 'races.json', 'w') as outputfile:
            dump(data, outputfile, indent=4)

        wcsplayer.data['_internal_wcsadmin_editor_value'] = new_value

        return menu
    elif option.choice_index == 2:
        value = wcsplayer.data['_internal_wcsadmin_editor_value']

        with open(CFG_PATH / 'races.json') as inputfile:
            data = load(inputfile)

        for i, name in enumerate(data['races']):
            if name == value:
                data['races'].pop(i)
                break

        with open(CFG_PATH / 'races.json', 'w') as outputfile:
            dump(data, outputfile, indent=4)

        return wcsadmin_management_races_menu

    return option.value


@wcsadmin_github_menu.register_select_callback
def wcsadmin_github_menu_select(menu, client, option):
    return option.value


@wcsadmin_github_races_menu.register_select_callback
def wcsadmin_github_races_menu_select(menu, client, option):
    wcsplayer = Player.from_index(client)

    wcsplayer.data['_internal_wcsadmin_github_name'] = option.value
    wcsplayer.data['_internal_wcsadmin_github_module'] = 1

    return wcsadmin_github_options_menu


@wcsadmin_github_items_menu.register_select_callback
def wcsadmin_github_items_menu_select(menu, client, option):
    wcsplayer = Player.from_index(client)

    wcsplayer.data['_internal_wcsadmin_github_name'] = option.value
    wcsplayer.data['_internal_wcsadmin_github_module'] = 0

    return wcsadmin_github_options_menu


@wcsadmin_github_options_menu.register_select_callback
def wcsadmin_github_options_menu_select(menu, client, option):
    wcsplayer = Player.from_index(client)

    if option.choice_index == BUTTON_BACK:
        if wcsplayer.data['_internal_wcsadmin_github_module']:
            return wcsadmin_github_races_menu
        else:
            return wcsadmin_github_items_menu
    elif isinstance(option.value, GithubStatus):
        wcsplayer.data['_internal_wcsadmin_github_cycle'] = 0

        module = 'races' if wcsplayer.data['_internal_wcsadmin_github_module'] else 'items'
        name = wcsplayer.data['_internal_wcsadmin_github_name']

        if option.value is GithubStatus.INSTALLING:
            github_installing_message.send(client, name=name)

            github_manager.install(module, name, userid_from_index(client))
        elif option.value is GithubStatus.UPDATING:
            github_updating_message.send(client, name=name)

            github_manager.update(module, name, userid_from_index(client))
        else:
            github_uninstalling_message.send(client, name=name)

            github_manager.uninstall(module, name, userid_from_index(client))

    return menu
