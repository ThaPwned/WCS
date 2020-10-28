# ../wcs/core/helpers/wards.py

# ============================================================================
# >> IMPORTS
# ============================================================================
# Python Imports
#   Math
from math import inf
#   Time
from time import time
#   Warnings
from warnings import warn

# Source.Python Imports
#   Core
from core import SOURCE_ENGINE_BRANCH
from core import AutoUnload
#   Engines
from engines.trace import ContentMasks
from engines.trace import engine_trace
from engines.trace import GameTrace
from engines.trace import Ray
from engines.trace import TraceFilterSimple
#   Events
from events import Event
#   Filters
from filters.players import PlayerIter
#   Hooks
from hooks.exceptions import except_hooks
#   Listeners
from listeners import OnLevelInit
from listeners.tick import Repeat
from listeners.tick import RepeatStatus
#   Mathlib
from mathlib import Vector
#   Players

# WCS Imports
#   Config
from ..config import cfg_ffa_enabled
#   Helpers
from .effects import effect3
from .effects import effect10
from .effects import effect11
from .effects import effect106
#   Listeners
from ..listeners import OnPlayerDelete
#   Players
from ..players.entity import Player
from ..players.filters import PlayerReadyIter


# ============================================================================
# >> ALL DECLARATION
# ============================================================================
__all__ = (
    'BaseWard',
    'DamageWard',
    'ward_manager',
)


# =============================================================================
# >> CLASSES
# =============================================================================
class BaseWard(object):
    def __init__(self, owner, origin, radius, duration, tick_interval=1, update_interval=1, target_owner=True, **kwargs):
        assert isinstance(owner, Player)
        assert owner.ready

        self._team_target = None

        self.owner = owner
        self.origin = origin
        self.radius = radius
        self.duration = duration
        self.team = owner.player.team
        self.team_target = self.team
        self.tick_interval = tick_interval
        self.update_interval = update_interval
        self.target_owner = target_owner
        self.data = kwargs
        self.entities = {}

        self._next_tick = time()

    def on_spawned(self):
        pass

    def on_disappear(self):
        pass

    def on_tick(self):
        pass

    def on_removed(self):
        pass

    def on_enter(self, wcsplayer):
        pass

    def on_update(self, wcsplayer):
        pass

    def on_exit(self, wcsplayer):
        pass

    def on_disconnect(self, wcsplayer):
        pass

    def has_within(self, origin):
        return self.origin.get_distance_sqr(origin) <= self.radius ** 2

    @property
    def team_target(self):
        return self._team_target

    @team_target.setter
    def team_target(self, value):
        self._team_target = value


class DamageWard(BaseWard):
    def __init__(self, owner, origin, radius, duration, damage, tick_interval=1, update_interval=1, **kwargs):
        super().__init__(owner, origin, radius, duration, tick_interval, update_interval, target_owner=False, **kwargs)

        self.damage = damage
        self.team_target = 5 - self.team

        self.speed = {}

    @BaseWard.team_target.getter
    def team_target(self):
        if cfg_ffa_enabled.get_int():
            return None

        return self._team_target

    def on_spawned(self):
        # TODO: Find models for csgo (only tested in css)
        effect11('sprites/purpleglow1.vmt', self.origin[0], self.origin[1], self.origin[2] + 120, self.duration, 2, 50).create()
        effect3('sprites/lgtning.vmt', self.origin[0], self.origin[1], self.origin[2] + 120, self.origin[0], self.origin[1], self.origin[2], self.duration, 20, 20, 255 if self.team == 2 else 10, 0, 255 if self.team == 3 else 10, 150).create()
        effect10('sprites/lgtning.vmt', self.origin[0], self.origin[1], self.origin[2] + 4, self.radius * 2 - 1, self.radius * 2, self.duration, 12, 100, 1, 255, 150, 70, 100, 3).create()

    def on_disappear(self):
        for wcsplayer in list(self.speed.keys()):
            self.on_exit(wcsplayer)

    def on_tick(self):
        # TODO: Find models for csgo (only tested in css)
        effect10('sprites/lgtning.vmt', self.origin[0], self.origin[1], self.origin[2] + 4, 20, self.radius * 2, 1, 20, 100, 1, 255, 150, 70, 100, 10).create()

    def on_enter(self, wcsplayer):
        self.on_update(wcsplayer)

        player = wcsplayer.player
        modified = player.speed * 0.3

        self.speed[wcsplayer] = modified

        player.speed -= modified

    def on_update(self, wcsplayer):
        vector = Vector(*wcsplayer.player.origin)

        # TODO: Find models for csgo (only tested in css)
        effect3('sprites/lgtning.vmt', self.origin[0], self.origin[1], self.origin[2] + 4, vector[0], vector[1], vector[2], 1, 10, 20, 255, 150, 70, 255).create()

        wcsplayer.take_damage(self.damage, self.owner.index, weapon='ward')

    def on_exit(self, wcsplayer):
        modified = self.speed.pop(wcsplayer, None)

        if modified is not None:
            wcsplayer.player.speed += modified


class _WardManager(AutoUnload, list):
    def __init__(self):
        super().__init__()

        self._repeat = Repeat(self._tick)
        self._filter = PlayerReadyIter(is_filters='alive')

    def _unload_instance(self):
        if self._repeat.status == RepeatStatus.RUNNING:
            self._repeat.stop()

    def _tick(self):
        now = time()
        players = {wcsplayer:player.origin for player, wcsplayer in self._filter}

        for wcsplayer in list(players.keys()):
            if wcsplayer.player.dead:
                warn(f'Player "{wcsplayer.name}" should NOT be here')

                del players[wcsplayer]

        ignore = TraceFilterSimple(PlayerIter())

        for ward in self.copy():
            if ward._next_tick <= now:
                try:
                    ward.on_tick()
                except:
                    except_hooks.print_exception()

                    try:
                        ward.on_disappear()
                    except:
                        except_hooks.print_exception()

                    self.remove(ward)

                    continue
                else:
                    ward._next_tick = now + ward.tick_interval

                    ward.duration -= 1

                    if not ward.duration:
                        try:
                            ward.on_disappear()
                        except:
                            except_hooks.print_exception()

                        self.remove(ward)

            entities = ward.entities
            team = ward.team_target

            for wcsplayer, origin in players.items():
                if not ward.target_owner and wcsplayer == ward.owner:
                    continue

                if team is None or wcsplayer.player.team == team:
                    trace = GameTrace()
                    ray = Ray(ward.origin, origin)

                    engine_trace.trace_ray(ray, ContentMasks.ALL, ignore, trace)

                    if ward.has_within(origin) and not trace.did_hit_world():
                        if wcsplayer in entities:
                            if entities[wcsplayer] <= now:
                                entities[wcsplayer] = now + ward.update_interval

                                try:
                                    ward.on_update(wcsplayer)
                                except:
                                    except_hooks.print_exception()
                        else:
                            entities[wcsplayer] = now + ward.update_interval

                            try:
                                ward.on_enter(wcsplayer)
                            except:
                                except_hooks.print_exception()
                    else:
                        if wcsplayer in entities:
                            del entities[wcsplayer]

                            try:
                                ward.on_exit(wcsplayer)
                            except:
                                except_hooks.print_exception()

    def append(self, ward):
        if not self:
            self._repeat.start(0.1)

        try:
            ward.on_spawned()
        except:
            except_hooks.print_exception()

        super().append(ward)

    def remove(self, ward):
        super().remove(ward)

        try:
            ward.on_removed()
        except:
            except_hooks.print_exception()

        if not self:
            self._repeat.stop()
ward_manager = _WardManager()


# =============================================================================
# >> LISTENERS
# =============================================================================
@OnLevelInit
def on_level_init(map_name):
    for ward in list(ward_manager):
        ward_manager.remove(ward)


@OnPlayerDelete
def on_player_delete(wcsplayer):
    for ward in ward_manager:
        if ward.owner == wcsplayer:
            ward_manager.remove(ward)
        elif wcsplayer in ward.entities:
            try:
                ward.on_disconnect(wcsplayer)
            except:
                except_hooks.print_exception()

            del ward.entities[wcsplayer]


# =============================================================================
# >> EVENTS
# =============================================================================
@Event('round_prestart' if SOURCE_ENGINE_BRANCH == 'csgo' else 'round_start')
def round_prestart(event):
    for ward in list(ward_manager):
        ward_manager.remove(ward)


@Event('player_team')
def player_team(event):
    userid = event['userid']
    wcsplayer = Player.from_userid(userid)

    if wcsplayer.ready:
        team = event['team']

        for ward in list(ward_manager):
            if ward.owner == wcsplayer and ward.team != team:
                ward_manager.remove(ward)
