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
#   Commands
from commands.server import ServerCommand
#   Cvars
from cvars import cvar
#   Engines
from engines.server import execute_server_command
#   Hooks
from hooks.exceptions import except_hooks
#   Keyvalues
from _keyvalues import KeyValues
# NOTE: Have to prefix it with a _ otherwise it'd import KeyValues from ES Emulator if it's loaded

# WCS Imports
#   Config
from ..config import cfg_debug_alias_duplicate
#   Constants
from ..constants import ModuleType
from ..constants.paths import CFG_PATH
#   Helpers
from ..helpers.esc.commands import _aliases
from ..helpers.esc.commands import _esc_strings
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
    'parse_ini_items',
    'parse_ini_races',
    'parse_key_items',
    'parse_key_races',
)


# ============================================================================
# >> GLOBAL VARIABLES
# ============================================================================
FIX_NAME = re_compile(r'\W')


# ============================================================================
# >> CLASSES
# ============================================================================
class ImportedRace(RaceSetting):
    def __init__(self, name, type_):
        self.name = name
        self.type = type_
        self.module = None

        self.config = {}
        self.strings = {}

        self.config['categories'] = []

        self.cmds = {}


class ImportedItem(ItemSetting):
    def __init__(self, name, type_):
        self.name = name
        self.type = type_
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
def parse_ini_races():
    races = OrderedDict()

    if (CFG_PATH / 'races.ini').isfile():
        imported = ConfigObj(CFG_PATH / 'races.ini')

        no_category = []

        for name, data in imported.items():
            for alias, value in data.items():
                if alias.startswith('racealias_'):
                    if alias in _aliases:
                        if cfg_debug_alias_duplicate.get_float():
                            warn(f'Alias "{alias}" is already registered')
                    else:
                        _aliases[alias] = value

            try:
                fixed_name = FIX_NAME.sub('', (name[8:] if name.startswith('wcs_lng_') else name).lower().replace(' ', '_'))

                settings = ImportedRace(fixed_name, ModuleType.ESS_INI)

                settings.cmds['preloadcmd'] = data['preloadcmd'] or None
                settings.cmds['roundstartcmd'] = data['roundstartcmd'] or None
                settings.cmds['roundendcmd'] = data['roundendcmd'] or None
                settings.cmds['spawncmd'] = data['spawncmd'] or None
                settings.cmds['deathcmd'] = data['deathcmd'] or None
                settings.cmds['changeintocmd'] = data.get('changeintocmd') or None
                settings.cmds['changefromcmd'] = data['onchange'] or None

                settings.config['required'] = int(data['required'])
                settings.config['maximum'] = int(data['maximum'])
                settings.config['maximum_race_level'] = int(data.get('maximum_race_level', 0))

                settings.config['restrictbot'] = int(data.get('restrictbot', 0))
                settings.config['restrictmap'] = data['restrictmap'].split('|') if data['restrictmap'] else []
                settings.config['restrictitem'] = data['restrictitem'].split('|') if data['restrictitem'] else []
                settings.config['restrictweapon'] = data['restrictweapon'].split('|') if 'restrictweapon' in data and data['restrictweapon'] else []
                settings.config['restrictteam'] = int(data['restrictteam'])
                settings.config['teamlimit'] = int(data.get('teamlimit', 0))

                settings.config['author'] = data['author']
                settings.config['allowonly'] = data['allowonly'].split('|') if data['allowonly'] else []

                skillnames = (_esc_strings[fixed_name][data['skillnames'][8:]].get_string('en') if data['skillnames'].startswith('wcs_lng_') else data['skillnames']).split('|')
                skilldescr = (_esc_strings[fixed_name][data['skilldescr'][8:]].get_string('en') if data['skilldescr'].startswith('wcs_lng_') else data['skilldescr']).split('|')
                skillcfg = data['skillcfg'].split('|')
                skillneeded = data['skillneeded'].split('|')
                numberoflevels = map(int, data['numberoflevels'].split('|')) if '|' in data['numberoflevels'] else [int(data['numberoflevels'])] * len(skillnames)

                skills = settings.config['skills'] = {}

                for i, skill_name in enumerate(skillnames):
                    fixed_skill_name = FIX_NAME.sub('', (skill_name[8:] if skill_name.startswith('wcs_lng_') else skill_name).lower().replace(' ', '_'))

                    settings.strings[fixed_skill_name] = _esc_strings[fixed_name][fixed_skill_name] if skill_name.startswith('wcs_lng_') else _LanguageString(skill_name)
                    settings.strings[f'{fixed_skill_name} description'] = _esc_strings[fixed_name][f'{fixed_skill_name} description'] if skilldescr[i].startswith('wcs_lng_') else _LanguageString(skilldescr[i].replace(r'\n', ''))

                    skill = skills[fixed_skill_name] = {}

                    skill['event'] = [skillcfg[i]]

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
                        cmd = data[f'skill{i + 1}']['cmd']
                        skill['cmds']['cmd'] = None if cmd == '0' else cmd

                    cmd = data[f'skill{i + 1}']['sfx']
                    skill['cmds']['sfx'] = None if cmd == '0' else cmd

                    count = len(data[f'skill{i + 1}']['setting'].split('|'))

                    if count:
                        skill['maximum'] = count
                    else:
                        skill['maximum'] = numberoflevels[i]

                    for alias, value in data[f'skill{i + 1}'].items():
                        if alias.startswith('racealias_'):
                            _aliases[alias] = value

                settings.strings['name'] = _esc_strings[fixed_name]['name'] if name.startswith('wcs_lng_') else _LanguageString(name)
                settings.strings['description'] = _esc_strings[fixed_name][data['desc'][8:]] if data['desc'].startswith('wcs_lng_') else _LanguageString(data['desc'].replace(r'\n', ''))
                settings.strings['shortname'] = settings.strings['name'] if data.get('shortname') is None else _esc_strings[fixed_name][data['shortname'][8:]] if data['shortname'].startswith('wcs_lng_') else _LanguageString(data['shortname'])

                categories = (data['category'].split('|') if data['category'] and not data['category'] == '0' else []) if 'category' in data else []

                if categories:
                    for category in categories:
                        if category == '0':
                            no_category.append(settings)
                            continue

                        fixed_category = FIX_NAME.sub('', category.lower().replace(' ', '_'))

                        if fixed_category not in categories_strings:
                            categories_strings[fixed_category] = _LanguageString(category)

                        settings.add_to_category(fixed_category)
                else:
                    no_category.append(settings)
            except:
                warn(f'Unable to properly parse the race "{name}" due to the following exception:')
                except_hooks.print_exception()
                continue
            else:
                races[fixed_name] = settings

        for settings in no_category:
            settings.add_to_category(None)

    return races


def parse_ini_items():
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
                            if alias in _aliases:
                                if cfg_debug_alias_duplicate.get_float():
                                    warn(f'Alias "{alias}" is already registered')
                            else:
                                _aliases[alias] = value

                    try:
                        fixed_name = FIX_NAME.sub('', name.lower().replace(' ', '_'))
                        settings = items[fixed_name] = ImportedItem(fixed_name, ModuleType.ESS_INI)

                        settings.cmds['activatecmd'] = data['cmdactivate']
                        settings.cmds['buycmd'] = data['cmdbuy']

                        settings.config['cost'] = int(data['cost'])
                        settings.config['required'] = int(data['level'])
                        settings.config['dab'] = int(data['dab'])
                        settings.config['duration'] = int(data['duration'])
                        settings.config['count'] = int(data['max'])
                        settings.config['event'] = [data['cfg']]

                        settings.strings['name'] = _LanguageString(data['name'])
                        settings.strings['description'] = _LanguageString(data['desc'].replace(r'\n', ''))

                        settings.add_to_category(fixed_category)
                    except:
                        warn(f'Unable to properly parse the item "{name}" due to the following exception:')
                        except_hooks.print_exception()
                        continue
                    else:
                        items[fixed_name] = settings

    return items


def parse_key_races():
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
                    if cvar.find_command(alias) is None:
                        ServerCommand(alias)(_command)

                        _aliases[alias] = value
                    else:
                        if cfg_debug_alias_duplicate.get_float():
                            warn(f'Alias "{alias}" is already registered')

            try:
                name = _get_string(data['name'])

                fixed_name = FIX_NAME.sub('', name.lower().replace(' ', '_'))
                settings = ImportedRace(fixed_name, ModuleType.ESS_KEY)

                settings.cmds['preloadcmd'] = data['preloadcmd'] or None
                settings.cmds['roundstartcmd'] = data['round_start_cmd'] or None
                settings.cmds['roundendcmd'] = data['round_end_cmd'] or None
                settings.cmds['spawncmd'] = data['player_spawn_cmd'] or None
                settings.cmds['deathcmd'] = data.get('deathcmd') or None
                settings.cmds['changeintocmd'] = data.get('changeintocmd') or None
                settings.cmds['changefromcmd'] = data.get('changefromcmd') or None

                settings.config['required'] = data['required_level']
                settings.config['maximum'] = data['maximum_level']
                settings.config['maximum_race_level'] = int(data.get('maximum_race_level', 0))

                settings.config['restrictbot'] = int(data.get('restrictbot', 0))
                settings.config['restrictmap'] = data['restrictmap'].split('|') if data.get('restrictmap') else []
                settings.config['restrictitem'] = data['restrict_shop'].replace('<', '').split('>')[:-1] if 'restrict_shop' in data and data['restrict_shop'] else []
                settings.config['restrictweapon'] = data['restrictweapon'].split('|') if data.get('restrictweapon') else []
                settings.config['restrictteam'] = int(data.get('restrictteam', 0))
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

                    skill['event'] = [skillcfg[i]]

                    if skillcfg[i] == 'player_ultimate':
                        skill['cooldown'] = [data['ultimate_cooldown']] * numberoflevels

                    skill['required'] = [skillneeded[i]] * numberoflevels

                    skill['variables'] = {}

                    skill['cmds'] = {}
                    skill['cmds']['setting'] = data[f'skill{i + 1}_setting'].split('|')

                    cmd = data[f'skill{i + 1}_cmd']
                    skill['cmds']['cmd'] = None if cmd == '0' else cmd

                    cmd = data[f'skill{i + 1}_sfx']
                    skill['cmds']['sfx'] = None if cmd == '0' else cmd

                    skill['maximum'] = numberoflevels

                settings.strings['name'] = _LanguageString(name)
                settings.strings['description'] = _LanguageString(_get_string(data['shortdescription']).replace(r'\n', '') if data['shortdescription'] else '')

                settings.add_to_category(None)
            except:
                warn(f'Unable to properly parse the race "{name}" due to the following exception:')
                except_hooks.print_exception()
                continue
            else:
                races[fixed_name] = settings

    return races


def parse_key_items():
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

        for data in categories.values():
            fixed_category = FIX_NAME.sub('', data['name'].lower().replace(' ', '_'))

            if fixed_category not in item_manager._category_max_items:
                # TODO: Maybe it'd be set to 3 by default?
                item_manager._category_max_items[fixed_category] = 999

            if fixed_category not in categories_strings:
                categories_strings[fixed_category] = _LanguageString(_get_string(data['name']))

            data['items'] = []
            data['id'] = fixed_category

        no_category = []

        for name, data in imported.items():
            for alias, value in data.items():
                if alias.startswith('shopalias_'):
                    if cvar.find_command(alias) is None:
                        ServerCommand(alias)(_command)

                        _aliases[alias] = value
                    else:
                        if cfg_debug_alias_duplicate.get_float():
                            warn(f'Alias "{alias}" is already registered')

            try:
                fixed_name = FIX_NAME.sub('', name.lower().replace(' ', '_'))
                settings = ImportedItem(fixed_name, ModuleType.ESS_KEY)

                settings.cmds['activatecmd'] = data['cmdactivate']
                settings.cmds['buycmd'] = data['cmdbuy']

                settings.config['cost'] = int(data['cost'])
                settings.config['required'] = int(data['level'])
                settings.config['dab'] = int(data['dab'])
                settings.config['duration'] = int(data['duration'])
                settings.config['count'] = int(data['maxamount'])
                settings.config['event'] = [data['itemconfig']]

                settings.strings['name'] = _LanguageString(_get_string(data['name']))
                settings.strings['description'] = _LanguageString(_get_string(data['description']).replace(r'\n', '') if data['description'] else '')

                if categories and isinstance(data['category'], int):
                    categories[str(data['category'])]['items'].append(settings)
                else:
                    no_category.append(settings)
            except:
                warn(f'Unable to properly parse the item "{name}" due to the following exception:')
                except_hooks.print_exception()
                continue
            else:
                items[fixed_name] = settings

        for data in categories.values():
            for settings in data['items']:
                settings.add_to_category(data['id'])

        for settings in no_category:
            settings.add_to_category(None)

    return items


def _command(command):
    alias = command.command_string.strip()

    if alias in _aliases:
        for cmd in _aliases[alias].split(';'):
            execute_server_command('es', cmd)
