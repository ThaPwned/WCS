# ../wcs/core/translations/__init__.py

# ============================================================================
# >> IMPORTS
# ============================================================================
# Source.Python Imports
#   Translations
from translations.strings import LangStrings

# WCS Imports
#   Constants
from ..constants.paths import TRANSLATION_PATH


# ============================================================================
# >> ALL DECLARATION
# ============================================================================
__all__ = (
    'categories_strings',
    'chat_strings',
    'config_strings',
    'menu_strings',
)


# ============================================================================
# >> GLOBAL VARIABLES
# ============================================================================
# Language strings for the UI
categories_strings = LangStrings(TRANSLATION_PATH / 'categories_strings')
# Language strings for the chat
chat_strings = LangStrings(TRANSLATION_PATH / 'chat_strings')
# Language strings for the configuration
config_strings = LangStrings(TRANSLATION_PATH / 'config_strings')
# Language strings for the menus
menu_strings = LangStrings(TRANSLATION_PATH / 'menu_strings')
