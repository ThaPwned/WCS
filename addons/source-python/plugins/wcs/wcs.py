# ../wcs/wcs.py

# ============================================================================
# >> IMPORTS
# ============================================================================
# Python Imports
#   Collections
from collections import defaultdict
#   Copy
from copy import deepcopy
#   Enum
from enum import IntEnum
#   JSON
from json import load as json_load
#   Math
from math import floor
#   Random
from random import choice
#   Time
from time import sleep
from time import time

# Source.Python Imports
#   Commands
from commands import CommandReturn
from commands.client import ClientCommand
from commands.say import SayCommand
from commands.typed import TypedClientCommand
#   Colors
from colors import Color
#   Core
from core import GAME_NAME
from core import SOURCE_ENGINE_BRANCH
from core import OutputReturn
#   CVars
from cvars import cvar
#   Engines
from engines.precache import Model
from engines.server import global_vars
#   Entities
from entities.constants import MoveType
from entities.constants import RenderMode
from entities.entity import Entity
#   Events
from events import Event
from events.hooks import PreEvent
#   Filters
from filters.weapons import WeaponClassIter
#   Listeners
from listeners import OnConVarChanged
from listeners import OnLevelInit
from listeners import OnServerOutput
from listeners import OnTick
from listeners.tick import Delay
from listeners.tick import Repeat
from listeners.tick import RepeatStatus
#   Mathlib
from mathlib import QAngle
from mathlib import Vector
#   Messages
from messages import HintText
#   Players
from players.helpers import get_client_language
from players.helpers import index_from_userid
#   Weapons
from weapons.manager import weapon_manager

# WCS Imports
#   Config
from .core.config import cfg_bonus_xp
from .core.config import cfg_bonus_bot_xp
from .core.config import cfg_bonus_xp_level_cap
from .core.config import cfg_kill_xp
from .core.config import cfg_kill_bot_xp
from .core.config import cfg_knife_xp
from .core.config import cfg_knife_bot_xp
from .core.config import cfg_headshot_xp
from .core.config import cfg_headshot_bot_xp
from .core.config import cfg_rested_xp_gained_base
from .core.config import cfg_rested_xp_gained_percentage
from .core.config import cfg_rested_xp_online_tick
from .core.config import cfg_rested_xp_online_value
from .core.config import cfg_rested_xp_offline_tick
from .core.config import cfg_rested_xp_offline_value
from .core.config import cfg_rested_xp_offline_duration
from .core.config import cfg_welcome_text
from .core.config import cfg_welcome_gui_text
from .core.config import cfg_level_up_effect
from .core.config import cfg_rank_gain_effect
from .core.config import cfg_spawn_text
from .core.config import cfg_hinttext_cooldown
from .core.config import cfg_ffa_enabled
from .core.config import cfg_race_clan_tag
from .core.config import cfg_changerace_next_round
from .core.config import cfg_resetskills_next_round
from .core.config import cfg_disable_text_on_level
from .core.config import cfg_top_announcement_enable
from .core.config import cfg_top_public_announcement
from .core.config import cfg_top_min_rank_announcement
from .core.config import cfg_top_stolen_notify
from .core.config import cfg_bot_random_race
from .core.config import cfg_unlock_race_notification
from .core.config import cfg_assist_xp
from .core.config import cfg_round_survival_xp
from .core.config import cfg_round_win_xp
from .core.config import cfg_bomb_plant_xp
from .core.config import cfg_bomb_defuse_xp
from .core.config import cfg_bomb_explode_xp
from .core.config import cfg_hostage_rescue_xp
from .core.config import cfg_bot_assist_xp
from .core.config import cfg_bot_round_survival_xp
from .core.config import cfg_bot_round_win_xp
from .core.config import cfg_bot_bomb_plant_xp
from .core.config import cfg_bot_bomb_defuse_xp
from .core.config import cfg_bot_bomb_explode_xp
from .core.config import cfg_bot_hostage_rescue_xp
from .core.config import cfg_bot_ability_chance
#   Constants
from .core.constants import COMMANDS
from .core.constants import IS_ESC_SUPPORT_ENABLED
from .core.constants import ModuleType
from .core.constants import RaceReason
from .core.constants import SkillReason
from .core.constants.info import info
from .core.constants.paths import ITEM_PATH
from .core.constants.paths import RACE_PATH
#   Database
from .core.database.manager import database_manager
from .core.database.thread import _repeat
from .core.database.thread import _thread
#   Emulate
from .core.emulate import emulate_manager
#   Events
from .core.events import FakeEvent
from .core.events import _events
#   Helpers
from .core.helpers.github import github_manager
from .core.helpers.overwrites import SayText2
#   Listeners
from .core.listeners import OnGithubNewVersionChecked
from .core.listeners import OnGithubNewVersionInstalled
from .core.listeners import OnIsSkillExecutableText
from .core.listeners import OnPlayerChangeRace
from .core.listeners import OnPlayerDelete
from .core.listeners import OnPlayerDestroy
from .core.listeners import OnPlayerLevelUp
from .core.listeners import OnPlayerQuery
from .core.listeners import OnPlayerRankUpdate
from .core.listeners import OnPlayerReady
from .core.listeners import OnPluginUnload
from .core.listeners import OnSettingsLoaded
from .core.listeners import OnTakeDamageAlive
#   Menus
from .core.menus import shopmenu_menu
from .core.menus import shopinfo_menu
from .core.menus import showskills_menu
from .core.menus import resetskills_menu
from .core.menus import spendskills_menu
from .core.menus import changerace_menu
from .core.menus import changerace_search_menu
from .core.menus import raceinfo_menu
from .core.menus import raceinfo_search_menu
from .core.menus import raceinfo_detail_menu
from .core.menus import playerinfo_menu
from .core.menus import playerinfo_offline_menu
from .core.menus import playerinfo_detail_menu
from .core.menus import wcstop_menu
from .core.menus import levelbank_menu
from .core.menus import wcshelp_menu
from .core.menus import welcome_menu
from .core.menus import wcsadmin_menu
from .core.menus import wcsadmin_players_offline_menu
from .core.menus.base import PagedOption
from .core.menus.build import _get_current_options  # Just to load it
from .core.menus.close import raceinfo_menu_close  # Just to load it
from .core.menus.menus import main_menu  # Just to load it
from .core.menus.select import main_menu_select  # Just to load it
#   Modules
from .core.modules.items.manager import item_manager
from .core.modules.races.manager import race_manager
#   Players
from .core.players import _initialize_players
from .core.players import index_from_accountid
from .core.players import team_data
from .core.players.entity import Player
from .core.players.filters import PlayerIter
from .core.players.filters import PlayerReadyIter
#   Ranks
from .core.ranks import rank_manager
#   Translations
from .core.translations import chat_strings
from .core.translations import menu_strings

# Is ESC supported?
if IS_ESC_SUPPORT_ENABLED:
    #   Helpers
    from .core.helpers.esc.events import _execute_ability
    from .core.helpers.esc.monkeypatch import cmd_manager  # Just to load it
    #   Modules
    from .core.modules.oldesc import parse_ini_items
    from .core.modules.oldesc import parse_ini_races
    from .core.modules.oldesc import parse_key_items
    from .core.modules.oldesc import parse_key_races


# ============================================================================
# >> ALL DECLARATION
# ============================================================================
__all__ = ()


# ============================================================================
# >> GLOBAL VARIABLES
# ============================================================================
not_ready_message = SayText2(chat_strings['not ready'])
xp_required_message = SayText2(chat_strings['xp required'])
help_text_message = SayText2(chat_strings['help text'])
welcome_text_message = SayText2(chat_strings['welcome text'])
rested_xp_message = SayText2(chat_strings['rested xp'])
changerace_message = SayText2(chat_strings['changerace'])
changerace_warning_message = SayText2(chat_strings['changerace warning'])
no_race_found_message = SayText2(chat_strings['no race found'])
gain_xp_killed_message = SayText2(chat_strings['gain xp killed'])
gain_xp_killed_rested_message = SayText2(chat_strings['gain xp killed rested'])
gain_xp_killed_higher_level_message = SayText2(chat_strings['gain xp killed higher level'])
gain_xp_headshot_message = SayText2(chat_strings['gain xp headshot'])
gain_xp_knife_message = SayText2(chat_strings['gain xp knife'])
gain_xp_assist_message = SayText2(chat_strings['gain xp assist'])
gain_xp_round_survival_message = SayText2(chat_strings['gain xp round survival'])
gain_xp_round_win_message = SayText2(chat_strings['gain xp round win'])
gain_xp_bomb_plant_message = SayText2(chat_strings['gain xp bomb plant'])
gain_xp_bomb_defuse_message = SayText2(chat_strings['gain xp bomb defuse'])
gain_xp_bomb_explode_message = SayText2(chat_strings['gain xp bomb explode'])
gain_xp_hostage_rescue_message = SayText2(chat_strings['gain xp hostage rescue'])
gain_level_message = SayText2(chat_strings['gain level'])
maximum_level_message = SayText2(chat_strings['maximum level'])
force_change_team_message = SayText2(chat_strings['force change team'])
force_change_team_limit_message = SayText2(chat_strings['force change team limit'])
no_unused_message = SayText2(chat_strings['no unused'])
no_access_message = SayText2(chat_strings['no access'])
rank_message = SayText2(chat_strings['rank'])
show_xp_message = SayText2(chat_strings['show xp'])
skills_reset_message = SayText2(chat_strings['skills reset'])
unlock_race_notification_message = SayText2(chat_strings['unlock race notification'])
unlock_race_many_notification_message = SayText2(chat_strings['unlock race many notification'])
ability_team_message = SayText2(chat_strings['ability team'])
ability_dead_message = SayText2(chat_strings['ability dead'])
ability_deactivated_message = SayText2(chat_strings['ability deactivated'])
ability_cooldown_message = SayText2(chat_strings['ability cooldown'])
ability_level_message = SayText2(chat_strings['ability level'])
top_public_announcement_message = SayText2(chat_strings['top public announcement'])
top_private_announcement_message = SayText2(chat_strings['top private announcement'])
top_stolen_notify_message = SayText2(chat_strings['top stolen notify'])
admin_gain_xp_all_message = SayText2(chat_strings['admin gain xp all'])
admin_gain_xp_receiver_message = SayText2(chat_strings['admin gain xp receiver'])
admin_gain_xp_sender_message = SayText2(chat_strings['admin gain xp sender'])
admin_gain_xp_self_message = SayText2(chat_strings['admin gain xp self'])
admin_gain_levels_all_message = SayText2(chat_strings['admin gain levels all'])
admin_gain_levels_receiver_message = SayText2(chat_strings['admin gain levels receiver'])
admin_gain_levels_sender_message = SayText2(chat_strings['admin gain levels sender'])
admin_gain_levels_self_message = SayText2(chat_strings['admin gain levels self'])
github_new_version_message = SayText2(chat_strings['github new version'])
github_no_new_version_message = SayText2(chat_strings['github no new version'])
github_mod_update_message = SayText2(chat_strings['github mod update'])

hinttext_cooldown_message = HintText(menu_strings['hinttext_cooldown'])
hinttext_cooldown_ready_message = HintText(menu_strings['hinttext_cooldown ready'])

help_text_message.message.tokens['command'] = COMMANDS['wcshelp'][0]
welcome_text_message.message.tokens['command'] = COMMANDS['wcshelp'][0]
skills_reset_message.message.tokens['command'] = COMMANDS['spendskills'][0]

# "combinemuzzle1" is no where to be found but it's still complaining about late precache
_combinemuzzle1_model = Model('effects/combinemuzzle1.vmt', True)
_combinemuzzle2_model = Model('effects/combinemuzzle2.vmt', True)
_yellowflare_model = Model('effects/yellowflare.vmt', True)

_delays = defaultdict(set)
_melee_weapons = [weapon.basename for weapon in WeaponClassIter('melee')]
_new_version = None
_pre_ffa_enabled = {}
_block_player_hurt = False

_effect_angle = QAngle(0, 0, 0)
_level_effect_color = Color(252, 232, 131)
_rank_effect_color = Color(43, 145, 255)


# ============================================================================
# >> FUNCTIONS
# ============================================================================
def load():
    database_manager.connect()

    if IS_ESC_SUPPORT_ENABLED:
        race_manager.update(parse_ini_races())
        race_manager.update(parse_key_races())
        item_manager.update(parse_ini_items())
        item_manager.update(parse_key_items())

    race_manager.load_all()
    item_manager.load_all()

    # Get the current players on the server, as we want to ignore them when giving out rested xp
    for _, wcsplayer in PlayerIter():
        wcsplayer.data['_internal_rested_xp_prevent'] = True

    _initialize_players()

    for settings in race_manager.values():
        settings.execute('preloadcmd')

    for settings in item_manager.values():
        settings.execute('preloadcmd')

    if cfg_bot_ability_chance.get_float():
        emulate_manager.start()


def unload():
    _thread.unloading = True

    emulate_manager.stop()

    for _, wcsplayer in PlayerReadyIter():
        # Retrieve the player's original clan tag
        clan_tag = wcsplayer.data.pop('_internal_clan_tag', None)

        # Did they have a clan tag stored?
        if clan_tag is not None:
            # Restore the clan tag to what it was previously (add 4 spaces to fix a display issue)
            wcsplayer.player.clan_tag = ('    ' if GAME_NAME == 'csgo' else '') + clan_tag

        OnPlayerDelete.manager.notify(wcsplayer)

    for _, wcsplayer in PlayerReadyIter():
        wcsplayer.save()

    OnPluginUnload.manager.notify()

    github_manager.stop()

    race_manager.unload_all()
    item_manager.unload_all()

    database_manager.close()

    # I live life dangerously
    while _repeat.status == RepeatStatus.RUNNING:
        _thread._tick()
        sleep(0.01)


def _xp_gained(wcsplayer, active_race, old_level, value, rested_xp, delay, _allow=True):
    if rested_xp:
        gain_xp_killed_rested_message.send(wcsplayer.index, value=value, rested_xp=rested_xp)
    else:
        gain_xp_killed_message.send(wcsplayer.index, value=value)

    if active_race.level > old_level and _allow:
        gain_level_message.send(wcsplayer.index, level=active_race.level, xp=active_race.xp, required=active_race.required_xp)

    _delays[wcsplayer].remove(delay)


def _send_message_and_remove(message, wcsplayer, delay, **kwargs):
    message.send(wcsplayer.index, **kwargs)

    _delays[wcsplayer].remove(delay)


def _query_refresh_offline(result):
    playerinfo_offline_menu.clear()
    wcsadmin_players_offline_menu.clear()

    for accountid, name in result.fetchall():
        playerinfo_offline_menu.append(PagedOption(name, accountid))
        wcsadmin_players_offline_menu.append(PagedOption(name, accountid))


def _query_refresh_ranks(result):
    players = []

    for accountid, name, current_race, total_level in result.fetchall():
        if current_race not in race_manager:
            current_race = race_manager.default_race

        if accountid is None:
            accountid = name

        players.append((name, accountid))

        rank_manager._data[accountid] = {'name':name, 'current_race':current_race, 'total_level':total_level}

        option = PagedOption(deepcopy(menu_strings['wcstop_menu line']), accountid, show_index=False)
        option.text.tokens['name'] = name

        wcstop_menu.append(option)

        rank_manager.append(accountid)

    players.sort(key=lambda x: x[0] or '')

    for name, accountid in players:
        playerinfo_offline_menu.append(PagedOption(name, accountid))
        wcsadmin_players_offline_menu.append(PagedOption(name, accountid))


def _give_xp_if_set(userid, config, bot_config, message):
    if not 0 < userid <= global_vars.max_clients:
        return

    wcsplayer = Player.from_userid(userid)

    if not wcsplayer.ready:
        return

    if wcsplayer.fake_client:
        value = bot_config.get_int()

        if value == -1:
            value = config.get_int()
    else:
        value = config.get_int()

    if value:
        active_race = wcsplayer.active_race
        maximum_race_level = active_race.settings.config.get('maximum_race_level', 0)

        if maximum_race_level and active_race.level >= maximum_race_level:
            return

        if wcsplayer.fake_client:
            wcsplayer.xp += value
        else:
            active_race = wcsplayer.active_race

            old_level = active_race.level

            active_race.xp += value

            delay = Delay(1, _send_message_and_remove, (message, wcsplayer), {'value':value})
            delay.args += (delay, )
            _delays[wcsplayer].add(delay)

            if active_race.level > old_level:
                delay = Delay(1.01, _send_message_and_remove, (gain_level_message, wcsplayer), {'level':active_race.level, 'xp':active_race.xp, 'required':active_race.required_xp})
                delay.args += (delay, )
                _delays[wcsplayer].add(delay)


def _give_players_xp_if_set(wcsplayers, config, bot_config, message):
    value = config.get_int()
    bot_value = bot_config.get_int()

    if bot_value == -1:
        bot_value = value

    for _, wcsplayer in wcsplayers:
        active_race = wcsplayer.active_race
        maximum_race_level = active_race.settings.config.get('maximum_race_level', 0)

        if not maximum_race_level or active_race.level < maximum_race_level:
            if wcsplayer.fake_client:
                if bot_value:
                    wcsplayer.xp += bot_value
            else:
                if value:
                    old_level = active_race.level

                    active_race.xp += value

                    delay = Delay(1, _send_message_and_remove, (message, wcsplayer), {'value':value})
                    delay.args += (delay, )
                    _delays[wcsplayer].add(delay)

                    if active_race.level > old_level:
                        delay = Delay(1.01, _send_message_and_remove, (gain_level_message, wcsplayer), {'level':active_race.level, 'xp':active_race.xp, 'required':active_race.required_xp})
                        delay.args += (delay, )
                        _delays[wcsplayer].add(delay)


def _fire_post_player_spawn(wcsplayer, delay):
    with FakeEvent('post_player_spawn', userid=wcsplayer.userid) as event:
        wcsplayer.execute('postspawncmd', event)
        wcsplayer.notify(event)

    _delays[wcsplayer].remove(delay)

    # TODO: This should be in commands.py but whatever...
    wcsplayer.data.pop('evasion_count', None)


def _toggle_ffa(enable):
    if enable:
        for name, value in {
            'mp_teammates_are_enemies': 1,
            'mp_autokick': 0,
            'mp_tkpunish': 0,
            'mp_friendlyfire': 1,
            'ff_damage_reduction_bullets': 1,
            'ff_damage_reduction_grenade': 1,
            'ff_damage_reduction_other': 1
        }.items():
            variable = cvar.find_var(name)

            if variable is not None:
                _pre_ffa_enabled[name] = variable.get_int()

                variable.set_int(value)
    else:
        for name, value in _pre_ffa_enabled.items():
            cvar.find_var(name).set_int(value)

        _pre_ffa_enabled.clear()


def _update_player_clan_tag(wcsplayer, delay):
    # Change the clan tag to the player's current race (add 4 spaces to fix a display issue)
    wcsplayer.player.clan_tag = ('    ' if GAME_NAME == 'csgo' else '') + wcsplayer.active_race.settings.strings['shortname'].get_string()

    # Remove the delay from the container
    _delays[wcsplayer].remove(delay)


# ============================================================================
# >> EVENTS
# ============================================================================
@Event('round_start')
def round_start(event):
    item_manager._round_restart = False

    for _, wcsplayer in PlayerReadyIter(not_filters=['un', 'spec']):
        wcsplayer.execute('roundstartcmd', event, define=True)


@Event('round_end')
def round_end(event):
    item_manager._round_restart = True

    for _, wcsplayer in PlayerReadyIter(not_filters=['un', 'spec']):
        wcsplayer.execute('roundendcmd', event, define=True)

        for item in wcsplayer.items.values():
            if item.settings.config['duration'] == 0:
                item.count = 0

    winner = event['winner']

    if winner in (2, 3):
        _give_players_xp_if_set(PlayerReadyIter(['alive', 't' if winner == 3 else 'ct']), cfg_round_survival_xp, cfg_bot_round_survival_xp, gain_xp_round_survival_message)
        _give_players_xp_if_set(PlayerReadyIter('t' if winner == 2 else 'ct'), cfg_round_win_xp, cfg_bot_round_win_xp, gain_xp_round_win_message)


@Event('player_team')
def player_team(event):
    userid = event['userid']
    wcsplayer = Player.from_userid(userid)

    if wcsplayer.ready:
        team = event['team']
        oldteam = event['oldteam']

        key = f'_internal_{wcsplayer.current_race}_limit_allowed'

        # Remove the reservation from the old team
        if oldteam >= 2:
            team_data[oldteam][key].remove(userid)

            if not team_data[oldteam][key]:
                del team_data[oldteam][key]

        if team >= 2:
            # Start by adding the reservation to the new team (even if we shouldn't be allowed to be this race now)
            if key not in team_data[team]:
                team_data[team][key] = []
            if userid not in team_data[team][key]:
                team_data[team][key].append(userid)

            reason = RaceReason.ALLOWED

            # Is the race not allowed on this team?
            restrictteam = wcsplayer.active_race.settings.config.get('restrictteam')

            if restrictteam:
                if not restrictteam == team:
                    reason = RaceReason.TEAM

            # Are there too many players with this race on this team
            if reason is RaceReason.ALLOWED:
                teamlimit = wcsplayer.active_race.settings.config.get('teamlimit')

                if teamlimit:
                    limit = team_data[team].get(key, [])

                    # If there are now too many players with this race (fx. limit+1 if counting the switching player)
                    if len(limit) > teamlimit and userid not in limit:
                        reason = RaceReason.TEAM_LIMIT

            if reason is not RaceReason.ALLOWED:
                usable_races = wcsplayer.available_races

                for name in usable_races.copy():
                    config = race_manager[name].config

                    restrictteam = config.get('restrictteam')

                    if restrictteam:
                        if not restrictteam == team:
                            usable_races.remove(name)
                            continue

                    teamlimit = config.get('teamlimit')

                    if teamlimit:
                        limit = team_data[team].get(f'_internal_{name}_limit_allowed', [])

                        if teamlimit <= len(limit) and userid not in limit:
                            usable_races.remove(name)
                            continue

                if not usable_races:
                    wcsplayer._ready = False
                    wcsplayer._current_race = None

                    raise RuntimeError(f'Unable to find a usable race to "{wcsplayer.name}".')

                new_race = choice(usable_races)
                old_race = wcsplayer.current_race

                wcsplayer.current_race = new_race

                if reason is RaceReason.TEAM:
                    force_change_team_message.send(wcsplayer.index, old=race_manager[old_race].strings['name'], new=race_manager[new_race].strings['name'])
                else:
                    force_change_team_limit_message.send(wcsplayer.index, count=len(team_data[team][key]), old=race_manager[old_race].strings['name'], new=race_manager[new_race].strings['name'])

        # Update the clan tag 0.2 seconds later otherwise it won't be set
        delay = Delay(0.2, _update_player_clan_tag, (wcsplayer, ))
        delay.args += (delay, )
        _delays[wcsplayer].add(delay)


@Event('player_spawn')
def player_spawn(event):
    userid = event['userid']
    wcsplayer = Player.from_userid(userid)

    if wcsplayer.ready:
        if wcsplayer.player.team_index >= 2 or GAME_NAME in ('hl2mp', ):
            if not wcsplayer.fake_client:
                if cfg_resetskills_next_round.get_int():
                    if wcsplayer.data.pop('_internal_reset_skills', False):
                        for skill in wcsplayer.skills.values():
                            skill.level = 0

                        wcsplayer.unused = wcsplayer.level

                        skills_reset_message.send(wcsplayer.index, unused=wcsplayer.unused)

                if cfg_changerace_next_round.get_int():
                    new_race = wcsplayer.data.pop('_internal_race_change', None)

                    if new_race is not None:
                        if race_manager[new_race].usable_by(wcsplayer) is RaceReason.ALLOWED:
                            wcsplayer.current_race = new_race

                            changerace_message.send(wcsplayer.index, name=wcsplayer.active_race.settings.strings['name'])

                if cfg_spawn_text.get_int():
                    if wcsplayer.total_level <= cfg_disable_text_on_level.get_int():
                        help_text_message.send(wcsplayer.index)

                active_race = wcsplayer.active_race

                xp_required_message.send(wcsplayer.index, name=active_race.settings.strings['name'], level=active_race.level, xp=active_race.xp, required=active_race.required_xp)

            wcsplayer.execute('spawncmd', event)
            wcsplayer.notify(event)

            delay = Delay(0, _fire_post_player_spawn, (wcsplayer, ))
            delay.args += (delay, )
            _delays[wcsplayer].add(delay)


@Event('player_hurt')
def player_hurt(event):
    global _block_player_hurt

    if _block_player_hurt:
        _block_player_hurt = False
        return

    attacker = event['attacker']

    if attacker:
        if event['weapon'] not in ('point_hurt', 'worldspawn') and not event['weapon'].startswith('wcs_'):
            userid = event['userid']

            if not userid == attacker:
                wcsvictim = Player.from_userid(userid)
                wcsattacker = Player.from_userid(attacker)

                if wcsvictim.ready:
                    health = event['health']
                    ffa_enabled = cfg_ffa_enabled.get_int()

                    if ffa_enabled or not wcsvictim.player.team_index == wcsattacker.player.team_index:
                        wcsvictim.notify(event, 'player_victim')

                        if health > 0:
                            if wcsattacker.ready:
                                wcsattacker.notify(event, 'player_attacker')

                    wcsvictim.notify(event, 'player_hurt')

                    if health > 0:
                        if wcsattacker.ready:
                            wcsattacker.notify(event, 'player_hurt')


@PreEvent('player_hurt')
def pre_player_hurt(event):
    if _block_player_hurt:
        return

    attacker = event['attacker']

    if attacker:
        if event['weapon'] not in ('point_hurt', 'worldspawn') and not event['weapon'].startswith('wcs_'):
            userid = event['userid']

            if not userid == attacker:
                wcsvictim = Player.from_userid(userid)
                wcsattacker = Player.from_userid(attacker)

                if wcsvictim.ready:
                    health = event['health']
                    ffa_enabled = cfg_ffa_enabled.get_int()

                    if ffa_enabled or not wcsvictim.player.team_index == wcsattacker.player.team_index:
                        wcsvictim.notify(event, 'pre_player_victim')

                        if health > 0:
                            if wcsattacker.ready:
                                wcsattacker.notify(event, 'pre_player_attacker')

                    wcsvictim.notify(event, 'pre_player_hurt')

                    if health > 0:
                        if wcsattacker.ready:
                            wcsattacker.notify(event, 'pre_player_hurt')


@Event('player_death')
def player_death(event):
    userid = event['userid']
    attacker = event['attacker']

    wcsvictim = Player.from_userid(userid)

    if wcsvictim.ready:
        if not wcsvictim.data.pop('_internal_block_changerace_execution', False):
            wcsvictim.notify(event)

        wcsvictim.execute('deathcmd', event)

    if attacker:
        wcsattacker = Player.from_userid(attacker)

        if wcsattacker.ready:
            if not userid == attacker:
                wcsattacker.notify(event, 'player_kill')

                ffa_enabled = cfg_ffa_enabled.get_int()

                if ffa_enabled or not wcsvictim.player.team_index == wcsattacker.player.team_index:
                    active_race = wcsattacker.active_race
                    maximum_race_level = active_race.settings.config.get('maximum_race_level', 0)

                    if not maximum_race_level or active_race.level < maximum_race_level:
                        value = kill_xp = (cfg_kill_bot_xp if wcsvictim.fake_client else cfg_kill_xp).get_int()

                        if not event.is_empty('headshot') and event['headshot']:
                            headshot_xp = (cfg_headshot_bot_xp if wcsvictim.fake_client else cfg_headshot_xp).get_int()

                            if headshot_xp:
                                value += headshot_xp

                                if not wcsattacker.fake_client:
                                    delay = Delay(1, _send_message_and_remove, (gain_xp_headshot_message, wcsattacker), {'value':headshot_xp})
                                    delay.args += (delay, )
                                    _delays[wcsattacker].add(delay)

                        if wcsvictim.ready:
                            difference = wcsvictim.level - active_race.level

                            if difference > 0:
                                bonus_xp = (cfg_bonus_bot_xp if wcsvictim.fake_client else cfg_bonus_xp).get_int()

                                if bonus_xp:
                                    cap = cfg_bonus_xp_level_cap.get_int()

                                    gained = (min(cap, difference) if cap > 0 else difference) * bonus_xp
                                    value += gained

                                    if not wcsattacker.fake_client:
                                        delay = Delay(1, _send_message_and_remove, (gain_xp_killed_higher_level_message, wcsattacker), {'value':gained, 'difference':difference})
                                        delay.args += (delay, )
                                        _delays[wcsattacker].add(delay)

                        if event['weapon'] in _melee_weapons:
                            knife_xp = (cfg_knife_bot_xp if wcsvictim.fake_client else cfg_knife_xp).get_int()

                            if knife_xp:
                                value += knife_xp

                                if not wcsattacker.fake_client:
                                    delay = Delay(1, _send_message_and_remove, (gain_xp_knife_message, wcsattacker), {'value':knife_xp})
                                    delay.args += (delay, )
                                    _delays[wcsattacker].add(delay)

                        if value:
                            if not wcsattacker.fake_client:
                                rested_xp_gained_base = cfg_rested_xp_gained_base.get_int()
                                rested_xp_gained_percentage = cfg_rested_xp_gained_percentage.get_float()

                                rested_xp = min(rested_xp_gained_base, wcsattacker.rested_xp)

                                if rested_xp_gained_percentage > 0:
                                    rested_xp += floor((wcsattacker.rested_xp - rested_xp) * rested_xp_gained_percentage)

                                if rested_xp > 0:
                                    wcsattacker.rested_xp -= rested_xp
                                    value += rested_xp

                                for delay in _delays[wcsattacker]:
                                    if delay.callback is _xp_gained:
                                        delay.kwargs['_allow'] = False

                                # I want this to be the last one
                                delay = Delay(1.01, _xp_gained, (wcsattacker, active_race, active_race.level, kill_xp, rested_xp))
                                delay.args += (delay, )
                                _delays[wcsattacker].add(delay)

                            active_race.xp += value

    if wcsvictim.ready:
        for item in wcsvictim.items.values():
            if item.settings.config['duration'] == 1:
                item.count = 0

        # Is the victim a bot?
        if wcsvictim.fake_client:
            # Is the variable 'wcs_bot_random_race' enabled?
            if cfg_bot_random_race.get_int():
                # Gets the key as well as removes it from the dict (whether or not it should ignore random bot races)
                if not wcsvictim.data.pop('_internal_ignore_bot_random_race', False):
                    usable_races = wcsvictim.available_races

                    if wcsvictim.current_race in usable_races:
                        usable_races.remove(wcsvictim.current_race)

                    if usable_races:
                        wcsvictim.current_race = choice(usable_races)

    if not event.is_empty('assister'):
        assister = event['assister']

        try:
            index_from_userid(assister)
        except ValueError:
            pass
        else:
            _give_xp_if_set(assister, cfg_assist_xp, cfg_bot_assist_xp, gain_xp_assist_message)


@Event('player_say')
def player_say(event):
    userid = event['userid']

    if userid == 0:
        return  # The server is not a player :)

    wcsplayer = Player.from_userid(userid)

    if wcsplayer.ready:
        wcsplayer.notify(event)


@Event('bomb_planted')
def bomb_planted(event):
    _give_xp_if_set(event['userid'], cfg_bomb_plant_xp, cfg_bot_bomb_plant_xp, gain_xp_bomb_plant_message)


@Event('bomb_defused')
def bomb_defused(event):
    _give_xp_if_set(event['userid'], cfg_bomb_defuse_xp, cfg_bot_bomb_defuse_xp, gain_xp_bomb_defuse_message)


@Event('bomb_exploded')
def bomb_exploded(event):
    _give_xp_if_set(event['userid'], cfg_bomb_explode_xp, cfg_bot_bomb_explode_xp, gain_xp_bomb_explode_message)


@Event('hostage_rescued')
def hostage_rescued(event):
    _give_xp_if_set(event['userid'], cfg_hostage_rescue_xp, cfg_bot_hostage_rescue_xp, gain_xp_hostage_rescue_message)


@Event('player_jump')
def player_jump(event):
    userid = event['userid']
    wcsplayer = Player.from_userid(userid)

    if wcsplayer.ready:
        value = wcsplayer.data.get('longjump')

        if value is not None and value > 0:
            player = wcsplayer.player

            velocity = Vector(*player.get_property_vector('m_vecVelocity'))

            velocity[0] *= value
            velocity[1] *= value

            player.set_property_vector('m_vecBaseVelocity', velocity)


# ============================================================================
# >> LISTENERS
# ============================================================================
@OnConVarChanged
def on_con_var_changed(convar, old_value):
    # Is the variable that was changed 'wcs_ffa_enabled'?
    if convar.name == cfg_ffa_enabled.name:
        # This has to be delayed by a tick otherwise it'll crash the server
        Delay(0, _toggle_ffa, (convar.get_int(), ))
    # Is the variable that was changed 'wcs_race_clan_tag'?
    elif convar.name == cfg_race_clan_tag.name:
        # Is the current game CSS or CSGO?
        if GAME_NAME in ('cstrike', 'csgo'):
            # Is the variable set to enabled, and it's not already enabled?
            if old_value == '0' and cfg_race_clan_tag.get_float():
                # Loop through all players who's ready
                for player, wcsplayer in PlayerReadyIter():
                    # Store the original clan tag for later
                    wcsplayer.data['_internal_clan_tag'] = player.clan_tag

                    # Change the clan tag to the player's current race (add 4 spaces to fix a display issue)
                    player.clan_tag = ('    ' if GAME_NAME == 'csgo' else '') + wcsplayer.active_race.settings.strings['shortname'].get_string()
            # Is the variable set to disabled, and it's not already disabled?
            elif old_value != '0' and not cfg_race_clan_tag.get_float():
                # Loop through all players who's ready
                for player, wcsplayer in PlayerReadyIter():
                    # Retrieve the player's original clan tag
                    clan_tag = wcsplayer.data.pop('_internal_clan_tag', None)

                    # Did they have a clan tag stored?
                    if clan_tag is not None:
                        # Restore the clan tag to what it was previously (add 4 spaces to fix a display issue)
                        player.clan_tag = ('    ' if GAME_NAME == 'csgo' else '') + clan_tag



@OnLevelInit
def on_level_init(map_name):
    # Remove all offline players from the cache (better place for this?)
    Player._accountid_players.clear()

    for name in race_manager._refresh_config:
        settings = race_manager[name]

        with open(RACE_PATH / name / 'config.json') as inputfile:
            config = json_load(inputfile)

        for key in ['required', 'maximum', 'restrictmap', 'restrictitem', 'restrictweapon', 'restrictteam', 'teamlimit', 'allowonly']:
            if key in config:
                settings.config[key] = config[key]

    for name in item_manager._refresh_config:
        settings = item_manager[name]

        with open(ITEM_PATH / name / 'config.json') as inputfile:
            config = json_load(inputfile)

        for key in ['cost', 'required', 'duration', 'count']:
            if key in config:
                settings.config[key] = config[key]

    race_manager._refresh_config.clear()
    item_manager._refresh_config.clear()


# TODO: Should probably find a less demanding solution
@OnTick
def on_tick():
    for player, wcsplayer in PlayerReadyIter():
        new_value = player.move_type
        data = wcsplayer.data

        old_value = data.get('_internal_movetype')

        if new_value == old_value:
            if '_internal_gravity' not in data:
                data['_internal_gravity_holder'] = player.gravity
        else:
            if new_value == MoveType.WALK and old_value == MoveType.LADDER:
                player.gravity = data.pop('_internal_gravity')
            elif new_value == MoveType.LADDER:
                data['_internal_gravity'] = data.get('_internal_gravity_holder', 1.0)

        data['_internal_movetype'] = new_value


@OnGithubNewVersionChecked
def on_github_new_version_checked(version, commits):
    global _new_version

    _new_version = version

    for _, wcsplayer in PlayerReadyIter():
        if wcsplayer.privileges.get('wcsadmin'):
            if _new_version is None:
                github_no_new_version_message.send(wcsplayer.index)
            else:
                github_new_version_message.send(wcsplayer.index, new=version)


@OnGithubNewVersionInstalled
def on_github_new_version_installed():
    global _new_version

    if _new_version is not None:
        for _, wcsplayer in PlayerReadyIter():
            if wcsplayer.privileges.get('wcsadmin'):
                github_mod_update_message.send(wcsplayer.index, old=info.version, new=_new_version)

        _new_version = None


@OnPlayerChangeRace
def on_player_change_race(wcsplayer, old, new):
    if old in _events:
        _events[old]['counter'] -= 1

        if not _events[old]['counter']:
            for event in _events[old]['events']:
                event.unregister()

    if new in _events:
        _events[new]['counter'] += 1

        if _events[new]['counter'] == 1:
            for event in _events[new]['events']:
                event.register()

    # Is the current game CSS or CSGO?
    if GAME_NAME in ('cstrike', 'csgo'):
        # Are we allowed to change the clan tag?
        if cfg_race_clan_tag.get_int():
            # Change the clan tag to the player's current race (add 4 spaces to fix a display issue)
            wcsplayer.player.clan_tag = ('    ' if GAME_NAME == 'csgo' else '') + wcsplayer.active_race.settings.strings['shortname'].get_string()


@OnPlayerDelete
def on_player_delete(wcsplayer):
    if wcsplayer.ready:
        with FakeEvent('disconnectcmd', userid=wcsplayer.userid) as event:
            wcsplayer.execute(event.name, event)

        try:
            # Try to get the player's team
            team = wcsplayer.player.team
        except ValueError:
            key = f'_internal_{wcsplayer.current_race}_limit_allowed'

            # Let's just search for the player and remove them
            for team in team_data:
                if key in team_data[team]:
                    if wcsplayer.userid in team_data[team][key]:
                        team_data[team][key].remove(wcsplayer.userid)

                        if not team_data[team][key]:
                            del team_data[team][key]

                        break
        else:
            # Remove the player from the counter tracking the team limit for races
            if team >= 2:
                key = f'_internal_{wcsplayer.current_race}_limit_allowed'

                team_data[team][key].remove(wcsplayer.userid)

                if not team_data[team][key]:
                    del team_data[team][key]

        tick = cfg_rested_xp_online_tick.get_int()

        if tick > 0:
            value = cfg_rested_xp_online_value.get_int()

            now = time()

            rested_xp = floor((now - wcsplayer.data['_internal_rested_xp']) / tick * value)

            if rested_xp > 0:
                wcsplayer.rested_xp += rested_xp

    for delay in _delays.pop(wcsplayer, []):
        if delay.running:
            delay.cancel()

    wcsplayer.data.pop('_internal_rested_xp_prevent', None)


@OnPlayerDestroy
def on_player_destroy(wcsplayer):
    if wcsplayer.current_race in _events:
        _events[wcsplayer.current_race]['counter'] -= 1

        if not _events[wcsplayer.current_race]['counter']:
            for event in _events[wcsplayer.current_race]['events']:
                event.unregister()


@OnPlayerLevelUp
def on_player_level_up(wcsplayer, race, old_level):
    if wcsplayer.current_race == race.name:
        if not wcsplayer.fake_client:
            for skill in wcsplayer.skills.values():
                if skill.level < skill.config['maximum']:
                    delay = Delay(2, _send_message_and_remove, (spendskills_menu, wcsplayer))
                    delay.args += (delay, )
                    _delays[wcsplayer].add(delay)
                    break

        if cfg_level_up_effect.get_int():
            player = wcsplayer.player

            if not player.dead:
                origin = Vector(*player.origin)
                origin.z += 10

                entity = Entity.create('env_smokestack')
                entity.origin = origin
                entity.base_spread = 28
                entity.spread_speed = 10
                entity.initial_state = 0
                entity.speed = 10
                entity.start_size = 1
                entity.end_size = 7
                entity.rate = 173
                entity.jet_length = 13
                entity.render_color = _level_effect_color
                entity.render_mode = RenderMode.NONE
                entity.render_amt = 200
                entity.smoke_material = _combinemuzzle2_model.path
                entity.angles = _effect_angle
                entity.twist = 15

                entity.spawn()

                entity.set_parent(player)

                entity.add_output('OnUser1 !self,TurnOff,,3.5,1')
                entity.add_output('OnUser1 !self,Kill,,6,1')

                entity.call_input('TurnOn')
                entity.call_input('FireUser1', '1')

        if cfg_unlock_race_notification.get_int():
            new_total_level = wcsplayer.total_level
            old_total_level = new_total_level - (race.level - old_level)

            unlocked_races = [settings for settings in race_manager.values() if old_total_level < settings.config.get('required', 0) <= new_total_level]

            if unlocked_races:
                player = wcsplayer.player

                if SOURCE_ENGINE_BRANCH == 'csgo':
                    player.play_sound('ui/panorama/case_unlock_01.wav')
                    player.delay(1.6, player.play_sound, ('ui/panorama/item_showcase_knife_01.wav', ))
                    player.delay(2.1, player.play_sound, ('ui/panorama/case_awarded_4_legendary_01.wav', ))

                if len(unlocked_races) > 1:
                    player.delay(2.3, unlock_race_many_notification_message.send, (wcsplayer.index, ), {'count':len(unlocked_races)})
                else:
                    player.delay(2.3, unlock_race_notification_message.send, (wcsplayer.index, ), {'name':unlocked_races[0].strings['name']})


@OnPlayerQuery
def on_player_query(wcsplayer):
    if wcsplayer.current_race in _events:
        _events[wcsplayer.current_race]['counter'] += 1

        if _events[wcsplayer.current_race]['counter'] == 1:
            for event in _events[wcsplayer.current_race]['events']:
                event.register()


@OnPlayerRankUpdate
def on_player_rank_update(wcsplayer, old, new):
    if cfg_top_announcement_enable.get_int():
        min_rank = cfg_top_min_rank_announcement.get_int()

        if not min_rank or new + 1 <= min_rank:
            if cfg_top_public_announcement.get_int():
                top_public_announcement_message.send(name=wcsplayer.name, min_rank=min_rank if min_rank else '', old=old + 1, new=new + 1)
            else:
                if not wcsplayer.fake_client:
                    top_private_announcement_message.send(wcsplayer.index, min_rank=min_rank if min_rank else '', old=old + 1, new=new + 1)

        if new < old:
            if cfg_top_stolen_notify.get_int():
                for i, accountid in enumerate(rank_manager[new + 1:old + 1], 1):
                    try:
                        index = index_from_accountid(accountid)
                    except ValueError:
                        pass
                    else:
                        top_stolen_notify_message.send(index, name=wcsplayer.name, old=new + i, new=new + i + 1)

            if cfg_rank_gain_effect.get_int():
                player = wcsplayer.player

                if not player.dead:
                    origin = Vector(*player.origin)
                    origin.z -= 9

                    entity = Entity.create('env_smokestack')
                    entity.origin = origin
                    entity.base_spread = 24
                    entity.spread_speed = 6
                    entity.initial_state = 0
                    entity.speed = 68
                    entity.start_size = 2
                    entity.end_size = 4
                    entity.rate = 212
                    entity.jet_length = 82
                    entity.render_color = _rank_effect_color
                    entity.render_mode = RenderMode.NONE
                    entity.render_amt = 200
                    entity.smoke_material = _yellowflare_model.path
                    entity.angles = _effect_angle
                    entity.twist = 0

                    entity.spawn()

                    entity.set_parent(player)

                    entity.add_output('OnUser1 !self,TurnOff,,3.5,1')
                    entity.add_output('OnUser1 !self,Kill,,6,1')

                    entity.call_input('TurnOn')
                    entity.call_input('FireUser1', '1')


@OnPlayerReady
def on_player_ready(wcsplayer):
    if wcsplayer.player.team_index >= 2 or GAME_NAME in ('hl2mp', ):
        if not wcsplayer.fake_client:
            if cfg_spawn_text.get_int():
                if wcsplayer.total_level <= cfg_disable_text_on_level.get_int():
                    help_text_message.send(wcsplayer.index)

            active_race = wcsplayer.active_race

            xp_required_message.send(wcsplayer.index, name=active_race.settings.strings['name'], level=active_race.level, xp=active_race.xp, required=active_race.required_xp)

        wcsplayer.execute('readycmd', define=True)

    wcsplayer.data['_internal_rested_xp'] = time()

    # Is the current game CSS or CSGO?
    if GAME_NAME in ('cstrike', 'csgo'):
        # Are we allowed to change the clan tag?
        if cfg_race_clan_tag.get_int():
            # Store the original clan tag for later
            wcsplayer.data['_internal_clan_tag'] = wcsplayer.player.clan_tag

            # Change the clan tag to the player's current race (add 4 spaces to fix a display issue)
            wcsplayer.player.clan_tag = ('    ' if GAME_NAME == 'csgo' else '') + wcsplayer.active_race.settings.strings['shortname'].get_string()

    if not wcsplayer.fake_client:
        if wcsplayer.total_level <= cfg_disable_text_on_level.get_int():
            if cfg_welcome_text.get_int():
                delay = Delay(10, _send_message_and_remove, (welcome_text_message, wcsplayer))
                delay.args += (delay, )
                _delays[wcsplayer].add(delay)

            if cfg_welcome_gui_text.get_int():
                delay = Delay(5, _send_message_and_remove, (welcome_menu, wcsplayer))
                delay.args += (delay, )
                _delays[wcsplayer].add(delay)

        if wcsplayer.data.pop('_internal_rested_xp_prevent', None):
            return

        tick = cfg_rested_xp_offline_tick.get_int()

        if tick > 0:
            value = cfg_rested_xp_offline_value.get_int()
            duration = cfg_rested_xp_offline_duration.get_int()

            now = time()
            diff = now - wcsplayer.lastconnect

            if duration > 0:
                diff = min(diff, duration)

            rested_xp = floor(diff / tick * value)

            if rested_xp > 0:
                wcsplayer.rested_xp += rested_xp

                rested_xp_message.send(wcsplayer.index, value=rested_xp)


@OnSettingsLoaded
def on_settings_loaded(settings):
    # TODO: Please, PLEASE, tell me why this is near instant with "blocking=True"
    #       Without it, it takes 15+ seconds to complete for some servers
    #       (the location it takes this long is "self.cur.fetchall()" in thread.py)
    database_manager.execute('rank update', callback=_query_refresh_ranks, blocking=True)


@OnTakeDamageAlive
def on_take_damage_alive(wcsvictim, wcsattacker, info):
    if wcsattacker is not None:
        if wcsvictim is not wcsattacker:
            if wcsvictim.ready:
                if info.attacker == info.inflictor:
                    entity = wcsattacker.player.active_weapon
                else:
                    entity = Entity(info.inflictor)

                if entity is None:
                    return

                class_name = entity.class_name

                if class_name not in ('point_hurt', 'worldspawn') and not class_name.startswith('wcs_'):
                    try:
                        weapon_name = weapon_manager[class_name].basename
                    except KeyError:
                        weapon_name = class_name

                    health = wcsvictim.player.health - info.damage
                    ffa_enabled = cfg_ffa_enabled.get_int()

                    if ffa_enabled or not wcsvictim.player.team_index == wcsattacker.player.team_index:
                        with FakeEvent('pre_take_damage_victim', userid=wcsvictim.userid, attacker=wcsattacker.userid, weapon=weapon_name, info=info) as event:
                            wcsvictim.notify(event)

                        if health > 0:
                            if wcsattacker.ready:
                                with FakeEvent('pre_take_damage_attacker', userid=wcsvictim.userid, attacker=wcsattacker.userid, weapon=weapon_name, info=info) as event:
                                    wcsattacker.notify(event)

                    with FakeEvent('pre_take_damage_hurt', userid=wcsvictim.userid, attacker=wcsattacker.userid, weapon=weapon_name, info=info) as event:
                        wcsvictim.notify(event)

                    if health > 0:
                        if wcsattacker.ready:
                            with FakeEvent('pre_take_damage_hurt', userid=wcsvictim.userid, attacker=wcsattacker.userid, weapon=weapon_name, info=info) as event:
                                wcsattacker.notify(event)

    # TODO: This is ugly and need to be improved...
    if GAME_NAME in ('hl2mp', ):
        global _block_player_hurt

        event_args = {}
        event_args['userid'] = wcsvictim.userid
        event_args['attacker'] = 0 if wcsattacker is None else wcsattacker.userid
        event_args['health'] = wcsvictim.player.health - info.damage

        try:
            event_args['weapon'] = Entity(info.weapon).class_name
        except ValueError:
            event_args['weapon'] = Entity(info.inflictor).class_name

        _block_player_hurt = False

        with FakeEvent('player_hurt', **event_args) as event:
            pre_player_hurt(event)
            player_hurt(event)

        _block_player_hurt = True


# ============================================================================
# >> COMMANDS
# ============================================================================
@ClientCommand(COMMANDS['wcs'])
@SayCommand(COMMANDS['wcs'])
def say_command_wcs(command, index, team=None):
    main_menu.send(index)

    return CommandReturn.BLOCK


@ClientCommand(COMMANDS['shopmenu'])
@SayCommand(COMMANDS['shopmenu'])
def say_command_shopmenu(command, index, team=None):
    wcsplayer = Player(index)

    if wcsplayer.ready:
        shopmenu_menu.send(index)
    else:
        not_ready_message.send(index)

    return CommandReturn.BLOCK


@ClientCommand(COMMANDS['shopinfo'])
@SayCommand(COMMANDS['shopinfo'])
def say_command_shopinfo(command, index, team=None):
    shopinfo_menu.send(index)

    return CommandReturn.BLOCK


@ClientCommand(COMMANDS['showskills'])
@SayCommand(COMMANDS['showskills'])
def say_command_showskills(command, index, team=None):
    wcsplayer = Player(index)

    if wcsplayer.ready:
        showskills_menu.send(index)
    else:
        not_ready_message.send(index)

    return CommandReturn.BLOCK


@ClientCommand(COMMANDS['resetskills'])
@SayCommand(COMMANDS['resetskills'])
def say_command_resetskills(command, index, team=None):
    wcsplayer = Player(index)

    if wcsplayer.ready:
        resetskills_menu.send(index)
    else:
        not_ready_message.send(index)

    return CommandReturn.BLOCK


@ClientCommand(COMMANDS['spendskills'])
@SayCommand(COMMANDS['spendskills'])
def say_command_spendskills(command, index, team=None):
    wcsplayer = Player(index)

    if wcsplayer.ready:
        active_race = wcsplayer.active_race

        if active_race.unused > 0:
            if any([skill.level < skill.config['maximum'] for skill in active_race.skills.values()]):
                spendskills_menu.send(index)
            else:
                maximum_level_message.send(index)
        else:
            no_unused_message.send(index)
    else:
        not_ready_message.send(index)

    return CommandReturn.BLOCK


@ClientCommand(COMMANDS['changerace'])
@SayCommand(COMMANDS['changerace'])
def say_command_changerace(command, index, team=None):
    wcsplayer = Player(index)

    if wcsplayer.ready:
        search = command.arg_string.split()

        if search:
            found = []
            joined_search = ' '.join([x.lower() for x in search])
            language = get_client_language(index)

            for name, settings in race_manager.items():
                if joined_search == settings.strings['name'].get_string(language).lower():
                    if name not in found:
                        found.append(name)

            for name, settings in race_manager.items():
                if joined_search in settings.strings['name'].get_string(language).lower():
                    if name not in found:
                        found.append(name)

            for partial in [x.lower() for x in search]:
                for name, settings in race_manager.items():
                    if partial in settings.strings['name'].get_string(language).lower():
                        if name not in found:
                            found.append(name)

            if found:
                if not cfg_changerace_next_round.get_int():
                    changerace_warning_message.send(index)

                wcsplayer.data['_internal_changerace_search'] = found

                changerace_search_menu.send(index)
            else:
                no_race_found_message.send(index, search=' '.join(search))
        else:
            if not cfg_changerace_next_round.get_int():
                changerace_warning_message.send(index)

            changerace_menu.send(index)
    else:
        not_ready_message.send(index)

    return CommandReturn.BLOCK


@ClientCommand(COMMANDS['raceinfo'])
@SayCommand(COMMANDS['raceinfo'])
def say_command_raceinfo(command, index, team=None):
    search = command.arg_string.split()

    if search:
        found = []
        joined_search = ' '.join([x.lower() for x in search])
        language = get_client_language(index)

        for name, settings in race_manager.items():
            if joined_search == settings.strings['name'].get_string(language).lower():
                if name not in found:
                    found.append(name)

        for name, settings in race_manager.items():
            if joined_search in settings.strings['name'].get_string(language).lower():
                if name not in found:
                    found.append(name)

        for partial in [x.lower() for x in search]:
            for name, settings in race_manager.items():
                if partial in settings.strings['name'].get_string(language).lower():
                    if name not in found:
                        found.append(name)

        if found:
            Player(index).data['_internal_raceinfo_search'] = found

            raceinfo_search_menu.send(index)
        else:
            no_race_found_message.send(index, search=' '.join(search))
    else:
        raceinfo_menu.send(index)

    return CommandReturn.BLOCK


@ClientCommand(COMMANDS['myraceinfo'])
@SayCommand(COMMANDS['myraceinfo'])
def say_command_myraceinfo(command, index, team=None):
    wcsplayer = Player(index)

    if wcsplayer.ready:
        categories = race_manager[wcsplayer.current_race].config['categories']

        wcsplayer.data['_internal_raceinfo'] = wcsplayer.current_race
        wcsplayer.data['_internal_raceinfo_category'] = categories[0] if categories else None

        raceinfo_detail_menu.send(index)
    else:
        not_ready_message.send(index)

    return CommandReturn.BLOCK


@ClientCommand(COMMANDS['playerinfo'])
@SayCommand(COMMANDS['playerinfo'])
def say_command_playerinfo(command, index, team=None):
    playerinfo_menu.send(index)

    return CommandReturn.BLOCK


@ClientCommand(COMMANDS['myinfo'])
@SayCommand(COMMANDS['myinfo'])
def say_command_myinfo(command, index, team=None):
    wcsplayer = Player(index)

    if wcsplayer.ready:
        wcsplayer.data['_internal_playerinfo'] = wcsplayer.accountid
        wcsplayer.data['_internal_playerinfo_name'] = wcsplayer.name

        playerinfo_detail_menu.send(index)
    else:
        not_ready_message.send(index)

    return CommandReturn.BLOCK


@ClientCommand(COMMANDS['wcstop'])
@SayCommand(COMMANDS['wcstop'])
def say_command_wcstop(command, index, team=None):
    wcstop_menu.send(index)

    return CommandReturn.BLOCK


@ClientCommand(COMMANDS['wcsrank'])
@SayCommand(COMMANDS['wcsrank'])
def say_command_wcsrank(command, index, team=None):
    wcsplayer = Player(index)

    if wcsplayer.ready:
        active_race = wcsplayer.active_race

        rank_message.send(name=wcsplayer.name, race=active_race.settings.strings['name'], level=active_race.level, total_level=wcsplayer.total_level, xp=active_race.xp, required=active_race.required_xp, rank=wcsplayer.rank, total=len(rank_manager))
    else:
        not_ready_message.send(index)

    return CommandReturn.BLOCK


@ClientCommand(COMMANDS['wcshelp'])
@SayCommand(COMMANDS['wcshelp'])
def say_command_wcshelp(command, index, team=None):
    wcshelp_menu.send(index)

    return CommandReturn.BLOCK


@ClientCommand(COMMANDS['wcsadmin'])
@SayCommand(COMMANDS['wcsadmin'])
def say_command_wcsadmin(command, index, team=None):
    wcsplayer = Player(index)

    if wcsplayer.privileges.get('wcsadmin', False):
        wcsadmin_menu.send(index)
    else:
        no_access_message.send(index)

    return CommandReturn.BLOCK


@ClientCommand(COMMANDS['showxp'])
@SayCommand(COMMANDS['showxp'])
def say_command_showxp(command, index, team=None):
    wcsplayer = Player(index)

    if wcsplayer.ready:
        active_race = wcsplayer.active_race

        show_xp_message.send(wcsplayer.index, name=active_race.settings.strings['name'], level=active_race.level, total_level=wcsplayer.total_level, xp=active_race.xp, required=active_race.required_xp)
    else:
        not_ready_message.send(index)

    return CommandReturn.BLOCK


@ClientCommand(COMMANDS['levelbank'])
@SayCommand(COMMANDS['levelbank'])
def say_command_levelbank(command, index, team=None):
    wcsplayer = Player(index)

    if wcsplayer.ready:
        levelbank_menu.send(index)
    else:
        not_ready_message.send(index)

    return CommandReturn.BLOCK


@TypedClientCommand('+ability')
def client_ability_plus_command(command, ability:int=1, *args:str):
    wcsplayer = Player(command.index)

    if wcsplayer.ready:
        # TODO: Monkeypatch until it's been fixed in SP (don't create a race with 32 abilities, please)
        if ability == 32:
            ability = 1

        active_race = wcsplayer.active_race

        i = 1

        for skill_name in active_race.settings.config['skills']:
            skill = active_race.skills[skill_name]

            if 'player_ability_on' in skill.config['event']:
                if ability == i:
                    reason = skill.is_executable()

                    if reason is SkillReason.ALLOWED:
                        wcsplayer.data[f'_internal_ability_{i}'] = True

                        with FakeEvent('player_ability_on' if skill._type is ModuleType.SP else f'{skill_name}_on', userid=wcsplayer.userid) as event:
                            skill.execute(event.name, event)
                    elif reason is SkillReason.TEAM:
                        ability_team_message.send(command.index)
                    elif reason is SkillReason.DEAD:
                        ability_dead_message.send(command.index)
                    elif reason is SkillReason.DEACTIVATED:
                        ability_deactivated_message.send(command.index)
                    elif reason is SkillReason.COOLDOWN:
                        ability_cooldown_message.send(command.index, cooldown=skill.cooldown_seconds, left=skill.cooldown - time())
                    elif reason is SkillReason.LEVEL:
                        ability_level_message.send(command.index)
                    elif isinstance(reason, IntEnum):
                        data = {'reason':reason}

                        OnIsSkillExecutableText.manager.notify(wcsplayer, skill, data)
                    else:
                        raise ValueError(f'Invalid reason: {reason}')

                    break

                i += 1

    return CommandReturn.BLOCK


@TypedClientCommand('-ability')
def client_ability_minus_command(command, ability:int=1, *args:str):
    wcsplayer = Player(command.index)

    if wcsplayer.ready:
        # TODO: Monkeypatch until it's been fixed in SP (don't create a race with 32 abilities, please)
        if ability == 32:
            ability = 1

        active_race = wcsplayer.active_race

        i = 1

        for skill_name in active_race.settings.config['skills']:
            skill = active_race.skills[skill_name]

            if 'player_ability_off' in skill.config['event'] or 'player_ability_on' in skill.config['event']:
                if ability == i:
                    if wcsplayer.data.pop(f'_internal_ability_{i}', False):
                        if 'player_ability_off' in skill.config['event']:
                            with FakeEvent('player_ability_off' if skill._type is ModuleType.SP else f'{skill_name}_off', userid=wcsplayer.userid) as event:
                                skill.execute(event.name, event)

                    break

                i += 1

    return CommandReturn.BLOCK


@TypedClientCommand('ability')
def client_ability_command(command):
    wcsplayer = Player(command.index)

    if wcsplayer.ready:
        active_race = wcsplayer.active_race

        for skill in active_race.skills.values():
            if 'player_ability' in skill.config['event']:
                reason = skill.is_executable()

                if reason is SkillReason.ALLOWED:
                    # Only used for ESS_INI and ESS_KEY races - SP, ESP, and ESS races should set the cooldown directly
                    # TODO: Races should handle the cooldown directly
                    if skill._type is ModuleType.ESS_INI or skill._type is ModuleType.ESS_KEY:
                        skill.reset_cooldown()

                    skill.execute('player_ability', define=True)
                elif reason is SkillReason.TEAM:
                    ability_team_message.send(command.index)
                elif reason is SkillReason.DEAD:
                    ability_dead_message.send(command.index)
                elif reason is SkillReason.DEACTIVATED:
                    ability_deactivated_message.send(command.index)
                elif reason is SkillReason.COOLDOWN:
                    ability_cooldown_message.send(command.index, cooldown=skill.cooldown_seconds, left=skill.cooldown - time())
                elif reason is SkillReason.LEVEL:
                    ability_level_message.send(command.index)
                elif isinstance(reason, IntEnum):
                    data = {'reason':reason}

                    OnIsSkillExecutableText.manager.notify(wcsplayer, skill, data)
                else:
                    raise ValueError(f'Invalid reason: {reason}')

                break
        else:
            if IS_ESC_SUPPORT_ENABLED:
                _execute_ability(wcsplayer)

    return CommandReturn.BLOCK


@TypedClientCommand('ultimate')
def client_ultimate_command(command):
    wcsplayer = Player(command.index)

    if wcsplayer.ready:
        active_race = wcsplayer.active_race

        for skill in active_race.skills.values():
            if 'player_ultimate' in skill.config['event']:
                reason = skill.is_executable()

                if reason is SkillReason.ALLOWED:
                    # Only used for ESS_INI and ESS_KEY races - SP, ESP, and ESS races should set the cooldown directly
                    # TODO: Races should handle the cooldown directly
                    if skill._type is ModuleType.ESS_INI or skill._type is ModuleType.ESS_KEY:
                        skill.reset_cooldown()

                    skill.execute('player_ultimate', define=True)
                elif reason is SkillReason.TEAM:
                    ability_team_message.send(command.index)
                elif reason is SkillReason.DEAD:
                    ability_dead_message.send(command.index)
                elif reason is SkillReason.DEACTIVATED:
                    ability_deactivated_message.send(command.index)
                elif reason is SkillReason.COOLDOWN:
                    ability_cooldown_message.send(command.index, cooldown=skill.cooldown_seconds, left=skill.cooldown - time())
                elif reason is SkillReason.LEVEL:
                    ability_level_message.send(command.index)
                elif isinstance(reason, IntEnum):
                    data = {'reason':reason}

                    OnIsSkillExecutableText.manager.notify(wcsplayer, skill, data)
                else:
                    raise ValueError(f'Invalid reason: {reason}')

                break

    return CommandReturn.BLOCK


# ============================================================================
# >> REPEATS
# ============================================================================
@Repeat
def save_data_repeat():
    for _, wcsplayer in PlayerReadyIter():
        wcsplayer.save()

    database_manager.execute('player offline', callback=_query_refresh_offline)
save_data_repeat.start(60 * 1)


@Repeat
def hinttext_repeat():
    now = time()

    for _, wcsplayer in PlayerReadyIter():
        messages = []
        language = get_client_language(wcsplayer.index)

        for i, skill in enumerate(wcsplayer.active_race.skills.values()):
            if 'player_ability' in skill.config['event'] or 'player_ultimate' in skill.config['event']:
                if skill.level > 0:
                    if skill.cooldown_seconds:
                        if skill.cooldown > now:
                            messages.append(menu_strings['hinttext_cooldown'].get_string(language, name=wcsplayer.active_race.settings.strings[skill.name], seconds=skill.cooldown - now))

                            wcsplayer.data[f'_internal_hinttext_cooldown_showing_{i}'] = True
                            wcsplayer.data[f'_internal_hinttext_cooldown_duration_{i}'] = None
                        elif wcsplayer.data.get(f'_internal_hinttext_cooldown_showing_{i}', False):
                            if wcsplayer.data[f'_internal_hinttext_cooldown_duration_{i}'] is None:
                                wcsplayer.data[f'_internal_hinttext_cooldown_duration_{i}'] = now + 3

                            if wcsplayer.data[f'_internal_hinttext_cooldown_duration_{i}'] > now:
                                messages.append(menu_strings['hinttext_cooldown ready'].get_string(language, name=wcsplayer.active_race.settings.strings[skill.name]))
                            else:
                                wcsplayer.data[f'_internal_hinttext_cooldown_showing_{i}'] = False

        if messages:
            HintText('\n'.join(messages)).send(wcsplayer.index)


if cfg_hinttext_cooldown.get_int():
    hinttext_repeat.start(0.1)
