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
#   Engines
from engines.server import global_vars
#   Menus
from menus import PagedOption
from menus import SimpleOption
from menus import Text
from menus.radio import MAX_ITEM_COUNT
#   Players
from players.helpers import get_client_language
#   Translations
from translations.strings import TranslationStrings

# WCS Imports
#   Constants
from ..constants import TIME_FORMAT
from ..constants import GithubStatus
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
from . import shopmenu_menu
from . import shopinfo_detail_menu
from . import showskills_menu
from . import spendskills_menu
from . import changerace_menu
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
from . import wcsadmin_menu
from . import wcsadmin_players_menu
from . import wcsadmin_players_sub_menu
from . import wcsadmin_players_sub_xp_menu
from . import wcsadmin_players_sub_levels_menu
from . import wcsadmin_management_races_menu
from . import wcsadmin_management_items_menu
from . import wcsadmin_management_races_add_menu
from . import wcsadmin_management_items_add_menu
from . import wcsadmin_management_races_editor_menu
from . import wcsadmin_management_items_editor_menu
from . import wcsadmin_github_races_options_menu
from . import wcsadmin_github_races_repository_menu
from . import wcsadmin_github_items_options_menu
from . import wcsadmin_github_items_repository_menu
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
def main_menu_build(menu, client):
    wcsplayer = Player.from_index(client)

    menu[1].selectable = menu[1].highlight = wcsplayer.ready and bool(item_manager)
    menu[2].selectable = menu[2].highlight = bool(item_manager)
    menu[4].selectable = menu[4].highlight = wcsplayer.ready
    menu[5].selectable = menu[5].highlight = wcsplayer.ready
    menu[6].selectable = menu[6].highlight = wcsplayer.ready and wcsplayer.unused > 0
    menu[8].selectable = menu[8].highlight = wcsplayer.ready and bool(race_manager) and (len(race_manager) > 1 or None not in race_manager)
    menu[9].selectable = menu[9].highlight = bool(race_manager) and (len(race_manager) > 1 or None not in race_manager)


@shopmenu_menu.register_build_callback
def shopmenu_menu_build(menu, client):
    wcsplayer = Player.from_index(client)

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
    wcsplayer = Player.from_index(client)
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
    info = info.get_string(get_client_language(client), **kwargs)

    for i, text in enumerate(wrap(info, 30), 5):
        menu.insert(i, text)

    for i in range(i + 1, MAX_ITEM_COUNT + 2):
        menu.insert(i, Text(' '))


@showskills_menu.register_build_callback
def showskills_menu_build(menu, client):
    menu.clear()

    wcsplayer = Player.from_index(client)
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

    wcsplayer = Player.from_index(client)
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
    wcsplayer = Player.from_index(client)

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
            elif reason is RaceReason.PRIVATE or reason is RaceReason.VIP:
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


@raceinfo_detail_menu.register_build_callback
def raceinfo_detail_menu_build(menu, client):
    wcsplayer = Player.from_index(client)
    name = wcsplayer.data['_internal_raceinfo']
    settings = race_manager[name]

    all_races = race_manager._category_to_values[wcsplayer.data.get('_internal_raceinfo_category')]

    if name not in all_races:
        all_races = race_manager._category_to_values[None]

    index = all_races.index(name)

    menu[0].text.tokens['name'] = settings.strings['name']
    menu[0].text.tokens['place'] = index + 1
    menu[0].text.tokens['total'] = len(all_races)
    menu[1].text.tokens['required'] = settings.config['required']
    menu[2].text.tokens['maximum'] = settings.config['maximum']
    menu[3].text.tokens['name'] = settings.config['author']

    if settings.config['allowonly']:
        if wcsplayer.uniqueid in settings.config['allowonly']:
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

    menu[7].selectable = menu[7].highlight = index != 0
    menu[8].selectable = menu[8].highlight = index != len(all_races) - 1


@raceinfo_skills_menu.register_build_callback
def raceinfo_skills_menu_build(menu, client):
    menu.clear()

    wcsplayer = Player.from_index(client)
    name = wcsplayer.data['_internal_raceinfo']
    settings = race_manager[name]

    menu.title.tokens['name'] = settings.strings['name']

    for name in settings.config['skills']:
        menu.append(PagedOption(settings.strings[name], name))


@raceinfo_skills_detail_menu.register_build_callback
def raceinfo_skills_detail_menu_build(menu, client):
    del menu[2:-3]

    wcsplayer = Player.from_index(client)
    race_name = wcsplayer.data['_internal_raceinfo']
    skill_name = wcsplayer.data['_internal_raceinfo_skill']
    settings = race_manager[race_name]

    menu[0].text.tokens['name'] = settings.strings['name']
    menu[1].text.tokens['name'] = settings.strings[skill_name]

    kwargs = {}

    settings.execute('on_skill_desc', wcsplayer, skill_name, kwargs)

    info = settings.strings[f'{skill_name} description']
    info = info.get_string(get_client_language(client), **kwargs)

    for i, text in enumerate(wrap(info, 30), 2):
        menu.insert(i, text)

    for i in range(i + 1, MAX_ITEM_COUNT + 2):
        menu.insert(i, Text(' '))


@raceinfo_race_detail_menu.register_build_callback
def raceinfo_race_detail_menu_build(menu, client):
    del menu[2:-3]

    wcsplayer = Player.from_index(client)
    race_name = wcsplayer.data['_internal_raceinfo']
    settings = race_manager[race_name]

    menu[0].text.tokens['name'] = settings.strings['name']

    kwargs = {}

    settings.execute('on_race_desc', wcsplayer, kwargs)

    info = settings.strings['description']
    info = info.get_string(get_client_language(client), **kwargs)

    for i, text in enumerate(wrap(info, 30), 2):
        menu.insert(i, text)

    for i in range(i + 1, MAX_ITEM_COUNT + 2):
        menu.insert(i, Text(' '))


@playerinfo_menu.register_build_callback
def playerinfo_menu_build(menu, client):
    stop = False

    for i, option in enumerate(menu):
        if isinstance(option, Text):
            if stop:
                del menu[1:i]
                break

            stop = True

    for i, (_, wcsplayer) in enumerate(PlayerReadyIter(), 1):
        menu.insert(i, PagedOption(wcsplayer.name, wcsplayer.uniqueid))


@playerinfo_detail_menu.register_build_callback
def playerinfo_detail_menu_build(menu, client):
    wcsplayer = Player.from_index(client)
    wcstarget = Player(wcsplayer.data['_internal_playerinfo'])

    menu[9].selectable = menu[9].highlight = wcstarget.ready
    menu[10].selectable = menu[10].highlight = wcstarget.online

    if wcstarget.ready:
        active_race = wcstarget.active_race

        menu[0].text.tokens['name'] = wcstarget.name
        menu[2].text.tokens['race'] = active_race.settings.strings['name']
        menu[3].text.tokens['xp'] = active_race.xp
        menu[3].text.tokens['required'] = active_race.required_xp
        menu[4].text.tokens['level'] = active_race.level
        menu[4].text.tokens['total_level'] = wcstarget.total_level
        menu[6].text.tokens['value'] = strftime(TIME_FORMAT, localtime(wcstarget._lastconnect))
        menu[7].text.tokens['status'] = menu_strings['yes' if wcstarget.online else 'no']
    else:
        menu[0].text.tokens['name'] = wcsplayer.data['_internal_playerinfo_name']
        menu[2].text.tokens['race'] = -1
        menu[3].text.tokens['xp'] = -1
        menu[3].text.tokens['required'] = -1
        menu[4].text.tokens['level'] = -1
        menu[4].text.tokens['total_level'] = -1
        menu[6].text.tokens['value'] = -1
        menu[7].text.tokens['status'] = -1

    menu[5].text.tokens['rank'] = wcstarget.rank
    menu[5].text.tokens['total_rank'] = len(rank_manager)


@playerinfo_detail_skills_menu.register_build_callback
def playerinfo_detail_skills_menu_build(menu, client):
    menu.clear()

    wcsplayer = Player.from_index(client)
    wcstarget = Player(wcsplayer.data['_internal_playerinfo'])

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
    wcsplayer = Player(Player.from_index(client).data['_internal_playerinfo'])

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
        option.text.tokens['rank'] = rank_manager[option.value]
        option.text.tokens['level'] = rank_manager._data[option.value]['total_level']


@wcstop_detail_menu.register_build_callback
def wcstop_detail_menu_build(menu, client):
    wcsplayer = Player.from_index(client)
    uniqueid = wcsplayer.data['_internal_wcstop']
    data = rank_manager._data[uniqueid]

    name = data['name']
    rank = rank_manager[uniqueid]
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


# ============================================================================
# >> ADMIN BUILD CALLBACKS
# ============================================================================
@wcsadmin_menu.register_build_callback
def wcsadmin_menu_build(menu, client):
    wcsplayer = Player.from_index(client)

    menu[2].selectable = menu[2].highlight = wcsplayer.privileges.get('wcsadmin_playersmanagement', False)
    menu[3].selectable = menu[3].highlight = wcsplayer.privileges.get('wcsadmin_managementaccess', False)
    menu[4].selectable = menu[4].highlight = wcsplayer.privileges.get('wcsadmin_githubaccess', False) and (github_manager['races'] or github_manager['items'])


@wcsadmin_players_menu.register_build_callback
def wcsadmin_players_menu_build(menu, client):
    stop = False

    for i, option in enumerate(menu):
        if isinstance(option, Text):
            if stop:
                del menu[2:i]
                break

            stop = True

    for i, (_, wcsplayer) in enumerate(PlayerReadyIter(), 2):
        menu.insert(i, PagedOption(wcsplayer.name, wcsplayer.uniqueid))


@wcsadmin_players_sub_menu.register_build_callback
def wcsadmin_players_sub_menu_build(menu, client):
    wcsplayer = Player.from_index(client)
    uniqueid = wcsplayer.data['_internal_wcsadmin_player']

    if uniqueid is None:
        menu[0].text.tokens['name'] = menu_strings['wcsadmin_players_menu all']
        menu[2].selectable = menu[2].highlight = True
        menu[3].selectable = menu[3].highlight = True

        menu[4] = Text(' ')
    else:
        wcstarget = Player(uniqueid)

        if wcstarget.ready:
            menu[0].text.tokens['name'] = wcstarget.name
        else:
            menu[0].text.tokens['name'] = wcsplayer.data['_internal_wcsadmin_player_name']

        menu[2].selectable = menu[2].highlight = wcstarget.ready
        menu[3].selectable = menu[3].highlight = wcstarget.ready
        menu[4].selectable = menu[4].highlight = wcstarget.ready

        menu[4] = SimpleOption(3, menu_strings['wcsadmin_players_sub_menu line 3'], selectable=False, highlight=False)


@wcsadmin_players_sub_xp_menu.register_build_callback
def wcsadmin_players_sub_xp_menu_build(menu, client):
    wcsplayer = Player.from_index(client)
    uniqueid = wcsplayer.data['_internal_wcsadmin_player']

    if uniqueid is None:
        menu[0].text.tokens['name'] = menu_strings['wcsadmin_players_menu all']
    else:
        wcstarget = Player(uniqueid)

        menu[0].text.tokens['name'] = wcstarget.name


@wcsadmin_players_sub_levels_menu.register_build_callback
def wcsadmin_players_sub_levels_menu_build(menu, client):
    wcsplayer = Player.from_index(client)
    uniqueid = wcsplayer.data['_internal_wcsadmin_player']

    if uniqueid is None:
        menu[0].text.tokens['name'] = menu_strings['wcsadmin_players_menu all']
    else:
        wcstarget = Player(uniqueid)

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
    wcsplayer = Player.from_index(client)
    name = wcsplayer.data['_internal_wcsadmin_editor_value']

    menu[0].text.tokens['name'] = name[1:] if name.startswith('_') else name
    menu[2].text = menu_strings[f'wcsadmin_management_races_editor_menu toggle {int(name.startswith("_"))}']


@wcsadmin_management_items_editor_menu.register_build_callback
def wcsadmin_management_items_editor_menu_build(menu, client):
    wcsplayer = Player.from_index(client)
    name = wcsplayer.data['_internal_wcsadmin_editor_value']

    menu[0].text.tokens['name'] = name[1:] if name.startswith('_') else name
    menu[2].text = menu_strings[f'wcsadmin_management_items_editor_menu toggle {int(name.startswith("_"))}']


@wcsadmin_github_races_options_menu.register_build_callback
def wcsadmin_github_races_options_menu_build(menu, client):
    wcsplayer = Player.from_index(client)

    name = wcsplayer.data['_internal_wcsadmin_github_name']

    git_option = github_manager['races'][name]
    status = git_option['status']

    menu[0].text.tokens['name'] = name

    menu[2].selectable = menu[2].highlight = status is GithubStatus.UNINSTALLED
    menu[3].selectable = menu[3].highlight = status is GithubStatus.INSTALLED
    menu[4].selectable = menu[4].highlight = status is GithubStatus.INSTALLED

    menu[5].text = menu_strings[f'wcsadmin_github_options_menu status {status.value}']

    if status is not GithubStatus.UNINSTALLED and not GithubStatus.INSTALLED:
        cycle = wcsplayer.data.get('_internal_wcsadmin_github_cycle', 0)

        menu[5].text.tokens['cycle'] = '.' * (cycle % 3 + 1)

        cycle += 1

        wcsplayer.data['_internal_wcsadmin_github_cycle'] = cycle

    if git_option['last_updated'] is None:
        menu[6].text = menu_strings['wcsadmin_github_options_menu last updated never']
    else:
        menu[6].text = menu_strings['wcsadmin_github_options_menu last updated']
        menu[6].text.tokens['time'] = strftime(TIME_FORMAT, localtime(git_option['last_updated']))

    if len(git_option['repositories']) == 1:
        menu[7].text.tokens['time'] = strftime(TIME_FORMAT, localtime(git_option['repositories'][list(git_option['repositories'])[0]]['last_modified']))
    else:
        if git_option['repository'] is None:
            menu[7].text.tokens['time'] = 0
        else:
            menu[7].text.tokens['time'] = strftime(TIME_FORMAT, localtime(git_option['repositories'][git_option['repository']]['last_modified']))


@wcsadmin_github_races_repository_menu.register_build_callback
def wcsadmin_github_races_repository_menu_build(menu, client):
    menu.clear()

    wcsplayer = Player.from_index(client)

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
    wcsplayer = Player.from_index(client)

    name = wcsplayer.data['_internal_wcsadmin_github_name']

    git_option = github_manager['items'][name]
    status = git_option['status']

    menu[0].text.tokens['name'] = name

    menu[2].selectable = menu[2].highlight = status is GithubStatus.UNINSTALLED
    menu[3].selectable = menu[3].highlight = status is GithubStatus.INSTALLED
    menu[4].selectable = menu[4].highlight = status is GithubStatus.INSTALLED

    menu[5].text = menu_strings[f'wcsadmin_github_options_menu status {status.value}']

    if status is not GithubStatus.UNINSTALLED and not GithubStatus.INSTALLED:
        cycle = wcsplayer.data.get('_internal_wcsadmin_github_cycle', 0)

        menu[5].text.tokens['cycle'] = '.' * (cycle % 3 + 1)

        cycle += 1

        wcsplayer.data['_internal_wcsadmin_github_cycle'] = cycle

    if git_option['last_updated'] is None:
        menu[6].text = menu_strings['wcsadmin_github_options_menu last updated never']
        menu[7].text.tokens['time'] = 0
    else:
        menu[6].text = menu_strings['wcsadmin_github_options_menu last updated']
        menu[6].text.tokens['time'] = strftime(TIME_FORMAT, localtime(git_option['last_updated']))

    if len(git_option['repositories']) == 1:
        menu[7].text.tokens['time'] = strftime(TIME_FORMAT, localtime(git_option['repositories'][list(git_option['repositories'])[0]]['last_modified']))
    else:
        if git_option['repository'] is None:
            menu[7].text.tokens['time'] = 0
        else:
            menu[7].text.tokens['time'] = strftime(TIME_FORMAT, localtime(git_option['repositories'][git_option['repository']]['last_modified']))


@wcsadmin_github_items_repository_menu.register_build_callback
def wcsadmin_github_items_repository_menu_build(menu, client):
    menu.clear()

    wcsplayer = Player.from_index(client)

    name = wcsplayer.data['_internal_wcsadmin_github_name']

    menu.title.tokens['name'] = name

    git_option = github_manager['items'][name]

    for repository in git_option['repositories']:
        option = PagedOption(menu_strings['wcsadmin_github_items_repository_menu line'], repository)

        option.text.tokens['name'] = repository
        option.text.tokens['time'] = strftime(TIME_FORMAT, localtime(git_option['repositories'][repository]['last_modified']))

        menu.append(option)
