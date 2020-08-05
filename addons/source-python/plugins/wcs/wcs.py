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
from core import SOURCE_ENGINE_BRANCH
from core import OutputReturn
#   Engines
from engines.server import global_vars
#   Entities
from entities.constants import MoveType
from entities.constants import RenderMode
from entities.entity import Entity
#   Events
from events import Event
#   Filters
from filters.weapons import WeaponClassIter
#   Listeners
from listeners import OnLevelInit
from listeners import OnServerOutput
from listeners import OnTick
from listeners.tick import Delay
from listeners.tick import Repeat
from listeners.tick import RepeatStatus
#   Mathlib
from mathlib import QAngle
from mathlib import Vector
#   Menus
from menus import Text
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
from .core.config import cfg_bonus_xp_level_cap
from .core.config import cfg_kill_xp
from .core.config import cfg_knife_xp
from .core.config import cfg_headshot_xp
from .core.config import cfg_welcome_text
from .core.config import cfg_welcome_gui_text
from .core.config import cfg_level_up_effect
from .core.config import cfg_rank_gain_effect
from .core.config import cfg_spawn_text
from .core.config import cfg_hinttext_cooldown
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
from .core.menus import wcstop_menu
from .core.menus import wcshelp_menu
from .core.menus import welcome_menu
from .core.menus import wcsadmin_menu
from .core.menus import wcsadmin_players_menu
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
changerace_message = SayText2(chat_strings['changerace'])
changerace_warning_message = SayText2(chat_strings['changerace warning'])
no_race_found_message = SayText2(chat_strings['no race found'])
gain_xp_killed_message = SayText2(chat_strings['gain xp killed'])
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
github_mod_update_message = SayText2(chat_strings['github mod update'])

hinttext_cooldown_message = HintText(menu_strings['hinttext_cooldown'])
hinttext_cooldown_ready_message = HintText(menu_strings['hinttext_cooldown ready'])

_delays = defaultdict(set)
_melee_weapons = [weapon.basename for weapon in WeaponClassIter('melee')]
_new_version = None

_effect_angle = QAngle(0, 0, 0)
_level_effect_color = Color(252, 232, 131)
_rank_effect_color = Color(43, 145, 255)


# ============================================================================
# >> FUNCTIONS
# ============================================================================
def load():
    github_manager.refresh_modules()

    database_manager.connect()

    if IS_ESC_SUPPORT_ENABLED:
        race_manager.update(parse_ini_races())
        race_manager.update(parse_key_races())
        item_manager.update(parse_ini_items())
        item_manager.update(parse_key_items())

    race_manager.load_all()
    item_manager.load_all()

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


def _xp_gained(wcsplayer, active_race, old_level, value, delay, _allow=True):
    gain_xp_killed_message.send(wcsplayer.index, value=value)

    if active_race.level > old_level and _allow:
        gain_level_message.send(wcsplayer.index, level=active_race.level, xp=active_race.xp, required=active_race.required_xp)

    _delays[wcsplayer].remove(delay)


def _send_message_and_remove(message, wcsplayer, delay, **kwargs):
    message.send(wcsplayer.index, **kwargs)

    _delays[wcsplayer].remove(delay)


def _query_refresh_offline(result):
    stop = False

    for i, option in enumerate(playerinfo_menu, 1):
        if isinstance(option, Text):
            if stop:
                del playerinfo_menu[i:]
                break

            stop = True

    stop = False

    for i, option in enumerate(wcsadmin_players_menu, 2):
        if isinstance(option, Text):
            if stop:
                del wcsadmin_players_menu[i:]
                break

            stop = True

    for accountid, name in result.fetchall():
        playerinfo_menu.append(PagedOption(name, accountid))
        wcsadmin_players_menu.append(PagedOption(name, accountid))


def _query_refresh_ranks(result):
    for accountid, name, current_race, total_level in result.fetchall():
        if current_race not in race_manager:
            current_race = race_manager.default_race

        if accountid is None:
            accountid = name

        rank_manager._data[accountid] = {'name':name, 'current_race':current_race, 'total_level':total_level}

        option = PagedOption(deepcopy(menu_strings['wcstop_menu line']), accountid, show_index=False)
        option.text.tokens['name'] = name

        wcstop_menu.append(option)

        rank_manager.append(accountid)


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
        maximum = active_race.settings.config['maximum']

        if not maximum or active_race.level < maximum:
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


# ============================================================================
# >> EVENTS
# ============================================================================
@Event('round_start')
def round_start(event):
    for _, wcsplayer in PlayerReadyIter(not_filters=['un', 'spec']):
        wcsplayer.execute('roundstartcmd', event, define=True)


@Event('round_end')
def round_end(event):
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

        if team >= 2:
            reason = RaceReason.ALLOWED

            restrictteam = wcsplayer.active_race.settings.config.get('restrictteam')

            if restrictteam:
                if not restrictteam == team:
                    reason = RaceReason.TEAM

            if reason is RaceReason.ALLOWED:
                teamlimit = wcsplayer.active_race.settings.config.get('teamlimit')

                if teamlimit:
                    limit = team_data[team].get(key, [])

                    if teamlimit <= len(limit) and userid not in limit:
                        reason = RaceReason.TEAM_LIMIT

            if reason is RaceReason.ALLOWED:
                if key not in team_data[team]:
                    team_data[team][key] = []

                if userid not in team_data[team][key]:
                    team_data[team][key].append(userid)
            else:
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
        elif oldteam >= 2:
            team_data[oldteam][key].remove(userid)

            if not team_data[oldteam][key]:
                del team_data[oldteam][key]


@Event('player_spawn')
def player_spawn(event):
    userid = event['userid']
    wcsplayer = Player.from_userid(userid)

    if wcsplayer.ready:
        if wcsplayer.player.team_index >= 2:
            if not wcsplayer.fake_client:
                if cfg_resetskills_next_round.get_int():
                    if wcsplayer.data.pop('_internal_reset_skills', False):
                        unused = 0
                        maximum = 0

                        for skill in wcsplayer.skills.values():
                            unused += skill.level
                            skill.level = 0

                            maximum += skill.config['maximum']

                        unused = wcsplayer.unused = min(wcsplayer.unused + unused, maximum)

                        skills_reset_message.send(wcsplayer.index, unused=unused)

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
    attacker = event['attacker']

    if attacker:
        if event['weapon'] not in ('point_hurt', 'worldspawn') and not event['weapon'].startswith('wcs_'):
            userid = event['userid']

            if not userid == attacker:
                wcsvictim = Player.from_userid(userid)
                wcsattacker = Player.from_userid(attacker)

                if wcsvictim.ready:
                    health = event['health']

                    if not wcsvictim.player.team_index == wcsattacker.player.team_index:
                        wcsvictim.notify(event, 'player_victim')

                        if health > 0:
                            if wcsattacker.ready:
                                wcsattacker.notify(event, 'player_attacker')

                    wcsvictim.notify(event, 'player_hurt')

                    if health > 0:
                        if wcsattacker.ready:
                            wcsattacker.notify(event, 'player_hurt')


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

                if not wcsvictim.player.team_index == wcsattacker.player.team_index:
                    active_race = wcsattacker.active_race
                    maximum = active_race.settings.config['maximum']

                    if not maximum or active_race.level < maximum:
                        value = kill_xp = cfg_kill_xp.get_int()

                        if event['headshot']:
                            headshot_xp = cfg_headshot_xp.get_int()

                            if headshot_xp:
                                value += headshot_xp

                                if not wcsattacker.fake_client:
                                    delay = Delay(1, _send_message_and_remove, (gain_xp_headshot_message, wcsattacker), {'value':headshot_xp})
                                    delay.args += (delay, )
                                    _delays[wcsattacker].add(delay)

                        if wcsvictim.ready:
                            difference = wcsvictim.level - active_race.level

                            if difference > 0:
                                bonus_xp = cfg_bonus_xp.get_int()

                                if bonus_xp:
                                    cap = cfg_bonus_xp_level_cap.get_int()

                                    gained = (min(cap, difference) if cap > 0 else difference) * bonus_xp
                                    value += gained

                                    if not wcsattacker.fake_client:
                                        delay = Delay(1, _send_message_and_remove, (gain_xp_killed_higher_level_message, wcsattacker), {'value':gained, 'difference':difference})
                                        delay.args += (delay, )
                                        _delays[wcsattacker].add(delay)

                        if event['weapon'] in _melee_weapons:
                            knife_xp = cfg_knife_xp.get_int()

                            if knife_xp:
                                value += knife_xp

                                if not wcsattacker.fake_client:
                                    delay = Delay(1, _send_message_and_remove, (gain_xp_knife_message, wcsattacker), {'value':knife_xp})
                                    delay.args += (delay, )
                                    _delays[wcsattacker].add(delay)

                        if value:
                            if not wcsattacker.fake_client:
                                for delay in _delays[wcsattacker]:
                                    if delay.callback is _xp_gained:
                                        delay.kwargs['_allow'] = False

                                # I want this to be the last one
                                delay = Delay(1.01, _xp_gained, (wcsattacker, active_race, active_race.level, kill_xp))
                                delay.args += (delay, )
                                _delays[wcsattacker].add(delay)

                            active_race.xp += value

    if wcsvictim.ready:
        for item in wcsvictim.items.values():
            if item.settings.config['duration'] == 1:
                item.count = 0

        if wcsvictim.fake_client:
            if cfg_bot_random_race.get_int():
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


# Is ESC supported?
if IS_ESC_SUPPORT_ENABLED:
    #  Used to clean up loading/unloading of wcs
    @OnServerOutput
    def on_server_output(severity, msg):
        if msg.startswith(('[EventScripts] Loaded wcs/modules/races/', 'Unloading wcs/modules/races/')) or (msg.startswith('wcs/modules/races/') and msg.endswith(' has been unloaded\n')):
            return OutputReturn.BLOCK
        if msg.startswith(('[EventScripts] Loaded wcs/modules/items/', 'Unloading wcs/modules/items/')) or (msg.startswith('wcs/modules/items/') and msg.endswith(' has been unloaded\n')):
            return OutputReturn.BLOCK

        return OutputReturn.CONTINUE


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


@OnPlayerDelete
def on_player_delete(wcsplayer):
    if wcsplayer.ready:
        with FakeEvent('disconnectcmd', userid=wcsplayer.userid) as event:
            wcsplayer.execute(event.name, event)

    for delay in _delays.pop(wcsplayer, []):
        if delay.running:
            delay.cancel()


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
                entity.smoke_material = 'effects/combinemuzzle2.vmt'
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
                    entity.smoke_material = 'effects/yellowflare.vmt'
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
    if wcsplayer.player.team_index >= 2:
        if not wcsplayer.fake_client:
            if cfg_spawn_text.get_int():
                if wcsplayer.total_level <= cfg_disable_text_on_level.get_int():
                    help_text_message.send(wcsplayer.index)

            active_race = wcsplayer.active_race

            xp_required_message.send(wcsplayer.index, name=active_race.settings.strings['name'], level=active_race.level, xp=active_race.xp, required=active_race.required_xp)

        wcsplayer.execute('readycmd', define=True)

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


@OnSettingsLoaded
def on_settings_loaded(settings):
    database_manager.execute('player offline', callback=_query_refresh_offline)
    database_manager.execute('rank update', callback=_query_refresh_ranks)


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

                    if not wcsvictim.player.team_index == wcsattacker.player.team_index:
                        with FakeEvent('pre_player_victim', userid=wcsvictim.userid, attacker=wcsattacker.userid, weapon=weapon_name, info=info) as event:
                            wcsvictim.notify(event)

                        if health > 0:
                            if wcsattacker.ready:
                                with FakeEvent('pre_player_attacker', userid=wcsvictim.userid, attacker=wcsattacker.userid, weapon=weapon_name, info=info) as event:
                                    wcsattacker.notify(event)

                    with FakeEvent('pre_player_hurt', userid=wcsvictim.userid, attacker=wcsattacker.userid, weapon=weapon_name, info=info) as event:
                        wcsvictim.notify(event)

                    if health > 0:
                        if wcsattacker.ready:
                            with FakeEvent('pre_player_hurt', userid=wcsvictim.userid, attacker=wcsattacker.userid, weapon=weapon_name, info=info) as event:
                                wcsattacker.notify(event)


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

        rank_message.send(name=wcsplayer.name, race=active_race.settings.strings['name'], level=active_race.level, xp=active_race.xp, required=active_race.required_xp, rank=wcsplayer.rank, total=len(rank_manager))
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
        for skill in wcsplayer.active_race.skills.values():
            if 'player_ultimate' in skill.config['event']:
                if skill.cooldown_seconds:
                    if skill.cooldown > now:
                        hinttext_cooldown_message.send(wcsplayer.index, name=wcsplayer.active_race.settings.strings[skill.name], seconds=skill.cooldown - now)

                        wcsplayer.data['_internal_hinttext_cooldown_shown'] = False
                    elif not wcsplayer.data.get('_internal_hinttext_cooldown_shown', False):
                        wcsplayer.data['_internal_hinttext_cooldown_shown'] = True

                        hinttext_cooldown_ready_message.send(wcsplayer.index, name=wcsplayer.active_race.settings.strings[skill.name])

                break


if cfg_hinttext_cooldown.get_int():
    hinttext_repeat.start(0.1)
