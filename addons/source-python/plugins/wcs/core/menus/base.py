# ../wcs/core/menus/base.py

# ============================================================================
# >> IMPORTS
# ============================================================================
# Source.Python Imports
#   Menus
from menus.base import _translate_text
from menus.radio import PagedRadioMenu as _PagedRadioMenu
from menus.radio import PagedRadioOption as _PagedRadioOption
from menus.radio import BUTTON_BACK
from menus.radio import BUTTON_NEXT
from menus.radio import BUTTON_CLOSE_SLOT

# WCS Imports
#   Translations
from ..translations import menu_strings


# ============================================================================
# >> ALL DECLARATION
# ============================================================================
__all__ = (
    'PagedMenu',
    'PagedPageCountMenu',
    'PagedOption',
)


# ============================================================================
# >> CLASSES
# ============================================================================
class PagedMenu(_PagedRadioMenu):
    def __init__(self, *args, **kwargs):
        kwargs['top_separator'] = ' '
        kwargs['bottom_separator'] = None

        super().__init__(*args, **kwargs)

    def _format_header(self, player_index, page, slots):
        buffer = '{0}\n'.format(_translate_text(self.title, player_index) if self.title else '')

        if self.description is not None:
            buffer += _translate_text(self.description, player_index) + '\n'

        if self.top_separator is not None:
            buffer += self.top_separator + '\n'

        return buffer

    def _format_footer(self, player_index, page, slots):
        buffer = ''

        if self.bottom_separator is not None:
            buffer += self.bottom_separator + '\n'

        if page.index > 0 or self.parent_menu is not None:
            buffer += _PagedRadioOption(menu_strings['back'])._render(player_index, BUTTON_BACK)

            slots.add(BUTTON_BACK)
        else:
            buffer += ' \n'

        if page.index < self.last_page_index:
            buffer += _PagedRadioOption(menu_strings['next'])._render(player_index, BUTTON_NEXT)

            slots.add(BUTTON_NEXT)
        else:
            buffer += ' \n'

        buffer += _PagedRadioOption(
            menu_strings['close'], highlight=False)._render(player_index, BUTTON_CLOSE_SLOT)

        return buffer


class PagedPageCountMenu(PagedMenu):
    def _format_header(self, player_index, page, slots):
        return _PagedRadioMenu._format_header(self, player_index, page, slots)


class PagedOption(_PagedRadioOption):
    def __init__(self, text, value=None, highlight=True, selectable=True, show_index=True):
        super().__init__(text, value, highlight, selectable)

        self.show_index = show_index

    def _render(self, player_index, choice_index):
        return '{0}{1}{2}\n'.format(
            self._get_highlight_prefix(),
            '{}. '.format(choice_index) if self.show_index else '',
            _translate_text(self.text, player_index)
        )
