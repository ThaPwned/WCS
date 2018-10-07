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

# WCS Imports
#   Constants
from ..constants import ModuleType
from ..constants.paths import CFG_PATH
#   Helpers
from ..helpers.esc.commands import _aliases
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
    'parse_races',
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

            skills = settings.config['skills'] = {}

            skillnames = data['skillnames'].split('|')
            skilldescr = data['skilldescr'].split('|')
            skillcfg = data['skillcfg'].split('|')
            skillneeded = data['skillneeded'].split('|')
            numberoflevels = map(int, data['numberoflevels'].split('|')) if '|' in data['numberoflevels'] else [int(data['numberoflevels'])] * len(skillnames)

            for i, skill_name in enumerate(skillnames):
                fixed_skill_name = FIX_NAME.sub('', skill_name.lower().replace(' ', '_'))

                settings.strings[fixed_skill_name] = _LanguageString(skill_name)
                settings.strings[f'{fixed_skill_name} description'] = _LanguageString(skilldescr[i].replace(r'\n', ''))

                skill = skills[fixed_skill_name] = {}

                skill['event'] = skillcfg[i]

                skill['required'] = int(skillneeded[i])

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
