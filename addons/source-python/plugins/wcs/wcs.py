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
#   Random
from random import choice
#   Time
from time import sleep
from time import time

# Source.Python Imports
#   Commands
from commands import CommandReturn
from commands.typed import TypedSayCommand
from commands.typed import TypedClientCommand
#   Colors
from colors import Color
#   Core
from core import OutputReturn
#   Entities
from entities.constants import RenderMode
from entities.entity import Entity
#   Events
from events import Event
#   Filters
from filters.weapons import WeaponClassIter
#   Listeners
from listeners import OnLevelInit
from listeners import OnServerOutput
from listeners.tick import Delay
from listeners.tick import Repeat
from listeners.tick import RepeatStatus
#   Mathlib
from mathlib import QAngle
from mathlib import Vector
#   Menus
from menus import Text
#   Players
from players.helpers import index_from_uniqueid
from players.helpers import index_from_userid
#   Weapons
from weapons.entity import Weapon

# WCS Imports
#   Config
from .core.config import cfg_bonus_xp
from .core.config import cfg_kill_xp
from .core.config import cfg_knife_xp
from .core.config import cfg_headshot_xp
from .core.config import cfg_welcome_text
from .core.config import cfg_welcome_gui_text
from .core.config import cfg_level_up_effect
from .core.config import cfg_spawn_text
from .core.config import cfg_disable_text_on_level
from .core.config import cfg_top_announcement_enable
from .core.config import cfg_top_public_announcement
from .core.config import cfg_top_min_rank_announcement
from .core.config import cfg_top_stolen_notify
from .core.config import cfg_bot_random_race
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
from .core.config import cfg_github_mod_update
from .core.config import cfg_github_refresh_rate
#   Constants
from .core.constants import IS_ESC_SUPPORT_ENABLED
from .core.constants import ModuleType
from .core.constants import RaceReason
from .core.constants import SkillReason
from .core.constants.info import info
#   Database
from .core.database.manager import database_manager
from .core.database.thread import _repeat
from .core.database.thread import _thread
#   Helpers
from .core.helpers.events import FakeEvent
from .core.helpers.github import github_manager
from .core.helpers.overwrites import SayText2
#   Listeners
from .core.listeners import OnDownloadComplete
from .core.listeners import OnIsSkillExecutableText
from .core.listeners import OnPlayerAbilityOff
from .core.listeners import OnPlayerAbilityOn
from .core.listeners import OnPlayerDelete
from .core.listeners import OnPlayerLevelUp
from .core.listeners import OnPlayerRankUpdate
from .core.listeners import OnPlayerReady
from .core.listeners import OnPluginUnload
from .core.listeners import OnTakeDamage
#   Menus
from .core.menus import shopmenu_menu
from .core.menus import shopinfo_menu
from .core.menus import showskills_menu
from .core.menus import resetskills_menu
from .core.menus import spendskills_menu
from .core.menus import changerace_menu
from .core.menus import raceinfo_menu
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

_delays = defaultdict(set)
_melee_weapons = [weapon.basename for weapon in WeaponClassIter('melee')]
_new_version = None

_effect_angle = QAngle(0, 0, 0)
_effect_color = Color(252, 232, 131)


# ============================================================================
# >> CLASSES
# ============================================================================
class QuietTypedClientCommand(TypedClientCommand):
    @staticmethod
    def send_message(command_info, message):
        pass


# ============================================================================
# >> FUNCTIONS
# ============================================================================
def load():
    github_manager.refresh()

    if cfg_github_mod_update.get_int():
        github_manager.download_update()

    database_manager.connect()

    if IS_ESC_SUPPORT_ENABLED:
        race_manager.update(parse_ini_races())
        race_manager.update(parse_key_races())
        item_manager.update(parse_ini_items())
        item_manager.update(parse_key_items())

    race_manager.load_all()
    item_manager.load_all()

    for _, player in PlayerIter():
        Player(player.uniqueid)

    for settings in race_manager.values():
        settings.execute('preloadcmd')

    for settings in item_manager.values():
        settings.execute('preloadcmd')

    database_manager.execute('player offline', callback=_query_refresh_offline)
    database_manager.execute('rank update', callback=_query_refresh_ranks)


def unload():
    database_manager._unloading = True

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

    for uniqueid, name in result.fetchall():
        playerinfo_menu.append(PagedOption(name, uniqueid))
        wcsadmin_players_menu.append(PagedOption(name, uniqueid))


def _query_refresh_ranks(result):
    for uniqueid, name, current_race, total_level in result.fetchall():
        if current_race not in race_manager:
            current_race = race_manager.default_race

        rank_manager._data[uniqueid] = {'name':name, 'current_race':current_race, 'total_level':total_level}

        option = PagedOption(deepcopy(menu_strings['wcstop_menu line']), uniqueid, show_index=False)
        option.text.tokens['name'] = name

        wcstop_menu.append(option)

        rank_manager.append(uniqueid)


def _give_xp_if_set(userid, config, bot_config, message):
    wcsplayer = Player.from_userid(userid)

    if not wcsplayer.ready:
        return

    if wcsplayer._is_bot:
        value = bot_config.get_int()

        if value == -1:
            value = config.get_int()
    else:
        value = config.get_int()

    if value:
        if wcsplayer._is_bot:
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
        if wcsplayer._is_bot:
            if bot_value:
                wcsplayer.xp += bot_value
        else:
            if value:
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


def _fire_post_player_spawn(wcsplayer, delay):
    with FakeEvent('post_player_spawn', userid=wcsplayer.userid) as event:
        wcsplayer.notify(event)

    _delays[wcsplayer].remove(delay)


# ============================================================================
# >> EVENTS
# ============================================================================
@Event('round_start')
def round_start(event):
    for _, wcsplayer in PlayerReadyIter(not_filters=['un', 'spec']):
        wcsplayer.execute('roundstartcmd', event, define=True)

    if _new_version is not None:
        for _, wcsplayer in PlayerReadyIter():
            if wcsplayer.privileges.get('wcsadmin'):
                github_mod_update_message.send(wcsplayer.index, old=info.version, new=_new_version)


@Event('round_end')
def round_end(event):
    for _, wcsplayer in PlayerReadyIter(not_filters=['un', 'spec']):
        wcsplayer.execute('roundendcmd', event, define=True)

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
            if not wcsplayer._is_bot:
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

                    if maximum:
                        if active_race.level >= maximum:
                            return

                    value = kill_xp = cfg_kill_xp.get_int()

                    if event['headshot']:
                        headshot_xp = cfg_headshot_xp.get_int()

                        if headshot_xp:
                            value += headshot_xp

                            if not wcsattacker._is_bot:
                                delay = Delay(1, _send_message_and_remove, (gain_xp_headshot_message, wcsattacker), {'value':headshot_xp})
                                delay.args += (delay, )
                                _delays[wcsattacker].add(delay)

                    if wcsvictim.ready:
                        difference = wcsvictim.level - active_race.level

                        if difference > 0:
                            bonus_xp = cfg_bonus_xp.get_int()

                            if bonus_xp:
                                gained = difference * bonus_xp
                                value += gained

                                if not wcsattacker._is_bot:
                                    delay = Delay(1, _send_message_and_remove, (gain_xp_killed_higher_level_message, wcsattacker), {'value':gained, 'difference':difference})
                                    delay.args += (delay, )
                                    _delays[wcsattacker].add(delay)

                    if event['weapon'] in _melee_weapons:
                        knife_xp = cfg_knife_xp.get_int()

                        if knife_xp:
                            value += knife_xp

                            if not wcsattacker._is_bot:
                                delay = Delay(1, _send_message_and_remove, (gain_xp_knife_message, wcsattacker), {'value':knife_xp})
                                delay.args += (delay, )
                                _delays[wcsattacker].add(delay)

                    if value:
                        if not wcsattacker._is_bot:
                            for delay in _delays[wcsattacker]:
                                if delay.callback is _xp_gained:
                                    delay.kwargs['_allow'] = False

                            # I want this to be the last one
                            delay = Delay(1.01, _xp_gained, (wcsattacker, active_race, active_race.level, kill_xp))
                            delay.args += (delay, )
                            _delays[wcsattacker].add(delay)

                        active_race.xp += value

    if wcsvictim._is_bot:
        if cfg_bot_random_race.get_int():
            if wcsvictim.ready:
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

        if value is not None and value > 1:
            player = wcsplayer.player

            velocity = Vector(*player.get_property_vector('m_vecVelocity'))

            velocity[0] *= value
            velocity[1] *= value

            player.set_property_vector('m_vecBaseVelocity', velocity)


# ============================================================================
# >> LISTENERS
# ============================================================================
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


@OnDownloadComplete
def on_download_complete(version):
    if version is not None:
        global _new_version

        _new_version = version

        for _, wcsplayer in PlayerReadyIter():
            if wcsplayer.privileges.get('wcsadmin'):
                github_mod_update_message.send(wcsplayer.index, old=info.version, new=version)


@OnLevelInit
def on_level_init(map_name):
    github_manager.refresh()

    if cfg_github_mod_update.get_int():
        github_manager.download_update()


@OnPlayerDelete
def on_player_delete(wcsplayer):
    if wcsplayer.ready:
        with FakeEvent('disconnectcmd', userid=wcsplayer.userid) as event:
            wcsplayer.execute(event.name, event)

    for delay in _delays.pop(wcsplayer, []):
        if delay.running:
            delay.cancel()


@OnPlayerLevelUp
def on_player_level_up(wcsplayer, race, old_level):
    if wcsplayer.current_race == race.name:
        if not wcsplayer._is_bot:
            for skill in wcsplayer.skills.values():
                if skill.level < skill.config['maximum']:
                    delay = Delay(2, _send_message_and_remove, (spendskills_menu, wcsplayer))
                    delay.args += (delay, )
                    _delays[wcsplayer].add(delay)
                    break

        if cfg_level_up_effect.get_int():
            player = wcsplayer.player

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
            entity.render_color = _effect_color
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


@OnPlayerRankUpdate
def on_player_rank_update(wcsplayer, old, new):
    if cfg_top_announcement_enable.get_int():
        min_rank = cfg_top_min_rank_announcement.get_int()

        if not min_rank or new <= min_rank:
            if cfg_top_public_announcement.get_int():
                top_public_announcement_message.send(name=wcsplayer.name, min_rank=min_rank if min_rank else '', old=old + 1, new=new + 1)
            else:
                if not wcsplayer._is_bot:
                    top_private_announcement_message.send(wcsplayer.index, min_rank=min_rank if min_rank else '', old=old + 1, new=new + 1)

        if new < old:
            if cfg_top_stolen_notify.get_int():
                for i, uniqueid in enumerate(rank_manager[new + 1:old + 1]):
                    try:
                        index = index_from_uniqueid(uniqueid)
                    except ValueError:
                        pass
                    else:
                        top_stolen_notify_message.send(index, name=wcsplayer.name, old=new + i, new=new + i + 1)


@OnPlayerReady
def on_player_ready(wcsplayer):
    if wcsplayer.player.team_index >= 2:
        if not wcsplayer._is_bot:
            if cfg_spawn_text.get_int():
                if wcsplayer.total_level <= cfg_disable_text_on_level.get_int():
                    help_text_message.send(wcsplayer.index)

            active_race = wcsplayer.active_race

            xp_required_message.send(wcsplayer.index, name=active_race.settings.strings['name'], level=active_race.level, xp=active_race.xp, required=active_race.required_xp)

        wcsplayer.execute('readycmd', define=True)

    if not wcsplayer._is_bot:
        if wcsplayer.total_level <= cfg_disable_text_on_level.get_int():
            if cfg_welcome_text.get_int():
                delay = Delay(10, _send_message_and_remove, (welcome_text_message, wcsplayer))
                delay.args += (delay, )
                _delays[wcsplayer].add(delay)

            if cfg_welcome_gui_text.get_int():
                delay = Delay(5, _send_message_and_remove, (welcome_menu, wcsplayer))
                delay.args += (delay, )
                _delays[wcsplayer].add(delay)


@OnTakeDamage
def on_take_damage(wcsvictim, wcsattacker, info):
    if wcsattacker is not None:
        if wcsvictim is not wcsattacker:
            if wcsvictim.ready:
                if info.attacker == info.inflictor:
                    weapon = wcsattacker.player.active_weapon
                else:
                    weapon = Weapon(info.inflictor)

                if weapon.class_name not in ('point_hurt', 'worldspawn') and not weapon.class_name.startswith('wcs_'):
                    # TODO: Make this the same as player_hurt (info.damage is not the real, calculated damage that is dealt, so don't know when a player is getting killed)
                    # TODO: Keep using weapon.class_name (weapon_<name>) or use weapon_manager[weapon.class_name].basename (<name>)?
                    if not wcsvictim.player.team_index == wcsattacker.player.team_index:
                        with FakeEvent('pre_player_victim', userid=wcsvictim.userid, attacker=wcsattacker.userid, weapon=weapon.class_name, info=info) as event:
                            wcsvictim.notify(event)

                        if wcsattacker.ready:
                            with FakeEvent('pre_player_attacker', userid=wcsvictim.userid, attacker=wcsattacker.userid, weapon=weapon.class_name, info=info) as event:
                                wcsattacker.notify(event)

                    with FakeEvent('pre_player_hurt', userid=wcsvictim.userid, attacker=wcsattacker.userid, weapon=weapon.class_name, info=info) as event:
                        wcsvictim.notify(event)

                    if wcsattacker.ready:
                        with FakeEvent('pre_player_hurt', userid=wcsvictim.userid, attacker=wcsattacker.userid, weapon=weapon.class_name, info=info) as event:
                            wcsattacker.notify(event)


# ============================================================================
# >> COMMANDS
# ============================================================================
@QuietTypedClientCommand('_wcsadmin_input_xp')
def _wcsadmin_input_xp_command(command, value:int):
    wcsplayer = Player.from_index(command.index)

    if not wcsplayer.privileges.get('wcsadmin_playersmanagement'):
        return CommandReturn.CONTINUE

    uniqueid = wcsplayer.data.get('_internal_wcsadmin_player')

    if uniqueid is None:
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
        wcstarget = Player(uniqueid)

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

    return CommandReturn.BLOCK


@QuietTypedClientCommand('_wcsadmin_input_level')
def _wcsadmin_input_level_command(command, value:int):
    wcsplayer = Player.from_index(command.index)

    if not wcsplayer.privileges.get('wcsadmin_playersmanagement'):
        return CommandReturn.CONTINUE

    uniqueid = wcsplayer.data.get('_internal_wcsadmin_player')

    if uniqueid is None:
        for _, wcstarget in PlayerReadyIter():
            wcstarget.level += value

            if wcstarget is wcsplayer:
                admin_gain_levels_self_message.send(wcsplayer.index, value=value)
            else:
                admin_gain_levels_receiver_message.send(wcstarget.index, value=value, name=wcsplayer.name)

        admin_gain_levels_all_message.send(wcsplayer.index, value=value)
    else:
        wcstarget = Player(uniqueid)

        if wcstarget.ready:
            wcstarget.level += value

            if wcstarget is wcsplayer:
                admin_gain_levels_self_message.send(wcsplayer.index, value=value)
            else:
                admin_gain_levels_sender_message.send(wcsplayer.index, name=wcstarget.name, value=value)
                admin_gain_levels_receiver_message.send(wcstarget.index, value=value, name=wcsplayer.name)

    return CommandReturn.BLOCK


@TypedSayCommand('wcs')
def say_command_wcs(command):
    main_menu.send(command.index)

    return CommandReturn.BLOCK


@TypedSayCommand('shopmenu')
def say_command_shopmenu(command):
    wcsplayer = Player.from_index(command.index)

    if wcsplayer.ready:
        shopmenu_menu.send(command.index)
    else:
        not_ready_message.send(command.index)

    return CommandReturn.BLOCK


@TypedSayCommand('shopinfo')
def say_command_shopinfo(command):
    shopinfo_menu.send(command.index)

    return CommandReturn.BLOCK


@TypedSayCommand('showskills')
def say_command_showskills(command):
    wcsplayer = Player.from_index(command.index)

    if wcsplayer.ready:
        showskills_menu.send(command.index)
    else:
        not_ready_message.send(command.index)

    return CommandReturn.BLOCK


@TypedSayCommand('resetskills')
def say_command_resetskills(command):
    wcsplayer = Player.from_index(command.index)

    if wcsplayer.ready:
        resetskills_menu.send(command.index)
    else:
        not_ready_message.send(command.index)

    return CommandReturn.BLOCK


@TypedSayCommand('spendskills')
def say_command_spendskills(command):
    wcsplayer = Player.from_index(command.index)

    if wcsplayer.ready:
        active_race = wcsplayer.active_race

        if active_race.unused > 0:
            if any([skill.level < skill.config['maximum'] for skill in active_race.skills.values()]):
                spendskills_menu.send(command.index)
            else:
                maximum_level_message.send(command.index)
        else:
            no_unused_message.send(command.index)
    else:
        not_ready_message.send(command.index)

    return CommandReturn.BLOCK


@TypedSayCommand('changerace')
def say_command_changerace(command):
    wcsplayer = Player.from_index(command.index)

    if wcsplayer.ready:
        changerace_menu.send(command.index)
    else:
        not_ready_message.send(command.index)

    return CommandReturn.BLOCK


@TypedSayCommand('raceinfo')
def say_command_raceinfo(command):
    raceinfo_menu.send(command.index)

    return CommandReturn.BLOCK


@TypedSayCommand('playerinfo')
def say_command_playerinfo(command):
    playerinfo_menu.send(command.index)

    return CommandReturn.BLOCK


@TypedSayCommand('wcstop')
def say_command_wcstop(command):
    wcstop_menu.send(command.index)

    return CommandReturn.BLOCK


@TypedSayCommand('wcshelp')
def say_command_wcshelp(command):
    wcshelp_menu.send(command.index)

    return CommandReturn.BLOCK


@TypedSayCommand('wcsadmin')
def say_command_wcsadmin(command):
    wcsplayer = Player.from_index(command.index)

    if wcsplayer.privileges.get('wcsadmin', False):
        wcsadmin_menu.send(command.index)
    else:
        no_access_message.send(command.index)

    return CommandReturn.BLOCK


@TypedSayCommand('showxp')
def say_command_showxp(command):
    wcsplayer = Player.from_index(command.index)
    active_race = wcsplayer.active_race

    xp_required_message.send(wcsplayer.index, name=active_race.settings.strings['name'], level=active_race.level, xp=active_race.xp, required=active_race.required_xp)

    return CommandReturn.BLOCK


@TypedClientCommand('+ability')
def client_ability_plus_command(command, ability:int=1, *args:str):
    wcsplayer = Player.from_index(command.index)

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
                        OnPlayerAbilityOn.manager.notify(wcsplayer, skill, args)

                        with FakeEvent('player_ability_on' if skill._type is ModuleType.SP else f'{skill_name}_on', userid=wcsplayer.userid, args=args) as event:
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
    wcsplayer = Player.from_index(command.index)
    if wcsplayer.ready:
        # TODO: Monkeypatch until it's been fixed in SP (don't create a race with 32 abilities, please)
        if ability == 32:
            ability = 1

        active_race = wcsplayer.active_race

        i = 1

        for skill_name in active_race.settings.config['skills']:
            skill = active_race.skills[skill_name]

            if 'player_ability_off' in skill.config['event']:
                if ability == i:
                    OnPlayerAbilityOff.manager.notify(wcsplayer, skill, args)

                    with FakeEvent('player_ability_off' if skill._type is ModuleType.SP else f'{skill_name}_off', userid=wcsplayer.userid, args=args) as event:
                        skill.execute(event.name, event)

                    break

                i += 1

    return CommandReturn.BLOCK


@TypedClientCommand('ability')
def client_ability_command(command):
    wcsplayer = Player.from_index(command.index)

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

    return CommandReturn.BLOCK


@TypedClientCommand('ultimate')
def client_ultimate_command(command):
    wcsplayer = Player.from_index(command.index)

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
def github_refresh_repeat():
    github_manager.refresh()


if cfg_github_refresh_rate.get_int():
    github_refresh_repeat.start(cfg_github_refresh_rate.get_int() * 60)
