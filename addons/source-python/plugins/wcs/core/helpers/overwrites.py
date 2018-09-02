# ../wcs/core/helpers/overwrites.py

# ============================================================================
# >> IMPORTS
# ============================================================================
# Source.Python
#   Core
from core import SOURCE_ENGINE_BRANCH
#   Messages
from messages import SayText2 as _SayText2


# ============================================================================
# >> ALL DECLARATION
# ============================================================================
__all__ = (
    'COLOR_DARKGREEN',
    'COLOR_DEFAULT',
    'COLOR_GREEN',
    'COLOR_LIGHTGREEN',
    'SayText2',
)


# ============================================================================
# >> GLOBAL VARIABLES
# ============================================================================
# Copied from EventScripts Emulator (es_emulator/helpers.py#90-99)
if SOURCE_ENGINE_BRANCH == 'csgo':
    COLOR_DEFAULT = '\1'
    COLOR_GREEN = '\4'
    COLOR_LIGHTGREEN = '\5'
    COLOR_DARKGREEN = '\6'
else:
    COLOR_DEFAULT = '\1'
    COLOR_GREEN = '\4'
    COLOR_LIGHTGREEN = '\3'
    COLOR_DARKGREEN = '\5'


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
