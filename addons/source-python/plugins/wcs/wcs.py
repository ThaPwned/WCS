# ../wcs/wcs.py

# ============================================================================
# >> IMPORTS
# ============================================================================
# Python Imports
#   Collections
from collections import defaultdict
#   Copy
from copy import deepcopy
#   Time
from time import sleep

# Source.Python Imports
#   Commands
from commands import CommandReturn
from commands.typed import TypedSayCommand
from commands.typed import TypedClientCommand
#   Core
from core import OutputReturn
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
#   Menus
from menus import Text
#   Players
from players.helpers import index_from_uniqueid

# WCS Imports
#   Config
from .core.config import cfg_bonus_xp
from .core.config import cfg_kill_xp
from .core.config import cfg_knife_xp
from .core.config import cfg_headshot_xp
from .core.config import cfg_welcome_text
from .core.config import cfg_welcome_gui_text
from .core.config import cfg_spawn_text
from .core.config import cfg_disable_text_on_level
from .core.config import cfg_top_announcement_enable
from .core.config import cfg_top_public_announcement
from .core.config import cfg_top_min_rank_announcement
from .core.config import cfg_top_stolen_notify
#   Constants
from .core.constants import IS_ESC_SUPPORT_ENABLED
from .core.constants import IS_GITHUB_ENABLED
#   Database
from .core.database.manager import database_manager
from .core.database.thread import _repeat
from .core.database.thread import _thread
#   Helpers
from .core.helpers.events import FakeEvent
from .core.helpers.overwrites import SayText2
#   Listeners
from .core.listeners import OnPlayerAbilityOff
from .core.listeners import OnPlayerAbilityOn
from .core.listeners import OnPlayerDelete
from .core.listeners import OnPlayerLevelUp
from .core.listeners import OnPlayerRankUpdate
from .core.listeners import OnPlayerReady
from .core.listeners import OnPluginUnload
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
from .core.menus.base import PagedOption
from .core.menus.build import _get_current_options  # Just to load it
from .core.menus.close import raceinfo_menu_close  # Just to load it
from .core.menus.menus import main_menu  # Just to load it
from .core.menus.select import main_menu_select  # Just to load it
#   Modules
from .core.modules.items.manager import item_manager
from .core.modules.races.manager import race_manager
#   Players
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
    from .core.helpers.esc.commands import _team_data  # Just to load it

# Is Github available?
if IS_GITHUB_ENABLED:
    #   Helpers
    from .core.helpers.github import github_manager


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
gain_level_message = SayText2(chat_strings['gain level'])
maximum_level_message = SayText2(chat_strings['maximum level'])
no_unused_message = SayText2(chat_strings['no unused'])
no_access_message = SayText2(chat_strings['no access'])
top_public_announcement_message = SayText2(chat_strings['top public announcement'])
top_private_announcement_message = SayText2(chat_strings['top private announcement'])
top_stolen_notify_message = SayText2(chat_strings['top stolen notify'])

_delays = defaultdict(set)
_melee_weapons = [weapon.basename for weapon in WeaponClassIter('melee')]


# ============================================================================
# >> FUNCTIONS
# ============================================================================
def load():
    # Is Github available?
    if IS_GITHUB_ENABLED:
        github_manager.refresh()

    database_manager.connect()

    race_manager.load_all()
    item_manager.load_all()

    for _, player in PlayerIter():
        Player(player.uniqueid)

    for settings in race_manager.values():
        settings.execute('preloadcmd')

    for settings in item_manager.values():
        settings.execute('preloadcmd')

    database_manager.execute('player offline', callback=_query_refresh_playerinfo)
    database_manager.execute('rank update', callback=_query_refresh_ranks)


def unload():
    database_manager._unloading = True

    for wcsplayer in Player._players.values():
        OnPlayerDelete.manager.notify(wcsplayer)

    for _, wcsplayer in PlayerReadyIter():
        wcsplayer.save()

    OnPluginUnload.manager.notify()

    # Is Github available?
    if IS_GITHUB_ENABLED:
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


def _query_refresh_playerinfo(result):
    stop = False

    for i, option in enumerate(playerinfo_menu, 1):
        if isinstance(option, Text):
            if stop:
                del playerinfo_menu[i:]
                break

            stop = True

    for uniqueid, name in result.fetchall():
        playerinfo_menu.append(PagedOption(name, uniqueid))


def _query_refresh_ranks(result):
    for uniqueid, name, current_race, total_level in result.fetchall():
        if current_race not in race_manager:
            current_race = race_manager.default_race

        rank_manager._data[uniqueid] = {'name':name, 'current_race':current_race, 'total_level':total_level}

        option = PagedOption(deepcopy(menu_strings['wcstop_menu line']), uniqueid, show_index=False)
        option.text.tokens['name'] = name

        wcstop_menu.append(option)

        rank_manager.append(uniqueid)


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


@Event('player_say')
def player_say(event):
    userid = event['userid']
    wcsplayer = Player.from_userid(userid)

    if wcsplayer.ready:
        wcsplayer.notify(event)


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


# Is Github available?
if IS_GITHUB_ENABLED:
    @OnLevelInit
    def on_level_init(map_name):
        github_manager.refresh()


@OnPlayerDelete
def on_player_delete(wcsplayer):
    for delay in _delays.pop(wcsplayer, []):
        if delay.running:
            delay.cancel()


@OnPlayerLevelUp
def on_player_level_up(wcsplayer, race, old_level):
    if not wcsplayer._is_bot:
        for skill in wcsplayer.skills.values():
            if skill.level < skill.config['maximum']:
                delay = Delay(2, _send_message_and_remove, (spendskills_menu, wcsplayer))
                delay.args += (delay, )
                _delays[wcsplayer].add(delay)
                break


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

        with FakeEvent('spawncmd', userid=wcsplayer.userid) as event:
            wcsplayer.execute(event.name, event)

        with FakeEvent('player_spawn', userid=wcsplayer.userid) as event:
            wcsplayer.notify(event)

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


# ============================================================================
# >> COMMANDS
# ============================================================================
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
    active_race = wcsplayer.active_race

    i = 1

    for skill_name in active_race.settings.config['skills']:
        skill = active_race.skills[skill_name]

        if skill.config['event'] == 'player_ability':
            if ability == i:
                OnPlayerAbilityOn.manager.notify(wcsplayer, skill, args)

                with FakeEvent(f'{skill_name}_on', userid=wcsplayer.userid, args=args) as event:
                    skill.execute(event.name, event)

                break

            i += 1

    return CommandReturn.BLOCK


@TypedClientCommand('-ability')
def client_ability_minus_command(command, ability:int=1, *args:str):
    wcsplayer = Player.from_index(command.index)
    active_race = wcsplayer.active_race

    i = 1

    for skill_name in active_race.settings.config['skills']:
        skill = active_race.skills[skill_name]

        if skill.config['event'] == 'player_ability':
            if ability == i:
                OnPlayerAbilityOff.manager.notify(wcsplayer, skill, args)

                with FakeEvent(f'{skill_name}_off', userid=wcsplayer.userid, args=args) as event:
                    skill.execute(event.name, event)

                break

            i += 1

    return CommandReturn.BLOCK


@TypedClientCommand('ability')
def client_ability_command(command):
    wcsplayer = Player.from_index(command.index)
    active_race = wcsplayer.active_race

    for skill in active_race.skills.values():
        if skill.config['event'] == 'player_ability':
            skill.execute('player_ability', define=True)

            break

    return CommandReturn.BLOCK


@TypedClientCommand('ultimate')
def client_ultimate_command(command):
    wcsplayer = Player.from_index(command.index)
    active_race = wcsplayer.active_race

    for skill in active_race.skills.values():
        if skill.config['event'] == 'player_ultimate':
            skill.execute('player_ultimate', define=True)

            break

    return CommandReturn.BLOCK


# ============================================================================
# >> REPEATS
# ============================================================================
@Repeat
def save_data_repeat():
    for _, wcsplayer in PlayerReadyIter():
        wcsplayer.save()

    database_manager.execute('player offline', callback=_query_refresh_playerinfo)
save_data_repeat.start(60 * 1)
