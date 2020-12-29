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
from menus import SimpleMenu
from menus import Text
from menus.radio import BUTTON_BACK
from menus.radio import MAX_ITEM_COUNT
#   Players
from players.helpers import get_client_language
from players.helpers import userid_from_index

# WCS Imports
#   Config
from ..config import cfg_changerace_next_round
from ..config import cfg_resetskills_next_round
#   Constants
from ..constants import GithubModuleStatus
from ..constants import ItemReason
from ..constants import RaceReason
from ..constants.paths import CFG_PATH
from ..constants.paths import RACE_PATH
#   Helpers
from ..helpers.github import github_manager
from ..helpers.overwrites import SayText2
#   Menus
from . import main_menu
from . import shopmenu_menu
from . import shopinfo_menu
from . import shopinfo_detail_menu
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
from . import playerinfo_detail_stats_menu
from . import wcstop_menu
from . import wcstop_detail_menu
from . import levelbank_menu
from . import wcsadmin_menu
from . import wcsadmin_players_menu
from . import wcsadmin_players_sub_menu
from . import wcsadmin_players_sub_xp_menu
from . import wcsadmin_players_sub_levels_menu
from . import wcsadmin_players_sub_changerace_menu
from . import wcsadmin_players_sub_bank_levels_menu
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
#   Modules
from ..modules.items.manager import item_manager
from ..modules.races.manager import race_manager
#   Players
from ..players.entity import Player
from ..players.filters import PlayerReadyIter
#   Translations
from ..translations import chat_strings
from ..translations import menu_strings


# ============================================================================
# >> ALL DECLARATION
# ============================================================================
__all__ = ()


# ============================================================================
# >> GLOBAL VARIABLES
# ============================================================================
xp_required_message = SayText2(chat_strings['xp required'])
gain_level_message = SayText2(chat_strings['gain level'])
skills_reset_message = SayText2(chat_strings['skills reset'])
changerace_message = SayText2(chat_strings['changerace'])
changerace_warning_message = SayText2(chat_strings['changerace warning'])
changerace_changed_message = SayText2(chat_strings['changerace updated'])
skills_reset_updated_message = SayText2(chat_strings['skills reset updated'])
skill_upgrade_message = SayText2(chat_strings['skill upgrade'])
item_bought_message = SayText2(chat_strings['item bought'])
levelbank_spent_message = SayText2(chat_strings['levelbank spent'])
admin_gain_xp_all_message = SayText2(chat_strings['admin gain xp all'])
admin_gain_xp_receiver_message = SayText2(chat_strings['admin gain xp receiver'])
admin_gain_xp_sender_message = SayText2(chat_strings['admin gain xp sender'])
admin_gain_xp_self_message = SayText2(chat_strings['admin gain xp self'])
admin_gain_levels_all_message = SayText2(chat_strings['admin gain levels all'])
admin_gain_levels_receiver_message = SayText2(chat_strings['admin gain levels receiver'])
admin_gain_levels_sender_message = SayText2(chat_strings['admin gain levels sender'])
admin_gain_levels_self_message = SayText2(chat_strings['admin gain levels self'])
admin_changerace_receiver_message = SayText2(chat_strings['admin changerace receiver'])
admin_changerace_sender_message = SayText2(chat_strings['admin changerace sender'])
admin_changerace_self_message = SayText2(chat_strings['admin changerace self'])
admin_gain_bank_levels_all_message = SayText2(chat_strings['admin gain bank levels all'])
admin_gain_bank_levels_receiver_message = SayText2(chat_strings['admin gain bank levels receiver'])
admin_gain_bank_levels_sender_message = SayText2(chat_strings['admin gain bank levels sender'])
admin_gain_bank_levels_self_message = SayText2(chat_strings['admin gain bank levels self'])
github_installing_message = SayText2(chat_strings['github installing'])
github_installing_message = SayText2(chat_strings['github installing'])
github_updating_message = SayText2(chat_strings['github updating'])
github_uninstalling_message = SayText2(chat_strings['github uninstalling'])


# ============================================================================
# >> SELECT CALLBACKS
# ============================================================================
@main_menu.register_select_callback
def main_menu_select(menu, client, option):
    if option.value is changerace_menu:
        if not cfg_changerace_next_round.get_int():
            changerace_warning_message.send(client)

    return option.value


@shopmenu_menu.register_select_callback
def shopmenu_menu_select(menu, client, option):
    wcsplayer = Player(client)

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
    wcsplayer = Player(client)

    if isinstance(option.value, PagedMenu):
        wcsplayer.data['_internal_shopinfo_category'] = option.value.name

        return option.value

    wcsplayer.data['_internal_shopinfo'] = option.value

    return shopinfo_detail_menu


@shopinfo_detail_menu.register_select_callback
def shopinfo_detail_menu_select(menu, client, option):
    if option.choice_index == BUTTON_BACK:
        wcsplayer = Player(client)
        name = wcsplayer.data.get('_internal_shopinfo')
        category = wcsplayer.data.get('_internal_shopinfo_category')

        all_items = item_manager._category_to_values[category]

        if name not in all_items:
            category = None

        if category is None:
            return shopinfo_menu

        return item_manager._info_category_menus[category]


@resetskills_menu.register_select_callback
def resetskills_menu_select(menu, client, option):
    wcsplayer = Player(client)

    if option.choice_index == 1:
        if cfg_resetskills_next_round.get_int():
            wcsplayer.data['_internal_reset_skills'] = True

            skills_reset_updated_message.send(client)
        else:
            unused = 0
            maximum = 0

            for skill in wcsplayer.skills.values():
                unused += skill.level
                skill.level = 0

                maximum += skill.config['maximum']

            wcsplayer.unused = min(wcsplayer.unused + unused, maximum)

            player = wcsplayer.player

            if not player.dead:
                player.godmode = False

                player.client_command('kill', True)

            skills_reset_message.send(client, unused=wcsplayer.unused)

        return

    return option.value


@spendskills_menu.register_select_callback
def spendskills_menu_select(menu, client, option):
    race, skill = option.value

    wcsplayer = Player(client)
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
@changerace_search_menu.register_select_callback
def changerace_menu_select(menu, client, option):
    wcsplayer = Player(client)

    if isinstance(option.value, PagedMenu):
        return option.value

    settings = race_manager[option.value]

    if settings.usable_by(wcsplayer) is RaceReason.ALLOWED:
        if cfg_changerace_next_round.get_int():
            wcsplayer.data['_internal_race_change'] = option.value

            changerace_changed_message.send(client, name=settings.strings['name'])
        else:
            changerace_message.send(client, name=settings.strings['name'])

            wcsplayer.current_race = option.value

            player = wcsplayer.player

            if not player.dead:
                wcsplayer.data['_internal_block_changerace_execution'] = True

                player.godmode = False

                player.client_command('kill', True)
    else:
        return menu


@raceinfo_menu.register_select_callback
def raceinfo_menu_select(menu, client, option):
    wcsplayer = Player(client)

    if isinstance(option.value, PagedMenu):
        wcsplayer.data['_internal_raceinfo_category'] = option.value.name

        return option.value

    wcsplayer.data['_internal_raceinfo'] = option.value

    return raceinfo_detail_menu


@raceinfo_search_menu.register_select_callback
def raceinfo_search_menu_select(menu, client, option):
    wcsplayer = Player(client)

    wcsplayer.data['_internal_raceinfo'] = option.value

    categories = race_manager[option.value].config['categories']

    wcsplayer.data['_internal_raceinfo_category'] = categories[0] if categories else None

    return raceinfo_detail_menu


@raceinfo_detail_menu.register_select_callback
def raceinfo_detail_menu_select(menu, client, option):
    if option.choice_index in (3, 4, BUTTON_BACK):
        wcsplayer = Player(client)
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
    wcsplayer = Player(client)

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
    wcsplayer = Player(client)

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
    wcsplayer = Player(client)

    wcsplayer.data['_internal_wcstop'] = option.value

    return wcstop_detail_menu


@wcstop_detail_menu.register_select_callback
def wcstop_detail_menu_select(menu, client, option):
    return option.value


@levelbank_menu.register_select_callback
def levelbank_menu(menu, client, option):
    if isinstance(option.value, int):
        wcsplayer = Player(client)
        active_race = wcsplayer.active_race

        maximum_race_level = active_race.settings.config.get('maximum_race_level', 0)

        value = option.value if not maximum_race_level else min(maximum_race_level, active_race.level + option.value)

        wcsplayer.bank_level -= value
        active_race.level += value

        levelbank_spent_message.send(client, value=value, name=active_race.settings.strings['name'], level=active_race.level)

        return menu
    elif option.value is None:
        wcsplayer = Player(client)

        return wcsplayer.request_input(_spend_bank_levels, return_menu=menu)

    return option.value


# ============================================================================
# >> ADMIN SELECT CALLBACKS
# ============================================================================
@wcsadmin_menu.register_select_callback
def wcsadmin_menu_select(menu, client, option):
    return option.value


@wcsadmin_players_menu.register_select_callback
def wcsadmin_players_menu_select(menu, client, option):
    wcsplayer = Player(client)

    wcsplayer.data['_internal_wcsadmin_player'] = option.value

    if option.value is None:
        return wcsadmin_players_sub_menu

    wcsplayer.data['_internal_wcsadmin_player_name'] = option.text

    return wcsadmin_players_sub_menu


@wcsadmin_players_sub_menu.register_select_callback
def wcsadmin_players_sub_menu_select(menu, client, option):
    if option.choice_index == 3:
        return Player(client).request_input(_change_race, return_menu=menu)

    return option.value


@wcsadmin_players_sub_xp_menu.register_select_callback
def wcsadmin_players_sub_xp_menu_select(menu, client, option):
    if isinstance(option.value, int):
        wcsplayer = Player(client)
        accountid = wcsplayer.data['_internal_wcsadmin_player']

        if accountid is None:
            for _, wcstarget in PlayerReadyIter():
                active_race = wcstarget.active_race
                old_level = active_race.level

                active_race.xp += option.value

                if wcstarget is wcsplayer:
                    admin_gain_xp_self_message.send(wcsplayer.index, value=option.value)
                else:
                    admin_gain_xp_receiver_message.send(wcstarget.index, value=option.value, name=wcsplayer.name)

                if active_race.level > old_level:
                    gain_level_message.send(wcstarget.index, level=active_race.level, xp=active_race.xp, required=active_race.required_xp)

            admin_gain_xp_all_message.send(wcsplayer.index, value=option.value)
        else:
            wcstarget = Player.from_accountid(accountid)
            active_race = wcstarget.active_race
            old_level = active_race.level

            active_race.xp += option.value

            if wcstarget is wcsplayer:
                admin_gain_xp_self_message.send(wcsplayer.index, value=option.value)
            else:
                admin_gain_xp_sender_message.send(wcsplayer.index, name=wcstarget.name, value=option.value)
                admin_gain_xp_receiver_message.send(wcstarget.index, value=option.value, name=wcsplayer.name)

            if active_race.level > old_level:
                gain_level_message.send(wcstarget.index, level=active_race.level, xp=active_race.xp, required=active_race.required_xp)

        return menu
    elif option.value is None:
        wcsplayer = Player(client)

        return wcsplayer.request_input(_give_experience, return_menu=menu)

    return option.value


@wcsadmin_players_sub_levels_menu.register_select_callback
def wcsadmin_players_sub_levels_menu_select(menu, client, option):
    if isinstance(option.value, int):
        wcsplayer = Player(client)
        accountid = wcsplayer.data['_internal_wcsadmin_player']

        if accountid is None:
            for _, wcstarget in PlayerReadyIter():
                wcstarget.level += option.value

                if wcstarget is wcsplayer:
                    admin_gain_levels_self_message.send(wcsplayer.index, value=option.value)
                else:
                    admin_gain_levels_receiver_message.send(wcstarget.index, value=option.value, name=wcsplayer.name)

            admin_gain_levels_all_message.send(wcsplayer.index, value=option.value)
        else:
            wcstarget = Player.from_accountid(accountid)

            wcstarget.level += option.value

            if wcstarget is wcsplayer:
                admin_gain_levels_self_message.send(wcsplayer.index, value=option.value)
            else:
                admin_gain_levels_sender_message.send(wcsplayer.index, name=wcstarget.name, value=option.value)
                admin_gain_levels_receiver_message.send(wcstarget.index, value=option.value, name=wcsplayer.name)

        return menu
    elif option.value is None:
        wcsplayer = Player(client)

        return wcsplayer.request_input(_give_levels, return_menu=menu)

    return option.value


@wcsadmin_players_sub_changerace_menu.register_select_callback
def wcsadmin_players_sub_changerace_menu_select(menu, client, option):
    wcsplayer = Player(client)
    accountid = wcsplayer.data['_internal_wcsadmin_player']
    wcstarget = Player.from_accountid(accountid)

    if wcstarget.online:
        wcstarget.current_race = option.value

        player = wcstarget.player

        if not player.dead:
            player.godmode = False

            player.client_command('kill', True)

        if wcstarget is wcsplayer:
            admin_changerace_self_message.send(client, value=race_manager[option.value].strings['name'])
        else:
            admin_changerace_receiver_message.send(wcstarget.index, value=race_manager[option.value].strings['name'])
            admin_changerace_sender_message.send(client, name=wcstarget.name, value=race_manager[option.value].strings['name'])

        active_race = wcstarget.active_race

        xp_required_message.send(wcsplayer.index, name=active_race.settings.strings['name'], level=active_race.level, xp=active_race.xp, required=active_race.required_xp)

    return menu.parent_menu


@wcsadmin_players_sub_bank_levels_menu.register_select_callback
def wcsadmin_players_sub_bank_levels_menu_select(menu, client, option):
    if isinstance(option.value, int):
        wcsplayer = Player(client)
        accountid = wcsplayer.data['_internal_wcsadmin_player']

        if accountid is None:
            for _, wcstarget in PlayerReadyIter():
                wcstarget.bank_level += option.value

                if wcstarget is wcsplayer:
                    admin_gain_bank_levels_self_message.send(wcsplayer.index, value=option.value)
                else:
                    admin_gain_bank_levels_receiver_message.send(wcstarget.index, value=option.value, name=wcsplayer.name)

            admin_gain_bank_levels_all_message.send(wcsplayer.index, value=option.value)
        else:
            wcstarget = Player.from_accountid(accountid)

            wcstarget.bank_level += option.value

            if wcstarget is wcsplayer:
                admin_gain_bank_levels_self_message.send(wcsplayer.index, value=option.value)
            else:
                admin_gain_bank_levels_sender_message.send(wcsplayer.index, name=wcstarget.name, value=option.value)
                admin_gain_bank_levels_receiver_message.send(wcstarget.index, value=option.value, name=wcsplayer.name)

        return menu
    elif option.value is None:
        wcsplayer = Player(client)

        return wcsplayer.request_input(_give_bank_levels, return_menu=menu)

    return option.value


@wcsadmin_management_menu.register_select_callback
def wcsadmin_management_menu_select(menu, client, option):
    return option.value


@wcsadmin_management_races_menu.register_select_callback
def wcsadmin_management_races_menu_select(menu, client, option):
    wcsplayer = Player(client)

    if isinstance(option.value, str):
        wcsplayer.data['_internal_wcsadmin_editor_value'] = option.value

        return wcsadmin_management_races_editor_menu

    return wcsadmin_management_races_add_menu


@wcsadmin_management_items_menu.register_select_callback
def wcsadmin_management_items_menu_select(menu, client, option):
    wcsplayer = Player(client)

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
    wcsplayer = Player(client)

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


@wcsadmin_management_races_editor_modify_menu.register_select_callback
def wcsadmin_management_races_editor_modify_menu_select(menu, client, option):
    if callable(option.value):
        wcsplayer = Player(client)

        return wcsplayer.request_input(option.value, return_menu=menu)
    elif isinstance(option.value, str):
        wcsplayer = Player(client)
        wcsplayer.data['_internal_wcsadmin_editor_key'] = option.value

        return wcsadmin_management_races_editor_modify_from_selection_menu

    return option.value


@wcsadmin_management_races_editor_modify_from_selection_menu.register_select_callback
def wcsadmin_management_races_editor_modify_from_selection_menu_select(menu, client, option):
    if option.value is None:
        wcsplayer = Player(client)

        return wcsplayer.request_input(_request_add_new_value, return_menu=menu)
    elif isinstance(option.value, str):
        wcsplayer = Player(client)

        _update_config(RACE_PATH, wcsplayer.data['_internal_wcsadmin_editor_value'], wcsplayer.data['_internal_wcsadmin_editor_key'], option.value, False)

    return menu


@wcsadmin_management_races_editor_modify_restricted_team_menu.register_select_callback
def wcsadmin_management_races_editor_modify_restricted_team_menu_select(menu, client, option):
    if isinstance(option.value, int):
        wcsplayer = Player(client)

        _update_config(RACE_PATH, wcsplayer.data['_internal_wcsadmin_editor_value'], 'restrictteam', option.value)

    return wcsadmin_management_races_editor_modify_menu


@wcsadmin_github_menu.register_select_callback
def wcsadmin_github_menu_select(menu, client, option):
    return option.value


@wcsadmin_github_races_menu.register_select_callback
def wcsadmin_github_races_menu_select(menu, client, option):
    wcsplayer = Player(client)

    wcsplayer.data['_internal_wcsadmin_github_name'] = option.value

    return wcsadmin_github_races_options_menu


@wcsadmin_github_races_options_menu.register_select_callback
def wcsadmin_github_races_options_menu_select(menu, client, option):
    wcsplayer = Player(client)

    if isinstance(option.value, GithubModuleStatus):
        wcsplayer.data['_internal_wcsadmin_github_cycle'] = 0

        name = wcsplayer.data['_internal_wcsadmin_github_name']

        if option.value is GithubModuleStatus.INSTALLING:
            if len(github_manager['races'][name]['repositories']) > 1:
                return wcsadmin_github_races_repository_menu
            else:
                github_installing_message.send(client, name=name)

                github_manager.install_module(list(github_manager['races'][name]['repositories'])[0], 'races', name, userid_from_index(client))
        elif option.value is GithubModuleStatus.UPDATING:
            github_updating_message.send(client, name=name)

            github_manager.update_module('races', name, userid_from_index(client))
        else:
            github_uninstalling_message.send(client, name=name)

            github_manager.uninstall_module('races', name, userid_from_index(client))
    elif isinstance(option.value, SimpleMenu):
        return option.value

    return menu


@wcsadmin_github_races_repository_menu.register_select_callback
def wcsadmin_github_races_repository_menu_select(menu, client, option):
    wcsplayer = Player(client)
    name = wcsplayer.data['_internal_wcsadmin_github_name']

    github_installing_message.send(client, name=name)

    github_manager.install_module(option.value, 'races', name, userid_from_index(client))

    return wcsadmin_github_races_repository_menu.parent_menu


@wcsadmin_github_items_menu.register_select_callback
def wcsadmin_github_items_menu_select(menu, client, option):
    wcsplayer = Player(client)

    wcsplayer.data['_internal_wcsadmin_github_name'] = option.value

    return wcsadmin_github_items_options_menu


@wcsadmin_github_items_options_menu.register_select_callback
def wcsadmin_github_items_options_menu_select(menu, client, option):
    wcsplayer = Player(client)

    if isinstance(option.value, GithubModuleStatus):
        wcsplayer.data['_internal_wcsadmin_github_cycle'] = 0

        name = wcsplayer.data['_internal_wcsadmin_github_name']

        if option.value is GithubModuleStatus.INSTALLING:
            if len(github_manager['items'][name]['repositories']) > 1:
                return wcsadmin_github_items_repository_menu
            else:
                github_installing_message.send(client, name=name)

                github_manager.install_module(list(github_manager['items'][name]['repositories'])[0], 'items', name, userid_from_index(client))
        elif option.value is GithubModuleStatus.UPDATING:
            github_updating_message.send(client, name=name)

            github_manager.update_module('items', name, userid_from_index(client))
        else:
            github_uninstalling_message.send(client, name=name)

            github_manager.uninstall_module('items', name, userid_from_index(client))
    elif isinstance(option.value, SimpleMenu):
        return option.value

    return menu


@wcsadmin_github_info_menu.register_select_callback
def wcsadmin_github_info_menu_select(menu, client, option):
    if option.choice_index == 1:
        menu._checking_cycle = 0

        menu[3] = Text(menu_strings['wcsadmin_github_info_menu checking'])
        github_manager.check_new_version()

        menu[4] = Text(' ')

        for index in menu._player_pages:
            if menu.is_active_menu(index):
                menu._refresh(index)
    elif option.choice_index == 2:
        return wcsadmin_github_info_confirm_menu
    elif option.choice_index == 3:
        if not option.value:
            github_manager.refresh_commits()

    return option.value or menu


@wcsadmin_github_info_confirm_menu.register_select_callback
def wcsadmin_github_info_confirm_menu_select(menu, client, option):
    if option.choice_index == 1:
        wcsadmin_github_info_menu.send([*menu._player_pages])
        menu.close([*menu._player_pages])

        wcsadmin_github_info_menu[3].selectable = wcsadmin_github_info_menu[3].highlight = False

        wcsadmin_github_info_menu[4] = Text(menu_strings['wcsadmin_github_info_menu updating'])
        wcsadmin_github_info_menu._installing_cycle = 0

        github_manager.refresh_commits()
        github_manager.install_new_version()

        return

    return option.value


@wcsadmin_github_info_confirm_commits_menu.register_select_callback
def wcsadmin_github_info_confirm_commits_menu(menu, client, option):
    return option.value


@wcsadmin_github_info_commits_menu.register_select_callback
def wcsadmin_github_info_commits_menu_select(menu, client, option):
    return option.value


# ============================================================================
# >> REQUEST CALLBACKS
# ============================================================================
def _request_required(wcsplayer, value):
    if not value.isdigit():
        return False

    _update_config(RACE_PATH, wcsplayer.data['_internal_wcsadmin_editor_value'], 'required', int(value))

    return True


def _request_maximum(wcsplayer, value):
    if not value.isdigit():
        return False

    _update_config(RACE_PATH, wcsplayer.data['_internal_wcsadmin_editor_value'], 'maximum', int(value))

    return True


def _request_team_limit(wcsplayer, value):
    if not value.isdigit():
        return False

    _update_config(RACE_PATH, wcsplayer.data['_internal_wcsadmin_editor_value'], 'teamlimit', int(value))

    return True


def _request_add_new_value(wcsplayer, value):
    _update_config(RACE_PATH, wcsplayer.data['_internal_wcsadmin_editor_value'], wcsplayer.data['_internal_wcsadmin_editor_key'], value)

    return True


def _change_race(wcsplayer, value):
    found = []
    lower_search = value.lower()
    language = get_client_language(wcsplayer.index)

    for name, settings in race_manager.items():
        if lower_search == settings.strings['name'].get_string(language).lower():
            if name not in found:
                found.append(name)

    for name, settings in race_manager.items():
        if lower_search in settings.strings['name'].get_string(language).lower():
            if name not in found:
                found.append(name)

    for partial in [x.lower() for x in value.split()]:
        for name, settings in race_manager.items():
            if partial in settings.strings['name'].get_string(language).lower():
                if name not in found:
                    found.append(name)

    if found:
        wcsplayer.data['_internal_wcsadmin_changerace'] = found

        return wcsadmin_players_sub_changerace_menu
    else:
        return False


def _give_experience(wcsplayer, value):
    if not value.isdigit():
        return False

    value = int(value)

    accountid = wcsplayer.data.get('_internal_wcsadmin_player')

    if accountid is None:
        for _, wcstarget in PlayerReadyIter():
            active_race = wcstarget.active_race
            old_level = active_race.level

            active_race.xp += value

            if wcstarget is wcsplayer:
                admin_gain_xp_self_message.send(wcsplayer.index, value=value)
            else:
                admin_gain_xp_receiver_message.send(wcstarget.index, value=value, name=wcsplayer.name)

            if active_race.level > old_level:
                gain_level_message.send(wcstarget.index, level=active_race.level, xp=active_race.xp, required=active_race.required_xp)

        admin_gain_xp_all_message.send(wcsplayer.index, value=value)
    else:
        wcstarget = Player.from_accountid(accountid)

        if wcstarget.ready:
            active_race = wcstarget.active_race
            old_level = active_race.level

            active_race.xp += value

            if wcstarget is wcsplayer:
                admin_gain_xp_self_message.send(wcsplayer.index, value=value)
            else:
                admin_gain_xp_sender_message.send(wcsplayer.index, name=wcstarget.name, value=value)
                admin_gain_xp_receiver_message.send(wcstarget.index, value=value, name=wcsplayer.name)

            if active_race.level > old_level:
                gain_level_message.send(wcstarget.index, level=active_race.level, xp=active_race.xp, required=active_race.required_xp)

    return True


def _give_levels(wcsplayer, value):
    if not value.isdigit():
        return False

    value = int(value)

    accountid = wcsplayer.data.get('_internal_wcsadmin_player')

    if accountid is None:
        for _, wcstarget in PlayerReadyIter():
            wcstarget.level += value

            if wcstarget is wcsplayer:
                admin_gain_levels_self_message.send(wcsplayer.index, value=value)
            else:
                admin_gain_levels_receiver_message.send(wcstarget.index, value=value, name=wcsplayer.name)

        admin_gain_levels_all_message.send(wcsplayer.index, value=value)
    else:
        wcstarget = Player.from_accountid(accountid)

        if wcstarget.ready:
            wcstarget.level += value

            if wcstarget is wcsplayer:
                admin_gain_levels_self_message.send(wcsplayer.index, value=value)
            else:
                admin_gain_levels_sender_message.send(wcsplayer.index, name=wcstarget.name, value=value)
                admin_gain_levels_receiver_message.send(wcstarget.index, value=value, name=wcsplayer.name)

    return True


def _give_bank_levels(wcsplayer, value):
    if not value.isdigit():
        return False

    value = int(value)

    accountid = wcsplayer.data.get('_internal_wcsadmin_player')

    if accountid is None:
        for _, wcstarget in PlayerReadyIter():
            wcstarget.bank_level += value

            if wcstarget is wcsplayer:
                admin_gain_bank_levels_self_message.send(wcsplayer.index, value=value)
            else:
                admin_gain_bank_levels_receiver_message.send(wcstarget.index, value=value, name=wcsplayer.name)

        admin_gain_bank_levels_all_message.send(wcsplayer.index, value=value)
    else:
        wcstarget = Player.from_accountid(accountid)

        if wcstarget.ready:
            wcstarget.bank_level += value

            if wcstarget is wcsplayer:
                admin_gain_bank_levels_self_message.send(wcsplayer.index, value=value)
            else:
                admin_gain_bank_levels_sender_message.send(wcsplayer.index, name=wcstarget.name, value=value)
                admin_gain_bank_levels_receiver_message.send(wcstarget.index, value=value, name=wcsplayer.name)

    return True


def _spend_bank_levels(wcsplayer, value):
    if not value.isdigit():
        return False

    value = int(value)

    if value > wcsplayer.bank_level:
        # Let the player know they entered an invalid value to prevent typos
        return False

    active_race = wcsplayer.active_race

    maximum_race_level = active_race.settings.config.get('maximum_race_level', 0)

    value = value if not maximum_race_level else min(maximum_race_level, active_race.level + value)

    wcsplayer.bank_level -= value
    active_race.level += value

    levelbank_spent_message.send(wcsplayer.index, value=value, name=active_race.settings.strings['name'], level=active_race.level)

    return True


# ============================================================================
# >> HELPERS
# ============================================================================
def _update_config(path, name, key, value, append=True):
    name = name[1:] if name.startswith('_') else name
    path = path / name

    with open(path / 'config.json') as inputfile:
        config = load(inputfile)

    if isinstance(config[key], list):
        if append:
            if value not in config[key]:
                config[key].append(value)
        else:
            config[key].remove(value)
    else:
        config[key] = value

    with open(path / 'config.json', 'w') as outputfile:
        dump(config, outputfile, indent=4)

    race_manager._refresh_config.add(name)
