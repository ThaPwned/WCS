# ../wcs/core/emulate/__init__.py

# ============================================================================
# >> IMPORTS
# ============================================================================
# Python Imports
#   Random
from random import random

# Source.Python Imports
#   Listeners
from listeners import OnConVarChanged
from listeners.tick import Repeat
from listeners.tick import RepeatStatus

# AvsD Imports
#   Config
from ..config import cfg_bot_ability_chance
#   Constants
from ..constants import ModuleType
from ..constants import SkillReason
#   Events
from ..events import FakeEvent
#   Players
from ..players.filters import PlayerReadyIter


# ============================================================================
# >> ALL DECLARATION
# ============================================================================
__all__ = (
    'emulate_manager',
)


# ============================================================================
# >> CLASSES
# ============================================================================
class _EmulateManager(object):
    def __init__(self):
        self._repeat = Repeat(self.tick)
        self._filter = PlayerReadyIter(['bot', 'alive'])

    def tick(self):
        chance = cfg_bot_ability_chance.get_float()

        for _, wcsplayer in self._filter:
            active_race = wcsplayer.active_race

            for skill_name in active_race.settings.config['skills']:
                if random() <= chance:
                    skill = active_race.skills[skill_name]

                    for event in ('player_ultimate', 'player_ability', 'player_ability_on', 'player_ability_off'):
                        if event in skill.config['event']:
                            if skill.is_executable() is SkillReason.ALLOWED:
                                if event == 'player_ultimate':
                                    if skill._type is ModuleType.ESS_INI or skill._type is ModuleType.ESS_KEY:
                                        skill.reset_cooldown()

                                    skill.execute('player_ultimate', define=True)
                                elif event == 'player_ability':
                                    if skill._type is ModuleType.ESS_INI or skill._type is ModuleType.ESS_KEY:
                                        skill.reset_cooldown()

                                    skill.execute('player_ability', define=True)
                                elif event == 'player_ability_on':
                                    with FakeEvent('player_ability_on' if skill._type is ModuleType.SP else f'{skill_name}_on', userid=wcsplayer.userid) as event:
                                        skill.execute(event.name, event)
                                elif event == 'player_ability_off':
                                    with FakeEvent('player_ability_off' if skill._type is ModuleType.SP else f'{skill_name}_off', userid=wcsplayer.userid) as event:
                                        skill.execute(event.name, event)

                            break

    def start(self):
        if self._repeat.status != RepeatStatus.RUNNING:
            self._repeat.start(1)

    def stop(self):
        if self._repeat.status == RepeatStatus.RUNNING:
            self._repeat.stop()
emulate_manager = _EmulateManager()


# ============================================================================
# >> LISTENERS
# ============================================================================
@OnConVarChanged
def on_convar_changed(convar, old_value):
    if convar.name == 'wcs_bot_ability_chance':
        if convar.get_float():
            emulate_manager.start()
        else:
            emulate_manager.stop()
