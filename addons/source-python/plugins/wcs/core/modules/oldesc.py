# ../wcs/core/modules/oldesc.py

# ============================================================================
# >> IMPORTS
# ============================================================================
# Python Imports
#   Collections
from collections import OrderedDict
#   Configobj
from configobj import ConfigObj
#   Re
from re import compile as re_compile
#   Warnings
from warnings import warn

# Source.Python Imports
#   Engines
from engines.server import queue_command_string
#   Keyvalues
from _keyvalues import KeyValues
# NOTE: Have to prefix it with a _ otherwise it'd import KeyValues from ES Emulator if it's loaded

# WCS Imports
#   Constants
from ..constants import ModuleType
from ..constants.paths import CFG_PATH
#   Helpers
from ..helpers.esc.commands import _aliases
from ..helpers.esc.commands import _languages
#   Modules
from .items.manager import ItemSetting
from .items.manager import item_manager
from .races.manager import RaceSetting
#   Translations
from ..translations import categories_strings


# ============================================================================
# >> ALL DECLARATION
# ============================================================================
__all__ = (
    'parse_items',
    'parse_items_old',
    'parse_races',
    'parse_races_old',
)


# ============================================================================
# >> GLOBAL VARIABLES
# ============================================================================
FIX_NAME = re_compile(r'\W')


# ============================================================================
# >> CLASSES
# ============================================================================
class ImportedRace(RaceSetting):
    def __init__(self, name):
        self.name = name
        self.type = ModuleType.ESS_OLD
        self.module = None

        self.config = {}
        self.strings = {}

        self.config['categories'] = []

        self.cmds = {}


class ImportedItem(ItemSetting):
    def __init__(self, name):
        self.name = name
        self.type = ModuleType.ESS_OLD
        self.module = None

        self.config = {}
        self.strings = {}

        self.config['categories'] = []

        self.cmds = {}


class _LanguageString(str):
    def get_string(self, *args, **kwargs):
        return self


# ============================================================================
# >> FUNCTIONS
# ============================================================================
def parse_races():
    races = OrderedDict()

    if (CFG_PATH / 'races.ini').isfile():
        imported = ConfigObj(CFG_PATH / 'races.ini')

        for name, data in imported.items():
            for alias, value in data.items():
                if alias.startswith('racealias_'):
                    _aliases[alias] = value

            fixed_name = FIX_NAME.sub('', name.lower().replace(' ', '_'))
            settings = races[fixed_name] = ImportedRace(fixed_name)

            settings.cmds['preloadcmd'] = data['preloadcmd']
            settings.cmds['roundstartcmd'] = data['roundstartcmd']
            settings.cmds['roundendcmd'] = data['roundendcmd']
            settings.cmds['spawncmd'] = data['spawncmd']
            settings.cmds['deathcmd'] = data['deathcmd']
            settings.cmds['changecmd'] = data['onchange']

            settings.config['required'] = int(data['required'])
            settings.config['maximum'] = int(data['maximum'])

            settings.config['restrictmap'] = data['restrictmap'].split('|') if data['restrictmap'] else []
            settings.config['restrictitem'] = data['restrictitem'].split('|') if data['restrictitem'] else []
            settings.config['restrictweapon'] = []
            settings.config['restrictteam'] = int(data['restrictteam'])
            settings.config['teamlimit'] = int(data.get('teamlimit', 0))

            settings.config['author'] = data['author']
            settings.config['allowonly'] = data['allowonly'].split('|') if data['allowonly'] else []

            skillnames = data['skillnames'].split('|')
            skilldescr = data['skilldescr'].split('|')
            skillcfg = data['skillcfg'].split('|')
            skillneeded = data['skillneeded'].split('|')
            numberoflevels = map(int, data['numberoflevels'].split('|')) if '|' in data['numberoflevels'] else [int(data['numberoflevels'])] * len(skillnames)

            skills = settings.config['skills'] = {}

            for i, skill_name in enumerate(skillnames):
                fixed_skill_name = FIX_NAME.sub('', skill_name.lower().replace(' ', '_'))

                settings.strings[fixed_skill_name] = _LanguageString(skill_name)
                settings.strings[f'{fixed_skill_name} description'] = _LanguageString(skilldescr[i].replace(r'\n', ''))

                skill = skills[fixed_skill_name] = {}

                skill['event'] = skillcfg[i]

                skill['required'] = [int(skillneeded[i])] * numberoflevels[i]

                if 'cooldown' in data[f'skill{i + 1}']:
                    skill['cooldown'] = list(map(lambda x: float(x) if '.' in x else int(x), data[f'skill{i + 1}']['cooldown'].split('|')))

                    if not len(skill['cooldown']) == numberoflevels[i]:
                        skill['cooldown'] = [skill['cooldown'][0]] * numberoflevels[i]

                skill['variables'] = {}

                skill['cmds'] = {}
                skill['cmds']['setting'] = data[f'skill{i + 1}']['setting'].split('|')

                if 'block' in data[f'skill{i + 1}']:
                    skill['cmds']['cmd'] = 'es_xdoblock ' + data[f'skill{i + 1}']['block']
                else:
                    skill['cmds']['cmd'] = data[f'skill{i + 1}']['cmd']

                skill['cmds']['sfx'] = data[f'skill{i + 1}']['sfx']

                count = len(data[f'skill{i + 1}']['setting'].split('|'))

                if count:
                    skill['maximum'] = count
                else:
                    skill['maximum'] = numberoflevels[i]

                for alias, value in data[f'skill{i + 1}'].items():
                    if alias.startswith('racealias_'):
                        _aliases[alias] = value

            settings.strings['name'] = _LanguageString(name)
            settings.strings['description'] = _LanguageString(data['desc'].replace(r'\n', ''))

            categories = (data['category'].split('|') if data['category'] and not data['category'] == '0' else []) if 'category' in data else []

            if categories:
                for category in categories:
                    if category == '0':
                        settings.add_to_category(None)
                        continue

                    fixed_category = FIX_NAME.sub('', category.lower().replace(' ', '_'))

                    if fixed_category not in categories_strings:
                        categories_strings[fixed_category] = _LanguageString(category)

                    settings.add_to_category(fixed_category)
            else:
                settings.add_to_category(None)

    return races


def parse_items():
    items = OrderedDict()

    if (CFG_PATH / 'items.ini').isfile():
        imported = ConfigObj(CFG_PATH / 'items.ini')

        for category in imported:
            fixed_category = FIX_NAME.sub('', category.lower().replace(' ', '_'))

            if fixed_category not in item_manager._category_max_items:
                item_manager._category_max_items[fixed_category] = int(imported[category]['maxitems'])

            if fixed_category not in categories_strings:
                categories_strings[fixed_category] = _LanguageString(category)

            for name, data in imported[category].items():
                if name not in ('desc', 'maxitems'):
                    for alias, value in data.items():
                        if alias.startswith('shopalias_'):
                            _aliases[alias] = value

                    fixed_name = FIX_NAME.sub('', name.lower().replace(' ', '_'))
                    settings = items[fixed_name] = ImportedItem(fixed_name)

                    settings.cmds['activatecmd'] = data['cmdactivate']
                    settings.cmds['buycmd'] = data['cmdbuy']

                    settings.config['cost'] = int(data['cost'])
                    settings.config['required'] = int(data['level'])
                    settings.config['dab'] = int(data['dab'])
                    settings.config['duration'] = int(data['duration'])
                    settings.config['count'] = int(data['max'])
                    settings.config['event'] = data['cfg']

                    settings.strings['name'] = _LanguageString(data['name'])
                    settings.strings['description'] = _LanguageString(data['desc'].replace(r'\n', ''))

                    settings.add_to_category(fixed_category)

    return items


def parse_races_old():
    races = OrderedDict()

    if (CFG_PATH / 'es_WCSraces_db.txt').isfile():
        def _get_string(text):
            if text.startswith('wcs_lng_r_'):
                if _languages:
                    return _languages['en'][text]

            return text

        imported = KeyValues.load_from_file(CFG_PATH / 'es_WCSraces_db.txt').as_dict()

        if not _languages:
            warn(f'Unable to find the "es_WCSlanguage_db" file.')

        for data in imported.values():
            for alias, value in data.items():
                if alias.startswith('racealias_'):
                    _aliases[alias] = value

            name = _get_string(data['name'])

            fixed_name = FIX_NAME.sub('', name.lower().replace(' ', '_'))
            settings = races[fixed_name] = ImportedRace(fixed_name)

            settings.cmds['preloadcmd'] = data['preloadcmd'] if data['preloadcmd'] else None
            settings.cmds['roundstartcmd'] = data['round_start_cmd'] if data['round_start_cmd'] else None
            settings.cmds['roundendcmd'] = data['round_end_cmd'] if data['round_end_cmd'] else None
            settings.cmds['spawncmd'] = data['player_spawn_cmd'] if data['player_spawn_cmd'] else None
            settings.cmds['deathcmd'] = None
            settings.cmds['changecmd'] = None

            settings.config['required'] = data['required_level']
            settings.config['maximum'] = data['maximum_level']

            settings.config['restrictmap'] = []
            settings.config['restrictitem'] = data['restrict_shop'].replace('<', '').split('>')[:-1] if 'restrict_shop' in data and data['restrict_shop'] else []
            settings.config['restrictweapon'] = []
            settings.config['restrictteam'] = None
            settings.config['teamlimit'] = data['teamlimit']

            settings.config['author'] = data['author']
            settings.config['allowonly'] = data['allow_only'].split('|') if data['allow_only'] else []

            skillnames = _get_string(data['skillnames']).split('|')
            skilldescr = _get_string(data['skilldescr']).split('|')
            skillcfg = data['skillcfg'].split('|')
            skillneeded = [8 if x == 'player_ultimate' else 0 for x in skillcfg]
            numberoflevels = data['numberoflevels']

            skills = settings.config['skills'] = {}

            for i, skill_name in enumerate(skillnames):
                fixed_skill_name = FIX_NAME.sub('', skill_name.lower().replace(' ', '_'))

                settings.strings[fixed_skill_name] = _LanguageString(skill_name)
                settings.strings[f'{fixed_skill_name} description'] = _LanguageString(skilldescr[i].replace(r'\n', ''))

                skill = skills[fixed_skill_name] = {}

                skill['event'] = skillcfg[i]

                if skillcfg[i] == 'player_ultimate':
                    skill['cooldown'] = [data['ultimate_cooldown']] * numberoflevels

                skill['required'] = [skillneeded[i]] * numberoflevels

                skill['variables'] = {}

                skill['cmds'] = {}
                skill['cmds']['setting'] = data[f'skill{i + 1}_setting'].split('|')
                skill['cmds']['cmd'] = data[f'skill{i + 1}_cmd']
                skill['cmds']['sfx'] = data[f'skill{i + 1}_sfx']

                skill['maximum'] = numberoflevels

            settings.strings['name'] = _LanguageString(name)
            settings.strings['description'] = _LanguageString(_get_string(data['shortdescription']).replace(r'\n', ''))

            settings.add_to_category(None)

    return races


def parse_items_old():
    items = OrderedDict()

    if (CFG_PATH / 'es_WCSshop_db.txt').isfile():
        def _get_string(text):
            if text.startswith('wcs_lng_s_'):
                if _languages:
                    return _languages['en'][text]

            return text

        imported = KeyValues.load_from_file(CFG_PATH / 'es_WCSshop_db.txt').as_dict()

        if not _languages:
            warn(f'Unable to find the "es_WCSlanguage_db" file.')

        if (CFG_PATH / 'es_WCSshop_cat_db.txt').isfile():
            categories = KeyValues.load_from_file(CFG_PATH / 'es_WCSshop_cat_db.txt').as_dict()
        else:
            warn(f'Unable to find the "es_WCSshop_cat_db" file.')
            categories = {}

        _convert = {}

        for number, data in categories.items():
            fixed_category = FIX_NAME.sub('', data['name'].lower().replace(' ', '_'))

            _convert[number] = fixed_category

            if fixed_category not in item_manager._category_max_items:
                # TODO: Maybe it'd be set to 3 by default?
                item_manager._category_max_items[fixed_category] = 999

            if fixed_category not in categories_strings:
                categories_strings[fixed_category] = _LanguageString(_get_string(data['name']))

        for name, data in imported.items():
            for alias, value in data.items():
                if alias.startswith('shopalias_'):
                    _aliases[alias] = value

            fixed_name = FIX_NAME.sub('', name.lower().replace(' ', '_'))
            settings = items[fixed_name] = ImportedItem(fixed_name)

            settings.cmds['activatecmd'] = data['cmdactivate']
            settings.cmds['buycmd'] = data['cmdbuy']

            settings.config['cost'] = int(data['cost'])
            settings.config['required'] = int(data['level'])
            settings.config['dab'] = int(data['dab'])
            settings.config['duration'] = int(data['duration'])
            settings.config['count'] = int(data['maxamount'])
            settings.config['event'] = data['itemconfig']

            settings.strings['name'] = _LanguageString(data['name'])
            settings.strings['description'] = _LanguageString(data['description'].replace(r'\n', ''))

            category = data['category']

            if isinstance(category, int):
                try:
                    settings.add_to_category(_convert[str(category)])
                except KeyError:
                    settings.add_to_category(None)
            else:
                settings.add_to_category(None)

    return items
