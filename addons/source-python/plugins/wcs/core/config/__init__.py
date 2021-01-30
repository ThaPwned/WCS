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
    'cfg_bonus_bot_xp',
    'cfg_bonus_xp_level_cap',
    'cfg_default_race',
    'cfg_race_clan_tag',
    'cfg_disable_text_on_level',
    'cfg_headshot_xp',
    'cfg_headshot_bot_xp',
    'cfg_interval',
    'cfg_kill_xp',
    'cfg_kill_bot_xp',
    'cfg_knife_xp',
    'cfg_knife_bot_xp',
    'cfg_spawn_text',
    'cfg_hinttext_cooldown',
    'cfg_ffa_enabled',
    'cfg_changerace_next_round',
    'cfg_resetskills_next_round',
    'cfg_top_announcement_enable',
    'cfg_top_min_rank_announcement',
    'cfg_top_public_announcement',
    'cfg_top_stolen_notify',
    'cfg_welcome_gui_text',
    'cfg_welcome_text',
    'cfg_new_player_bank_bonus',
    'cfg_debug_alias_duplicate',
    'cfg_level_up_effect',
    'cfg_rank_gain_effect',
    'cfg_rested_xp_gained_base',
    'cfg_rested_xp_gained_percentage',
    'cfg_rested_xp_online_tick',
    'cfg_rested_xp_online_value',
    'cfg_rested_xp_offline_tick',
    'cfg_rested_xp_offline_value',
    'cfg_rested_xp_offline_duration',
    'cfg_assist_xp',
    'cfg_round_survival_xp',
    'cfg_round_win_xp',
    'cfg_bomb_plant_xp',
    'cfg_bomb_defuse_xp',
    'cfg_bomb_explode_xp',
    'cfg_hostage_rescue_xp',
    'cfg_bot_assist_xp',
    'cfg_bot_round_survival_xp',
    'cfg_bot_round_win_xp',
    'cfg_bot_bomb_plant_xp',
    'cfg_bot_bomb_explode_xp',
    'cfg_bot_bomb_defuse_xp',
    'cfg_bot_hostage_rescue_xp',
    'cfg_bot_ability_chance'
)


# ============================================================================
# >> CONFIGURATION
# ============================================================================
# Create the configuration file
with ConfigManager(f'{info.name}/config.cfg', cvar_prefix=f'{info.name}_') as config:
    cfg_interval = config.cvar('interval', '80', config_strings['interval'])
    cfg_bonus_xp = config.cvar('bonus_xp', '4', config_strings['bonus_xp'])
    cfg_bonus_bot_xp = config.cvar('bonus_bot_xp', '4', config_strings['bonus_bot_xp'])
    cfg_bonus_xp_level_cap = config.cvar('bonus_xp_level_cap', '0', config_strings['bonus_xp_level_cap'])
    cfg_kill_xp = config.cvar('kill_xp', '20', config_strings['kill_xp'])
    cfg_kill_bot_xp = config.cvar('kill_bot_xp', '20', config_strings['kill_bot_xp'])
    cfg_knife_xp = config.cvar('knife_xp', '40', config_strings['knife_xp'])
    cfg_knife_bot_xp = config.cvar('knife_bot_xp', '40', config_strings['knife_bot_xp'])
    cfg_headshot_xp = config.cvar('headshot_xp', '15', config_strings['headshot_xp'])
    cfg_headshot_bot_xp = config.cvar('headshot_bot_xp', '15', config_strings['headshot_bot_xp'])
    cfg_rested_xp_gained_base = config.cvar('rested_xp_gained_base', '10', config_strings['rested_xp_gained_base'])
    cfg_rested_xp_gained_percentage = config.cvar('rested_xp_gained_percentage', '0.01', config_strings['rested_xp_gained_percentage'])
    cfg_rested_xp_online_tick = config.cvar('rested_xp_online_tick', '60', config_strings['rested_xp_online_tick'])
    cfg_rested_xp_online_value = config.cvar('rested_xp_online_value', '1', config_strings['rested_xp_online_value'])
    cfg_rested_xp_offline_tick = config.cvar('rested_xp_offline_tick', '120', config_strings['rested_xp_offline_tick'])
    cfg_rested_xp_offline_value = config.cvar('rested_xp_offline_value', '1', config_strings['rested_xp_offline_value'])
    cfg_rested_xp_offline_duration = config.cvar('rested_xp_offline_duration', '604800', config_strings['rested_xp_offline_duration'])
    cfg_welcome_text = config.cvar('welcome_text', '0', config_strings['welcome_text'])
    cfg_welcome_gui_text = config.cvar('welcome_gui_text', '0', config_strings['welcome_gui_text'])
    cfg_new_player_bank_bonus = config.cvar('new_player_bank_bonus', '15', config_strings['new_player_bank_bonus'])
    cfg_debug_alias_duplicate = config.cvar('debug_alias_duplicate', '1', config_strings['debug_alias_duplicate'])
    cfg_level_up_effect = config.cvar('level_up_effect', '1', config_strings['level_up_effect'])
    cfg_rank_gain_effect = config.cvar('rank_gain_effect', '1', config_strings['rank_gain_effect'])
    cfg_spawn_text = config.cvar('spawn_text', '1', config_strings['spawn_text'])
    cfg_hinttext_cooldown = config.cvar('hinttext_cooldown', '0', config_strings['hinttext_cooldown'])
    cfg_ffa_enabled = config.cvar('ffa_enabled', '0', config_strings['ffa_enabled'])
    cfg_changerace_next_round = config.cvar('changerace_next_round', '0', config_strings['changerace_next_round'])
    cfg_resetskills_next_round = config.cvar('resetskills_next_round', '0', config_strings['resetskills_next_round'])
    cfg_disable_text_on_level = config.cvar('disable_text_on_level', '20', config_strings['disable_text_on_level'])
    cfg_default_race = config.cvar('default_race', '', config_strings['default_race'])
    cfg_race_clan_tag = config.cvar('race_clan_tag', '1', config_strings['race_clan_tag'])
    cfg_top_announcement_enable = config.cvar('top_announcement_enable', '1', config_strings['top_announcement_enable'])
    cfg_top_public_announcement = config.cvar('top_public_announcement', '1', config_strings['top_public_announcement'])
    cfg_top_min_rank_announcement = config.cvar('top_min_rank_announcement', '10', config_strings['top_min_rank_announcement'])
    cfg_top_stolen_notify = config.cvar('top_stolen_notify', '1', config_strings['top_stolen_notify'])
    cfg_bot_random_race = config.cvar('bot_random_race', '1', config_strings['bot_random_race'])
    cfg_unlock_race_notification = config.cvar('unlock_race_notification', '1', config_strings['unlock_race_notification'])
    cfg_assist_xp = config.cvar('assist_xp', '15', config_strings['assist_xp'])
    cfg_round_survival_xp = config.cvar('round_survival_xp', '10', config_strings['round_survival_xp'])
    cfg_round_win_xp = config.cvar('round_win_xp', '20', config_strings['round_win_xp'])
    cfg_bomb_plant_xp = config.cvar('bomb_plant_xp', '10', config_strings['bomb_plant_xp'])
    cfg_bomb_explode_xp = config.cvar('bomb_explode_xp', '10', config_strings['bomb_explode_xp'])
    cfg_bomb_defuse_xp = config.cvar('bomb_defuse_xp', '20', config_strings['bomb_defuse_xp'])
    cfg_hostage_rescue_xp = config.cvar('hostage_rescue_xp', '10', config_strings['hostage_rescue_xp'])
    cfg_bot_assist_xp = config.cvar('bot_assist_exp', '-1', config_strings['bot_assist_xp'])
    cfg_bot_round_survival_xp = config.cvar('bot_round_survival_xp', '-1', config_strings['bot_round_survival_xp'])
    cfg_bot_round_win_xp = config.cvar('bot_round_win_xp', '-1', config_strings['bot_round_win_xp'])
    cfg_bot_bomb_plant_xp = config.cvar('bot_bomb_plant_xp', '-1', config_strings['bot_bomb_plant_xp'])
    cfg_bot_bomb_explode_xp = config.cvar('bot_bomb_explode_xp', '-1', config_strings['bot_bomb_explode_xp'])
    cfg_bot_bomb_defuse_xp = config.cvar('bot_bomb_defuse_xp', '-1', config_strings['bot_bomb_defuse_xp'])
    cfg_bot_hostage_rescue_xp = config.cvar('bot_hostage_rescue_xp', '-1', config_strings['bot_hostage_rescue_xp'])
    cfg_bot_ability_chance = config.cvar('bot_ability_chance', '0.15', config_strings['bot_ability_chance'])
