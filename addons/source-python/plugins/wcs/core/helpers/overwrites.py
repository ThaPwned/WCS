# ../wcs/core/helpers/overwrites.py

# ============================================================================
# >> IMPORTS
# ============================================================================
# Source.Python Imports
#   Messages
from messages import SayText2 as _SayText2

# WCS Imports
#   Constants
from ...constants import COLOR_DARKGREEN
from ...constants import COLOR_DEFAULT
from ...constants import COLOR_GREEN
from ...constants import COLOR_LIGHTGREEN


# ============================================================================
# >> ALL DECLARATION
# ============================================================================
__all__ = (
    'SayText2',
)


# ============================================================================
# >> CLASSES
# ============================================================================
class SayText2(_SayText2):
    def send(self, *player_indexes, **tokens):
        tokens['default'] = COLOR_DEFAULT
        tokens['green'] = COLOR_GREEN
        tokens['lightgreen'] = COLOR_LIGHTGREEN
        tokens['darkgreen'] = COLOR_DARKGREEN

        super().send(*player_indexes, **tokens)

    def _send(self, player_indexes, translated_kwargs):
        translated_kwargs.message = f'{COLOR_GREEN}[WCS] {COLOR_LIGHTGREEN}{translated_kwargs.message}'

        super()._send(player_indexes, translated_kwargs)
