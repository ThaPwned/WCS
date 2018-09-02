# ../wcs/core/players/iterator.py

# ============================================================================
# >> IMPORTS
# ============================================================================
# Source.Python Imports
#   Filters
from filters.players import PlayerIter as _PlayerIter

# WCS Imports
#   Player
from .entity import Player


# ============================================================================
# >> ALL DECLARATION
# ============================================================================
__all__ = (
    'PlayerIter',
    'PlayerReadyIter',
)


# ============================================================================
# >> CLASSES
# ============================================================================
class PlayerIter(_PlayerIter):
    def __iter__(self):
        for item in self.iterator():
            valid, wcsplayer = self._is_valid(item)

            if valid:
                yield item, wcsplayer

    def _is_valid(self, item):
        if super()._is_valid(item):
            return True, Player.from_index(item.index)

        return False, None


class PlayerReadyIter(PlayerIter):
    def __init__(self, is_filters=None, not_filters=None, ready=True):
        super().__init__(is_filters, not_filters)

        self.ready = ready

    def _is_valid(self, item):
        valid, wcsplayer = super()._is_valid(item)

        if valid:
            return wcsplayer.ready == self.ready, wcsplayer

        return False, None


# ============================================================================
# >> GLOBAL VARIABLES
# ============================================================================
PlayerIter._filters = _PlayerIter._filters
PlayerReadyIter._filters = _PlayerIter._filters
