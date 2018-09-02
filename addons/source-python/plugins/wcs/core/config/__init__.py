# ../wcs/core/config/__init__.py

# ============================================================================
# >> IMPORTS
# ============================================================================
# Source.Python Imports
#   Config
from config.manager import ConfigManager

# WCS Imports
#   Constants
from ..constants.info import info
#   Translations
from ..translations import config_strings


# ============================================================================
# >> ALL DECLARATION
# ============================================================================
__all__ = (
    'cfg_bonus_xp',
    'cfg_default_race',
    'cfg_disable_text_on_level',
    'cfg_headshot_xp',
    'cfg_interval',
    'cfg_kill_xp',
    'cfg_knife_xp',
    'cfg_spawn_text',
    'cfg_top_announcement_enable',
    'cfg_top_min_rank_announcement',
    'cfg_top_public_announcement',
    'cfg_top_stolen_notify',
    'cfg_welcome_gui_text',
    'cfg_welcome_text',
)


# ============================================================================
# >> CONFIGURATION
# ============================================================================
# Create the configuration file
with ConfigManager(f'{info.name}/config.cfg', cvar_prefix=f'{info.name}_') as config:
    cfg_interval = config.cvar('interval', '80', config_strings['interval'])
    cfg_bonus_xp = config.cvar('bonus_xp', '4', config_strings['bonus_xp'])
    cfg_kill_xp = config.cvar('kill_xp', '20', config_strings['kill_xp'])
    cfg_knife_xp = config.cvar('knife_xp', '40', config_strings['knife_xp'])
    cfg_headshot_xp = config.cvar('headshot_xp', '15', config_strings['headshot_xp'])
    cfg_welcome_text = config.cvar('welcome_text', '0', config_strings['welcome_text'])
    cfg_welcome_gui_text = config.cvar('welcome_gui_text', '0', config_strings['welcome_gui_text'])
    cfg_spawn_text = config.cvar('spawn_text', '1', config_strings['spawn_text'])
    cfg_disable_text_on_level = config.cvar('disable_text_on_level', '20', config_strings['disable_text_on_level'])
    cfg_default_race = config.cvar('default_race', '', config_strings['default_race'])
    cfg_top_announcement_enable = config.cvar('top_announcement_enable', '1', config_strings['top_announcement_enable'])
    cfg_top_public_announcement = config.cvar('top_public_announcement', '1', config_strings['top_public_announcement'])
    cfg_top_min_rank_announcement = config.cvar('top_min_rank_announcement', '10', config_strings['top_min_rank_announcement'])
    cfg_top_stolen_notify = config.cvar('top_stolen_notify', '1', config_strings['top_stolen_notify'])
