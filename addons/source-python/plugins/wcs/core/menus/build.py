# ../wcs/core/menus/build.py

# ============================================================================
# >> IMPORTS
# ============================================================================
# Python Imports
#   Copy
from copy import deepcopy
#   Enum
from enum import IntEnum
#   JSON
from json import load
#   Textwrap
from textwrap import wrap
#   Time
from time import localtime
from time import strftime

# Source.Python Imports
#   Core
from core import GAME_NAME
#   Engines
from engines.server import global_vars
#   Hooks
from hooks.exceptions import except_hooks
#   Players
from players.helpers import get_client_language
#   Translations
from translations.strings import TranslationStrings

# WCS Imports
#   Constants
from ..constants import TIME_FORMAT
from ..constants import GithubModuleStatus
from ..constants import ItemReason
from ..constants import RaceReason
from ..constants.paths import CFG_PATH
from ..constants.paths import ITEM_PATH
from ..constants.paths import RACE_PATH
#   Helpers
from ..helpers.github import github_manager
#   Listeners
from ..listeners import OnIsItemUsableText
from ..listeners import OnIsRaceUsableText
#   Menus
from . import _get_current_options
from . import main_menu
from . import main2_menu
from . import shopmenu_menu
from . import shopinfo_detail_menu
from . import showskills_menu
from . import spendskills_menu
from . import changerace_menu
from . import changerace_search_menu
from . import raceinfo_search_menu
from . import raceinfo_detail_menu
from . import raceinfo_skills_menu
from . import raceinfo_skills_single_menu
from . import raceinfo_skills_detail_menu
from . import raceinfo_race_detail_menu
from . import playerinfo_menu
from . import playerinfo_online_menu
from . import playerinfo_offline_menu
from . import playerinfo_detail_menu
from . import playerinfo_detail_skills_menu
from . import playerinfo_detail_stats_menu
from . import wcstop_menu
from . import wcstop_detail_menu
from . import levelbank_menu
from . import input_menu
from . import wcsadmin_menu
from . import wcsadmin_players_menu
from . import wcsadmin_players_online_menu
from . import wcsadmin_players_offline_menu
from . import wcsadmin_players_sub_menu
from . import wcsadmin_players_sub_xp_menu
from . import wcsadmin_players_sub_levels_menu
from . import wcsadmin_players_sub_changerace_menu
from . import wcsadmin_players_sub_bank_levels_menu
from . import wcsadmin_management_races_menu
from . import wcsadmin_management_items_menu
from . import wcsadmin_management_races_add_menu
from . import wcsadmin_management_items_add_menu
from . import wcsadmin_management_races_editor_menu
from . import wcsadmin_management_items_editor_menu
from . import wcsadmin_management_races_editor_modify_menu
from . import wcsadmin_management_races_editor_modify_from_selection_menu
from . import wcsadmin_management_races_editor_modify_restricted_team_menu
from . import wcsadmin_github_races_menu
from . import wcsadmin_github_races_options_menu
from . import wcsadmin_github_races_repository_menu
from . import wcsadmin_github_items_menu
from . import wcsadmin_github_items_options_menu
from . import wcsadmin_github_items_repository_menu
from . import wcsadmin_github_info_menu
from . import wcsadmin_github_info_commits_menu
from .base import MAX_ITEM_COUNT
from .base import PagedOption
from .base import SimpleOption
from .base import Text
#   Modules
from ..modules.items.manager import item_manager
from ..modules.races.manager import race_manager
#   Players
from ..players import team_data
from ..players.entity import Player
from ..players.filters import PlayerReadyIter
#   Ranks
from ..ranks import rank_manager
#   Translations
from ..translations import menu_strings


# ============================================================================
# >> ALL DECLARATION
# ============================================================================
__all__ = ()


# ============================================================================
# >> BUILD CALLBACKS
# ============================================================================
@main_menu.register_build_callback
@main2_menu.register_build_callback
def main_menu_build(menu, client):
    wcsplayer = Player(client)

    if GAME_NAME in ('hl2mp', ):
        if menu is main_menu:
            menu[0].selectable = menu[0].highlight = wcsplayer.ready and bool(item_manager)
            menu[1].selectable = menu[1].highlight = bool(item_manager)
            menu[2].selectable = menu[2].highlight = wcsplayer.ready
            menu[3].selectable = menu[3].highlight = wcsplayer.ready
            menu[4].selectable = menu[4].highlight = wcsplayer.ready
        else:
            menu[0].selectable = menu[0].highlight = wcsplayer.ready and wcsplayer.unused > 0
            menu[1].selectable = menu[1].highlight = wcsplayer.ready and bool(race_manager) and (len(race_manager) > 1 or None not in race_manager)
            menu[2].selectable = menu[2].highlight = bool(race_manager) and (len(race_manager) > 1 or None not in race_manager)
    else:
        menu[1].selectable = menu[1].highlight = wcsplayer.ready and bool(item_manager)
        menu[2].selectable = menu[2].highlight = bool(item_manager)
        menu[4].selectable = menu[4].highlight = wcsplayer.ready
        menu[5].selectable = menu[5].highlight = wcsplayer.ready
        menu[6].selectable = menu[6].highlight = wcsplayer.ready and wcsplayer.unused > 0
        menu[8].selectable = menu[8].highlight = wcsplayer.ready and bool(race_manager) and (len(race_manager) > 1 or None not in race_manager)
        menu[9].selectable = menu[9].highlight = bool(race_manager) and (len(race_manager) > 1 or None not in race_manager)


@shopmenu_menu.register_build_callback
def shopmenu_menu_build(menu, client):
    wcsplayer = Player(client)

    for option in _get_current_options(menu, client):
        if isinstance(option.value, str):
            settings = item_manager[option.value]
            reason = settings.usable_by(wcsplayer)

            if reason is ItemReason.ALLOWED:
                option.text = deepcopy(menu_strings['shopmenu_menu line'])
                option.text.tokens['cost'] = settings.config['cost']
                option.selectable = option.highlight = True
            elif reason is ItemReason.TOO_MANY:
                option.text = deepcopy(menu_strings['shopmenu_menu too many'])
                option.text.tokens['total'] = settings.config['count']
                option.selectable = option.highlight = False
            elif reason is ItemReason.CANNOT_AFFORD:
                option.text = deepcopy(menu_strings['shopmenu_menu cannot afford'])
                option.text.tokens['value'] = settings.config['cost'] - wcsplayer.player.cash
                option.selectable = option.highlight = False
            elif reason is ItemReason.RACE_RESTRICTED:
                option.text = deepcopy(menu_strings['shopmenu_menu race restricted'])
                option.selectable = option.highlight = False
            elif reason is ItemReason.TOO_MANY_CATEGORY:
                option.text = deepcopy(menu_strings[f'shopmenu_menu too many category'])
                option.text.tokens['total'] = wcsplayer.items._maxitems[wcsplayer.data['_internal_shopmenu']]
                option.selectable = option.highlight = False
            elif reason is ItemReason.WRONG_STATUS:
                option.text = deepcopy(menu_strings[f'shopmenu_menu wrong status {settings.config["dab"]}'])
                option.selectable = option.highlight = False
            elif reason is ItemReason.REQUIRED_LEVEL:
                option.text = deepcopy(menu_strings['shopmenu_menu required level'])
                option.text.tokens['level'] = settings.config['required']
                option.selectable = option.highlight = False
            elif reason is ItemReason.ROUND_RESTART:
                option.text = deepcopy(menu_strings['shopmenu_menu round restart'])
                option.selectable = option.highlight = False
            elif isinstance(reason, IntEnum):
                data = {'reason':reason, 'string':None}

                OnIsItemUsableText.manager.notify(wcsplayer, settings, data)

                if not isinstance(data['string'], TranslationStrings):
                    raise ValueError(f'Invalid string: {data["string"]}')

                option.text = data['string']
                option.selectable = option.highlight = False
            else:
                raise ValueError(f'Invalid reason: {reason}')

            option.text.tokens['name'] = settings.strings['name']


@shopinfo_detail_menu.register_build_callback
def shopinfo_detail_menu_build(menu, client):
    wcsplayer = Player(client)
    item_name = wcsplayer.data['_internal_shopinfo']
    settings = item_manager[item_name]

    menu[0].text.tokens['name'] = settings.strings['name']
    menu[1].text.tokens['level'] = settings.config['required']
    menu[2].text.tokens['cost'] = settings.config['cost']
    menu[3].text = menu_strings[f'shopinfo_detail_menu line 3 {settings.config["dab"]}']
    menu[4].text = menu_strings[f'shopinfo_detail_menu line 4 {settings.config["duration"]}']

    for i, option in enumerate(menu[5:], 5):
        if isinstance(option, SimpleOption):
            del menu[5:i]
            break

    kwargs = {}

    settings.execute('on_item_desc', wcsplayer, kwargs)

    info = settings.strings['description']

    if info:
        info = info.get_string(get_client_language(client), **kwargs)

        for i, text in enumerate(wrap(info, 30), 5):
            menu.insert(i, text)

        for i in range(i + 1, MAX_ITEM_COUNT + 2):
            menu.insert(i, Text(' '))
    else:
        for i in range(i + 1, MAX_ITEM_COUNT + 2):
            menu.insert(i, Text(' '))


@showskills_menu.register_build_callback
def showskills_menu_build(menu, client):
    menu.clear()

    wcsplayer = Player(client)
    active_race = wcsplayer.active_race
    settings = active_race.settings

    menu.title.tokens['name'] = active_race.settings.strings['name']
    menu.description.tokens['unused'] = active_race.unused

    for skill_name in settings.config['skills']:
        skill = active_race.skills[skill_name]
        option = PagedOption(deepcopy(menu_strings['showskills_menu line']), selectable=False)
        option.text.tokens['name'] = settings.strings[skill_name]
        option.text.tokens['level'] = skill.level
        option.text.tokens['maximum'] = skill.config['maximum']

        menu.append(option)


@spendskills_menu.register_build_callback
def spendskills_menu_build(menu, client):
    menu.clear()

    wcsplayer = Player(client)
    active_race = wcsplayer.active_race
    settings = active_race.settings

    menu.description.tokens['unused'] = active_race.unused

    for skill_name, config in settings.config['skills'].items():
        skill = active_race.skills[skill_name]
        maximum = config['maximum']
        required = config['required']

        if skill.level >= maximum:
            option = PagedOption(deepcopy(menu_strings['spendskills_menu max']), selectable=False, highlight=False)
        elif active_race.level < required[skill.level]:
            option = PagedOption(deepcopy(menu_strings['spendskills_menu required']), selectable=False, highlight=False)
            option.text.tokens['required'] = required[skill.level]
        else:
            option = PagedOption(deepcopy(menu_strings['spendskills_menu skill']), (active_race.name, skill_name))
            option.selectable = option.highlight = active_race.unused > 0
            option.text.tokens['level'] = skill.level
            option.text.tokens['maxlevel'] = maximum

        option.text.tokens['name'] = settings.strings[skill_name]

        menu.append(option)


@changerace_menu.register_build_callback
def changerace_menu_build(menu, client):
    wcsplayer = Player(client)

    for option in _get_current_options(menu, client):
        if isinstance(option.value, str):
            settings = race_manager[option.value]
            reason = settings.usable_by(wcsplayer)

            if reason is RaceReason.ALLOWED:
                option.text = deepcopy(menu_strings['changerace_menu line'])
                race = wcsplayer._races.get(option.value)

                if race is None:
                    option.text.tokens['level'] = 0
                else:
                    option.text.tokens['level'] = race.level

                option.selectable = option.highlight = not wcsplayer.current_race == option.value
            elif reason is RaceReason.REQUIRED_LEVEL:
                option.text = deepcopy(menu_strings['changerace_menu required level'])
                option.text.tokens['level'] = settings.config['required']
                option.selectable = option.highlight = False
            elif reason is RaceReason.MAXIMUM_LEVEL:
                option.text = deepcopy(menu_strings['changerace_menu maximum level'])
                option.text.tokens['level'] = settings.config['maximum']
                option.selectable = option.highlight = False
            elif reason is RaceReason.TEAM_LIMIT:
                option.text = deepcopy(menu_strings['changerace_menu team limit'])
                option.text.tokens['count'] = len(team_data[wcsplayer.player.team][f'_internal_{option.value}_limit_allowed'])
                option.selectable = option.highlight = False
            elif reason is RaceReason.TEAM:
                option.text = deepcopy(menu_strings['changerace_menu team'])
                option.text.tokens['team'] = ['T', 'CT'][wcsplayer.player.team - 2]
                option.selectable = option.highlight = False
            elif reason is RaceReason.PRIVATE or reason is RaceReason.VIP or reason is RaceReason.ADMIN:
                option.text = deepcopy(menu_strings['changerace_menu private'])
                option.selectable = option.highlight = False
            elif reason is RaceReason.MAP:
                option.text = deepcopy(menu_strings['changerace_menu map'])
                option.text.tokens['map'] = global_vars.map_name
                option.selectable = option.highlight = False
            elif isinstance(reason, IntEnum):
                data = {'reason':reason, 'string':None}

                OnIsRaceUsableText.manager.notify(wcsplayer, settings, data)

                if not isinstance(data['string'], TranslationStrings):
                    raise ValueError(f'Invalid string: {data["string"]}')

                option.text = data['string']
                option.selectable = option.highlight = False
            else:
                raise ValueError(f'Invalid reason: {reason}')

            option.text.tokens['name'] = settings.strings['name']


@changerace_search_menu.register_build_callback
def changerace_search_menu_build(menu, client):
    menu.clear()

    wcsplayer = Player(client)

    for name in wcsplayer.data['_internal_changerace_search']:
        menu.append(PagedOption(deepcopy(menu_strings['changerace_menu line']), name))

    for option in _get_current_options(menu, client):
        if isinstance(option.value, str):
            settings = race_manager[option.value]
            reason = settings.usable_by(wcsplayer)

            if reason is RaceReason.ALLOWED:
                option.text = deepcopy(menu_strings['changerace_menu line'])
                race = wcsplayer._races.get(option.value)

                if race is None:
                    option.text.tokens['level'] = 0
                else:
                    option.text.tokens['level'] = race.level

                option.selectable = option.highlight = not wcsplayer.current_race == option.value
            elif reason is RaceReason.REQUIRED_LEVEL:
                option.text = deepcopy(menu_strings['changerace_menu required level'])
                option.text.tokens['level'] = settings.config['required']
                option.selectable = option.highlight = False
            elif reason is RaceReason.MAXIMUM_LEVEL:
                option.text = deepcopy(menu_strings['changerace_menu maximum level'])
                option.text.tokens['level'] = settings.config['maximum']
                option.selectable = option.highlight = False
            elif reason is RaceReason.TEAM_LIMIT:
                option.text = deepcopy(menu_strings['changerace_menu team limit'])
                option.text.tokens['count'] = len(team_data[wcsplayer.player.team][f'_internal_{option.value}_limit_allowed'])
                option.selectable = option.highlight = False
            elif reason is RaceReason.TEAM:
                option.text = deepcopy(menu_strings['changerace_menu team'])
                option.text.tokens['team'] = ['T', 'CT'][wcsplayer.player.team - 2]
                option.selectable = option.highlight = False
            elif reason is RaceReason.PRIVATE or reason is RaceReason.VIP or reason is RaceReason.ADMIN:
                option.text = deepcopy(menu_strings['changerace_menu private'])
                option.selectable = option.highlight = False
            elif reason is RaceReason.MAP:
                option.text = deepcopy(menu_strings['changerace_menu map'])
                option.text.tokens['map'] = global_vars.map_name
                option.selectable = option.highlight = False
            elif isinstance(reason, IntEnum):
                data = {'reason':reason, 'string':None}

                OnIsRaceUsableText.manager.notify(wcsplayer, settings, data)

                if not isinstance(data['string'], TranslationStrings):
                    raise ValueError(f'Invalid string: {data["string"]}')

                option.text = data['string']
                option.selectable = option.highlight = False
            else:
                raise ValueError(f'Invalid reason: {reason}')

            option.text.tokens['name'] = settings.strings['name']


@raceinfo_search_menu.register_build_callback
def raceinfo_search_menu_build(menu, client):
    menu.clear()

    wcsplayer = Player(client)

    for name in wcsplayer.data['_internal_raceinfo_search']:
        menu.append(PagedOption(race_manager[name].strings['name'], name))


@raceinfo_detail_menu.register_build_callback
def raceinfo_detail_menu_build(menu, client):
    wcsplayer = Player(client)
    name = wcsplayer.data['_internal_raceinfo']
    settings = race_manager[name]

    all_races = race_manager._category_to_values[wcsplayer.data.get('_internal_raceinfo_category')]

    if name not in all_races:
        all_races = race_manager._category_to_values[None]

    try:
        index = all_races.index(name)
    except IndexError:
        index = None
        except_hooks.print_exception()

    menu[0].text.tokens['name'] = settings.strings['name']
    menu[0].text.tokens['place'] = -1 if index is None else index + 1
    menu[0].text.tokens['total'] = len(all_races)
    menu[1].text.tokens['required'] = settings.config['required']
    menu[2].text.tokens['maximum'] = settings.config['maximum']
    menu[3].text.tokens['name'] = settings.config['author']

    if settings.config['allowonly']:
        if wcsplayer._baseplayer.steamid2 in settings.config['allowonly'] or wcsplayer._baseplayer.steamid3 in settings.config['allowonly']:
            menu[4].text = menu_strings['raceinfo_detail_menu private allowed']
        elif 'VIP' in settings.config['allowonly'] and wcsplayer.privileges.get('vip_raceaccess'):
            menu[4].text = menu_strings['raceinfo_detail_menu private allowed']
        elif 'ADMIN' in settings.config['allowonly'] and wcsplayer.privileges.get('admin_raceaccess'):
            menu[4].text = menu_strings['raceinfo_detail_menu private allowed']
        else:
            menu[4].text = menu_strings['raceinfo_detail_menu private']
    else:
        menu[4].text = menu_strings['raceinfo_detail_menu public']

    menu[5].text.tokens['count'] = len(settings.config['skills'])

    menu[7].selectable = menu[7].highlight = False if index is None else index != 0
    menu[8].selectable = menu[8].highlight = False if index is None else index != len(all_races) - 1


@raceinfo_skills_menu.register_build_callback
def raceinfo_skills_menu_build(menu, client):
    menu.clear()

    wcsplayer = Player(client)
    name = wcsplayer.data['_internal_raceinfo']
    settings = race_manager[name]

    menu.title.tokens['name'] = settings.strings['name']

    i = 1

    for name in settings.config['skills']:
        events = settings.config['skills'][name]['event']

        if 'player_ultimate' in events:
            option = PagedOption(menu_strings['raceinfo_skills_menu ultimate'], name)
            option.text.tokens['name'] = settings.strings[name]
        elif 'player_ability' in events:
            option = PagedOption(menu_strings['raceinfo_skills_menu ability'], name)
            option.text.tokens['name'] = settings.strings[name]
        elif 'player_ability_on' in events or 'player_ability_off' in events:
            option = PagedOption(menu_strings['raceinfo_skills_menu ability_on'], name)
            option.text.tokens['name'] = settings.strings[name]
            option.text.tokens['index'] = i

            i += 1
        else:
            option = PagedOption(settings.strings[name], name)

        menu.append(option)


@raceinfo_skills_single_menu.register_build_callback
def raceinfo_skills_single_menu_build(menu, client):
    menu.clear()

    wcsplayer = Player(client)
    name = wcsplayer.data['_internal_raceinfo']
    settings = race_manager[name]

    menu.title.tokens['name'] = settings.strings['name']

    current_skill = wcsplayer.data.get('_internal_raceinfo_viewing_skill')

    i = 1

    for name in settings.config['skills']:
        events = settings.config['skills'][name]['event']

        if 'player_ultimate' in events:
            option = PagedOption(menu_strings['raceinfo_skills_menu ultimate'], name)
            option.text.tokens['name'] = settings.strings[name]
        elif 'player_ability' in events:
            option = PagedOption(menu_strings['raceinfo_skills_menu ability'], name)
            option.text.tokens['name'] = settings.strings[name]
        elif 'player_ability_on' in events or 'player_ability_off' in events:
            option = PagedOption(menu_strings['raceinfo_skills_menu ability_on'], name)
            option.text.tokens['name'] = settings.strings[name]
            option.text.tokens['index'] = i

            i += 1
        else:
            option = PagedOption(settings.strings[name], name)

        menu.append(option)

        if name == current_skill:
            kwargs = {}

            settings.execute('on_skill_desc', wcsplayer, name, kwargs)

            info = settings.strings[f'{name} description']

            if info:
                info = info.get_string(get_client_language(client), **kwargs)

                for text in wrap(info, 30):
                    menu.append(text)


@raceinfo_skills_detail_menu.register_build_callback
def raceinfo_skills_detail_menu_build(menu, client):
    del menu[2:-3]

    wcsplayer = Player(client)
    race_name = wcsplayer.data['_internal_raceinfo']
    skill_name = wcsplayer.data['_internal_raceinfo_skill']
    settings = race_manager[race_name]

    menu[0].text.tokens['name'] = settings.strings['name']
    menu[1].text.tokens['name'] = settings.strings[skill_name]

    kwargs = {}

    settings.execute('on_skill_desc', wcsplayer, skill_name, kwargs)

    info = settings.strings[f'{skill_name} description']

    if info:
        info = info.get_string(get_client_language(client), **kwargs)

        for i, text in enumerate(wrap(info, 30), 2):
            menu.insert(i, text)

        for i in range(i + 1, MAX_ITEM_COUNT + 2):
            menu.insert(i, Text(' '))
    else:
        for i in range(2, MAX_ITEM_COUNT + 2):
            menu.insert(i, Text(' '))


@raceinfo_race_detail_menu.register_build_callback
def raceinfo_race_detail_menu_build(menu, client):
    del menu[2:-3]

    wcsplayer = Player(client)
    race_name = wcsplayer.data['_internal_raceinfo']
    settings = race_manager[race_name]

    menu[0].text.tokens['name'] = settings.strings['name']

    kwargs = {}

    settings.execute('on_race_desc', wcsplayer, kwargs)

    info = settings.strings['description']

    if info:
        info = info.get_string(get_client_language(client), **kwargs)

        for i, text in enumerate(wrap(info, 30), 2):
            menu.insert(i, text)

        for i in range(i + 1, MAX_ITEM_COUNT + 2):
            menu.insert(i, Text(' '))
    else:
        for i in range(2, MAX_ITEM_COUNT + 2):
            menu.insert(i, Text(' '))


@playerinfo_online_menu.register_build_callback
def playerinfo_online_menu_build(menu, client):
    menu.clear()

    for i, (_, wcsplayer) in enumerate(PlayerReadyIter(), 1):
        menu.insert(i, PagedOption(wcsplayer.name, wcsplayer.accountid))


@playerinfo_detail_menu.register_build_callback
def playerinfo_detail_menu_build(menu, client):
    wcsplayer = Player(client)
    wcstarget = Player.from_accountid(wcsplayer.data['_internal_playerinfo'])

    menu[7].selectable = menu[7].highlight = wcstarget.ready
    menu[8].selectable = menu[8].highlight = wcstarget.online

    if wcstarget.ready:
        active_race = wcstarget.active_race

        menu[0].text.tokens['name'] = wcstarget.name
        menu[1].text.tokens['race'] = active_race.settings.strings['name']
        menu[2].text.tokens['xp'] = active_race.xp
        menu[2].text.tokens['required'] = active_race.required_xp
        menu[2].text.tokens['rested_xp'] = wcstarget.rested_xp
        menu[3].text.tokens['level'] = active_race.level
        menu[3].text.tokens['total_level'] = wcstarget.total_level
        menu[5].text.tokens['value'] = strftime(TIME_FORMAT, localtime(wcstarget._lastconnect))
        menu[6].text.tokens['status'] = menu_strings['online' if wcstarget.online else 'offline']
    else:
        menu[0].text.tokens['name'] = wcsplayer.data['_internal_playerinfo_name']
        menu[1].text.tokens['race'] = -1
        menu[2].text.tokens['xp'] = -1
        menu[2].text.tokens['required'] = -1
        menu[2].text.tokens['rested_xp'] = -1
        menu[3].text.tokens['level'] = -1
        menu[3].text.tokens['total_level'] = -1
        menu[5].text.tokens['value'] = -1
        menu[6].text.tokens['status'] = -1

    menu[4].text.tokens['rank'] = wcstarget.rank
    menu[4].text.tokens['total_rank'] = len(rank_manager)


@playerinfo_detail_skills_menu.register_build_callback
def playerinfo_detail_skills_menu_build(menu, client):
    menu.clear()

    wcsplayer = Player(client)
    wcstarget = Player.from_accountid(wcsplayer.data['_internal_playerinfo'])

    if wcstarget.ready:
        menu.title.tokens['name'] = wcstarget.name

        active_race = wcstarget.active_race

        for name, skill in active_race.skills.items():
            option = Text(deepcopy(menu_strings['playerinfo_detail_skills_menu line']))
            option.text.tokens['name'] = active_race.settings.strings[name]
            option.text.tokens['level'] = skill.level
            option.text.tokens['maximum'] = skill.config['maximum']

            menu.append(option)
    else:
        menu.title.tokens['name'] = wcsplayer.data['_internal_playerinfo_name']


@playerinfo_detail_stats_menu.register_build_callback
def playerinfo_detail_stats_menu_build(menu, client):
    wcsplayer = Player.from_accountid(Player(client).data['_internal_playerinfo'])

    if wcsplayer.ready and wcsplayer.online:
        player = wcsplayer.player

        menu[0].text.tokens['name'] = player.name
        menu[2].text.tokens['value'] = player.health
        menu[3].text.tokens['value'] = player.armor
        menu[4].text.tokens['value'] = round(player.speed * 100, 1)
        menu[5].text.tokens['value'] = round(player.gravity * 100, 1)
        menu[6].text.tokens['value'] = round(100 - player.color.a / 2.55, 1)
    else:
        menu[0].text.tokens['name'] = wcsplayer.data['_internal_playerinfo_name']
        menu[2].text.tokens['value'] = -1
        menu[3].text.tokens['value'] = -1
        menu[4].text.tokens['value'] = -1
        menu[5].text.tokens['value'] = -1
        menu[6].text.tokens['value'] = -1


@wcstop_menu.register_build_callback
def wcstop_menu_build(menu, client):
    for option in _get_current_options(menu, client):
        option.text.tokens['rank'] = rank_manager.from_accountid(option.value)
        option.text.tokens['level'] = rank_manager._data[option.value]['total_level']


@wcstop_detail_menu.register_build_callback
def wcstop_detail_menu_build(menu, client):
    wcsplayer = Player(client)
    accountid = wcsplayer.data['_internal_wcstop']
    data = rank_manager._data[accountid]

    name = data['name']
    rank = rank_manager.from_accountid(accountid)
    total_level = data['total_level']
    current_race = data['current_race']

    menu[0].text.tokens['name'] = name
    menu[2].text.tokens['rank'] = rank
    menu[2].text.tokens['total'] = len(rank_manager)
    menu[3].text.tokens['level'] = total_level

    settings = race_manager.get(current_race, race_manager.get(race_manager.default_race, None))

    if settings is None:
        menu[4].text.tokens['name'] = current_race
    else:
        menu[4].text.tokens['name'] = settings.strings['name']


@levelbank_menu.register_build_callback
def levelbank_menu_build(menu, client):
    wcsplayer = Player(client)
    active_race = wcsplayer.active_race

    menu[0].text.tokens['bank_level'] = wcsplayer.bank_level
    menu[2].text.tokens['name'] = active_race.settings.strings['name']
    menu[2].text.tokens['level'] = active_race.level

    maximum_race_level = active_race.settings.config.get('maximum_race_level', 0)

    for i in range(3, 8):
        menu[i].selectable = menu[i].highlight = wcsplayer.bank_level >= menu[i].value and (not maximum_race_level or active_race.level + menu[i].value <= maximum_race_level)


@input_menu.register_build_callback
def input_menu_build(menu, client):
    wcsplayer = Player(client)
    repeat = wcsplayer.data['_internal_input_repeat']

    menu[1].text.tokens['duration'] = repeat.total_time_remaining


# ============================================================================
# >> ADMIN BUILD CALLBACKS
# ============================================================================
@wcsadmin_menu.register_build_callback
def wcsadmin_menu_build(menu, client):
    wcsplayer = Player(client)

    menu[2].selectable = menu[2].highlight = wcsplayer.privileges.get('wcsadmin_playersmanagement', False)
    menu[3].selectable = menu[3].highlight = wcsplayer.privileges.get('wcsadmin_managementaccess', False)
    menu[4].selectable = menu[4].highlight = wcsplayer.privileges.get('wcsadmin_githubaccess', False)


@wcsadmin_players_online_menu.register_build_callback
def wcsadmin_players_online_menu_build(menu, client):
    menu.clear()

    for i, (_, wcsplayer) in enumerate(PlayerReadyIter(), 2):
        menu.insert(i, PagedOption(wcsplayer.name, wcsplayer.accountid))


@wcsadmin_players_sub_menu.register_build_callback
def wcsadmin_players_sub_menu_build(menu, client):
    wcsplayer = Player(client)
    accountid = wcsplayer.data['_internal_wcsadmin_player']

    if accountid is None:
        menu[0].text.tokens['name'] = menu_strings['wcsadmin_players_menu all']
        menu[2].selectable = menu[2].highlight = True
        menu[3].selectable = menu[3].highlight = True

        menu[4] = Text(' ')
    else:
        wcstarget = Player.from_accountid(accountid)

        if wcstarget.ready:
            menu[0].text.tokens['name'] = wcstarget.name
        else:
            menu[0].text.tokens['name'] = wcsplayer.data['_internal_wcsadmin_player_name']

        menu[2].selectable = menu[2].highlight = wcstarget.ready
        menu[3].selectable = menu[3].highlight = wcstarget.ready

        menu[4] = SimpleOption(3, menu_strings['wcsadmin_players_sub_menu line 3'])
        menu[4].selectable = menu[4].highlight = wcstarget.ready and wcstarget.online


@wcsadmin_players_sub_xp_menu.register_build_callback
def wcsadmin_players_sub_xp_menu_build(menu, client):
    wcsplayer = Player(client)
    accountid = wcsplayer.data['_internal_wcsadmin_player']

    if accountid is None:
        menu[0].text.tokens['name'] = menu_strings['wcsadmin_players_menu all']
    else:
        wcstarget = Player.from_accountid(accountid)

        menu[0].text.tokens['name'] = wcstarget.name


@wcsadmin_players_sub_levels_menu.register_build_callback
def wcsadmin_players_sub_levels_menu_build(menu, client):
    wcsplayer = Player(client)
    accountid = wcsplayer.data['_internal_wcsadmin_player']

    if accountid is None:
        menu[0].text.tokens['name'] = menu_strings['wcsadmin_players_menu all']
    else:
        wcstarget = Player.from_accountid(accountid)

        menu[0].text.tokens['name'] = wcstarget.name


@wcsadmin_players_sub_changerace_menu.register_build_callback
def wcsadmin_players_sub_changerace_menu_build(menu, client):
    menu.clear()

    wcsplayer = Player(client)
    accountid = wcsplayer.data['_internal_wcsadmin_player']
    wcstarget = Player.from_accountid(accountid)

    menu.title.tokens['name'] = wcstarget.name

    for name in wcsplayer.data['_internal_wcsadmin_changerace']:
        option = PagedOption(race_manager[name].strings['name'], name)

        option.highlight = option.selectable = not wcstarget.current_race == name

        menu.append(option)


@wcsadmin_players_sub_bank_levels_menu.register_build_callback
def wcsadmin_players_sub_bank_levels_menu_build(menu, client):
    wcsplayer = Player(client)
    accountid = wcsplayer.data['_internal_wcsadmin_player']

    if accountid is None:
        menu[0].text.tokens['name'] = menu_strings['wcsadmin_players_menu all']
    else:
        wcstarget = Player.from_accountid(accountid)

        menu[0].text.tokens['name'] = wcstarget.name


@wcsadmin_management_races_menu.register_build_callback
def wcsadmin_management_races_menu_build(menu, client):
    if (CFG_PATH / 'races.json').isfile():
        with open(CFG_PATH / 'races.json') as inputfile:
            current_races = load(inputfile).get('races', [])
    else:
        current_races = []

    menu.clear()

    option = PagedOption(menu_strings['wcsadmin_management_races_menu add'])
    option.selectable = option.highlight = any(x for x in (x.basename() for x in RACE_PATH.listdir()) if x not in current_races and '_' + x not in current_races)
    menu.append(option)

    for value in current_races:
        menu.append(PagedOption(f'-{value[1:]}' if value.startswith('_') else value, value))


@wcsadmin_management_items_menu.register_build_callback
def wcsadmin_management_items_menu_build(menu, client):
    if (CFG_PATH / 'items.json').isfile():
        with open(CFG_PATH / 'items.json') as inputfile:
            current_items = load(inputfile).get('items', [])
    else:
        current_items = []

    menu.clear()

    option = PagedOption(menu_strings['wcsadmin_management_items_menu add'])
    option.selectable = option.highlight = any(x for x in (x.basename() for x in ITEM_PATH.listdir()) if x not in current_items and '_' + x not in current_items)
    menu.append(option)

    for value in current_items:
        menu.append(PagedOption(value, value))


@wcsadmin_management_races_add_menu.register_build_callback
def wcsadmin_management_races_add_menu_build(menu, client):
    if (CFG_PATH / 'races.json').isfile():
        with open(CFG_PATH / 'races.json') as inputfile:
            current_races = load(inputfile).get('races', [])
    else:
        current_races = []

    menu.clear()

    available_races = [x.basename() for x in RACE_PATH.listdir()]

    for value in [x for x in available_races if x not in current_races and '_' + x not in current_races]:
        menu.append(PagedOption(value, value))


@wcsadmin_management_items_add_menu.register_build_callback
def wcsadmin_management_items_add_menu_build(menu, client):
    if (CFG_PATH / 'items.json').isfile():
        with open(CFG_PATH / 'items.json') as inputfile:
            current_items = load(inputfile).get('items', [])
    else:
        current_items = []

    menu.clear()

    available_items = [x.basename() for x in ITEM_PATH.listdir()]

    for value in [x for x in available_items if x not in current_items and '_' + x not in current_items]:
        menu.append(PagedOption(value, value))


@wcsadmin_management_races_editor_menu.register_build_callback
def wcsadmin_management_races_editor_menu_build(menu, client):
    wcsplayer = Player(client)
    name = wcsplayer.data['_internal_wcsadmin_editor_value']

    menu[0].text.tokens['name'] = name[1:] if name.startswith('_') else name
    menu[2].text = menu_strings[f'wcsadmin_management_races_editor_menu toggle {int(name.startswith("_"))}']


@wcsadmin_management_items_editor_menu.register_build_callback
def wcsadmin_management_items_editor_menu_build(menu, client):
    wcsplayer = Player(client)
    name = wcsplayer.data['_internal_wcsadmin_editor_value']

    menu[0].text.tokens['name'] = name[1:] if name.startswith('_') else name
    menu[2].text = menu_strings[f'wcsadmin_management_items_editor_menu toggle {int(name.startswith("_"))}']


@wcsadmin_management_races_editor_modify_menu.register_build_callback
def wcsadmin_management_races_editor_modify_menu_build(menu, client):
    wcsplayer = Player(client)
    name = wcsplayer.data['_internal_wcsadmin_editor_value']
    actual_name = name[1:] if name.startswith('_') else name

    menu.title.tokens['name'] = actual_name

    with open(RACE_PATH / actual_name / 'config.json') as inputfile:
        config = load(inputfile)

    for i, key in enumerate(['required', 'maximum', 'restrictmap', 'restrictitem', 'restrictweapon', 'restrictteam', 'teamlimit', 'allowonly']):
        if i == 5:
            menu[i].text.tokens['value'] = menu_strings[f'wcsadmin_management_races_editor_modify_restricted_team_menu {config["restrictteam"]}']
        else:
            menu[i].text.tokens['value'] = config[key] if i in (0, 1, 6) else len(config[key])


@wcsadmin_management_races_editor_modify_from_selection_menu.register_build_callback
def wcsadmin_management_races_editor_modify_from_selection_menu_build(menu, client):
    wcsplayer = Player(client)
    name = wcsplayer.data['_internal_wcsadmin_editor_value']
    key = wcsplayer.data['_internal_wcsadmin_editor_key']
    actual_name = name[1:] if name.startswith('_') else name

    menu.title.tokens['name'] = actual_name

    del menu[1:]

    with open(RACE_PATH / actual_name / 'config.json') as inputfile:
        config = load(inputfile)

    for value in config[key]:
        menu.append(PagedOption(value, value))


@wcsadmin_management_races_editor_modify_restricted_team_menu.register_build_callback
def wcsadmin_management_races_editor_modify_restricted_team_menu_build(menu, client):
    wcsplayer = Player(client)
    name = wcsplayer.data['_internal_wcsadmin_editor_value']
    actual_name = name[1:] if name.startswith('_') else name

    menu[0].text.tokens['name'] = actual_name

    with open(RACE_PATH / actual_name / 'config.json') as inputfile:
        config = load(inputfile)

    menu[2].text.tokens['value'] = menu_strings[f'wcsadmin_management_races_editor_modify_restricted_team_menu {config["restrictteam"]}']
    menu[2].text.tokens['real_value'] = config['restrictteam']

    currently_selected_index = config['restrictteam'] + 2 if config['restrictteam'] else 3

    for index in (3, 4, 5):
        menu[index].selectable = menu[index].highlight = not index == currently_selected_index


@wcsadmin_github_races_menu.register_build_callback
def wcsadmin_github_races_menu_build(menu, client):
    if menu._cycle is not None:
        menu.description.tokens['cycle'] = '.' * (menu._cycle % 3 + 1)

        menu._cycle += 1


@wcsadmin_github_items_menu.register_build_callback
def wcsadmin_github_items_menu_build(menu, client):
    if menu._cycle is not None:
        menu.description.tokens['cycle'] = '.' * (menu._cycle % 3 + 1)

        menu._cycle += 1


@wcsadmin_github_races_options_menu.register_build_callback
def wcsadmin_github_races_options_menu_build(menu, client):
    wcsplayer = Player(client)

    name = wcsplayer.data['_internal_wcsadmin_github_name']

    git_option = github_manager['races'][name]
    status = git_option['status']

    menu[0].text.tokens['name'] = name

    menu[2].selectable = menu[2].highlight = status is GithubModuleStatus.UNINSTALLED
    menu[3].selectable = menu[3].highlight = status is GithubModuleStatus.INSTALLED
    menu[4].selectable = menu[4].highlight = status is GithubModuleStatus.INSTALLED

    menu[5].text = menu_strings[f'wcsadmin_github_options_menu status {status.value}']

    if status is not GithubModuleStatus.UNINSTALLED and not GithubModuleStatus.INSTALLED:
        cycle = wcsplayer.data.get('_internal_wcsadmin_github_cycle', 0)

        menu[5].text.tokens['cycle'] = '.' * (cycle % 3 + 1)

        cycle += 1

        wcsplayer.data['_internal_wcsadmin_github_cycle'] = cycle

    menu[6].text.tokens['repository'] = menu_strings['none'] if status is GithubModuleStatus.UNINSTALLED else git_option['repository']

    if git_option['last_updated'] is None:
        menu[7].text = menu_strings['wcsadmin_github_options_menu last updated never']
    else:
        menu[7].text = menu_strings['wcsadmin_github_options_menu last updated']
        menu[7].text.tokens['time'] = strftime(TIME_FORMAT, localtime(git_option['last_updated']))

    if len(git_option['repositories']) == 1:
        last_modified = git_option['repositories'][list(git_option['repositories'])[0]]['last_modified']

        if last_modified is None:
            menu[8].text.tokens['time'] = 0
        else:
            menu[8].text.tokens['time'] = strftime(TIME_FORMAT, localtime(last_modified))
    else:
        if git_option['repository'] is None:
            menu[8].text.tokens['time'] = 0
        else:
            menu[8].text.tokens['time'] = strftime(TIME_FORMAT, localtime(git_option['repositories'][git_option['repository']]['last_modified']))


@wcsadmin_github_races_repository_menu.register_build_callback
def wcsadmin_github_races_repository_menu_build(menu, client):
    menu.clear()

    wcsplayer = Player(client)

    name = wcsplayer.data['_internal_wcsadmin_github_name']

    menu.title.tokens['name'] = name

    git_option = github_manager['races'][name]

    for repository in git_option['repositories']:
        option = PagedOption(menu_strings['wcsadmin_github_races_repository_menu line'], repository)

        option.text.tokens['name'] = repository
        option.text.tokens['time'] = strftime(TIME_FORMAT, localtime(git_option['repositories'][repository]['last_modified']))

        menu.append(option)


@wcsadmin_github_items_options_menu.register_build_callback
def wcsadmin_github_items_options_menu_build(menu, client):
    wcsplayer = Player(client)

    name = wcsplayer.data['_internal_wcsadmin_github_name']

    git_option = github_manager['items'][name]
    status = git_option['status']

    menu[0].text.tokens['name'] = name

    menu[2].selectable = menu[2].highlight = status is GithubModuleStatus.UNINSTALLED
    menu[3].selectable = menu[3].highlight = status is GithubModuleStatus.INSTALLED
    menu[4].selectable = menu[4].highlight = status is GithubModuleStatus.INSTALLED

    menu[5].text = menu_strings[f'wcsadmin_github_options_menu status {status.value}']

    if status is not GithubModuleStatus.UNINSTALLED and not GithubModuleStatus.INSTALLED:
        cycle = wcsplayer.data.get('_internal_wcsadmin_github_cycle', 0)

        menu[5].text.tokens['cycle'] = '.' * (cycle % 3 + 1)

        cycle += 1

        wcsplayer.data['_internal_wcsadmin_github_cycle'] = cycle

    menu[6].text.tokens['repository'] = menu_strings['none'] if status is GithubModuleStatus.UNINSTALLED else git_option['repository']

    if git_option['last_updated'] is None:
        menu[7].text = menu_strings['wcsadmin_github_options_menu last updated never']
    else:
        menu[7].text = menu_strings['wcsadmin_github_options_menu last updated']
        menu[7].text.tokens['time'] = strftime(TIME_FORMAT, localtime(git_option['last_updated']))

    if len(git_option['repositories']) == 1:
        last_modified = git_option['repositories'][list(git_option['repositories'])[0]]['last_modified']

        if last_modified is None:
            menu[8].text.tokens['time'] = 0
        else:
            menu[8].text.tokens['time'] = strftime(TIME_FORMAT, localtime(last_modified))
    else:
        if git_option['repository'] is None:
            menu[8].text.tokens['time'] = 0
        else:
            menu[8].text.tokens['time'] = strftime(TIME_FORMAT, localtime(git_option['repositories'][git_option['repository']]['last_modified']))


@wcsadmin_github_items_repository_menu.register_build_callback
def wcsadmin_github_items_repository_menu_build(menu, client):
    menu.clear()

    wcsplayer = Player(client)

    name = wcsplayer.data['_internal_wcsadmin_github_name']

    menu.title.tokens['name'] = name

    git_option = github_manager['items'][name]

    for repository in git_option['repositories']:
        option = PagedOption(menu_strings['wcsadmin_github_items_repository_menu line'], repository)

        option.text.tokens['name'] = repository
        option.text.tokens['time'] = strftime(TIME_FORMAT, localtime(git_option['repositories'][repository]['last_modified']))

        menu.append(option)


@wcsadmin_github_info_menu.register_build_callback
def wcsadmin_github_info_menu_build(menu, client):
    if menu._checking_cycle is not None:
        menu[3].text.tokens['cycle'] = '.' * (menu._checking_cycle % 3 + 1)

        menu._checking_cycle += 1

    try:
        if menu._installing_cycle is not None:
            menu[4].text.tokens['cycle'] = '.' * (menu._installing_cycle % 3 + 1)

            menu._installing_cycle += 1
    except:
        pass


@wcsadmin_github_info_commits_menu.register_build_callback
def wcsadmin_github_info_commits_menu_build(menu, client):
    if menu._cycle is not None:
        menu[0].tokens['cycle'] = '.' * (menu._cycle % 3 + 1)

        menu._cycle += 1
