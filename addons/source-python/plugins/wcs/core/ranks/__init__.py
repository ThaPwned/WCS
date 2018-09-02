# ../wcs/core/ranks/__init__.py

# ============================================================================
# >> IMPORTS
# ============================================================================
# Python Imports
#   Copy
from copy import deepcopy

# WCS Imports
#   Listeners
from ..listeners import OnPlayerChangeRace
from ..listeners import OnPlayerLevelUp
from ..listeners import OnPlayerQuery
from ..listeners import OnPlayerRankUpdate
#   Menus
from ..menus import wcstop_menu
from ..menus.base import PagedOption
#   Translations
from ..translations import menu_strings


# ============================================================================
# >> ALL DECLARATION
# ============================================================================
__all__ = (
    'rank_manager',
)


# ============================================================================
# >> CLASSES
# ============================================================================
class _RankManager(list):
    def __init__(self):
        super().__init__()

        self._data = {}

    def __getitem__(self, item):
        try:
            return super().__getitem__(item)
        except TypeError:
            try:
                return self.index(item) + 1
            except ValueError:
                return len(self)

    def _update(self, wcsplayer, value):
        uniqueid = wcsplayer.uniqueid

        self._data[uniqueid]['total_level'] += value

        index = self.index(uniqueid)
        curlevel = self._data[uniqueid]['total_level']
        swap = None

        # TODO: Implement negative ranking (for reset)
        # TODO: Use "Standard competition ranking ("1224" ranking)" (use a list for same rank - (rank + 1) should be set to None)
        if value > 0:
            for i, other in enumerate(reversed(self[:index]), 1):
                if curlevel >= self._data[other]['total_level']:
                    swap = index - i
                else:
                    break

            if swap is None:
                return

            self.pop(index)
            self.insert(swap, uniqueid)

            OnPlayerRankUpdate.manager.notify(wcsplayer, index, swap)

        if swap is None:
            return

        for i, option in enumerate(wcstop_menu):
            if option.value == uniqueid:
                wcstop_menu.insert(swap - (1 if i < swap else 0), wcstop_menu.pop(i))
                break

    @property
    def last_place(self):
        return len(self)
rank_manager = _RankManager()


# ============================================================================
# >> LISTENERS
# ============================================================================
@OnPlayerChangeRace
def on_player_change_race(wcsplayer, old, new):
    rank_manager._data[wcsplayer.uniqueid]['current_race'] = new


@OnPlayerLevelUp
def on_player_level_up(wcsplayer, race, from_level):
    rank_manager._update(wcsplayer, race.level - from_level)


@OnPlayerQuery
def on_player_query(wcsplayer):
    uniqueid = wcsplayer.uniqueid

    for option in wcstop_menu:
        if option.value == uniqueid:
            break
    else:
        total_level = wcsplayer.total_level

        rank_manager._data[uniqueid] = {'name':wcsplayer.name, 'current_race':wcsplayer.current_race, 'total_level':total_level}

        option = PagedOption(deepcopy(menu_strings['wcstop_menu line']), uniqueid, show_index=False)
        option.text.tokens['name'] = wcsplayer.name

        if rank_manager:
            total = len(rank_manager)

            for i, other in enumerate(reversed(rank_manager)):
                if total_level <= rank_manager._data[other]['total_level']:
                    rank_manager.insert(total - i + 1, uniqueid)

                    wcstop_menu.insert(total - i + 1, option)

                    break
        else:
            rank_manager.append(uniqueid)
            wcstop_menu.append(option)
