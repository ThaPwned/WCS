# ../wcs/core/menus/base.py

# ============================================================================
# >> IMPORTS
# ============================================================================
# Source.Python Imports
#   Core
from core import GAME_NAME
#   Keyvalues
from _keyvalues import KeyValues
#   Menus
from menus import Text
from menus.base import _translate_text

if GAME_NAME in ('hl2mp', ):
    from menus.esc import SimpleESCOption as _SimpleOption
    from menus.esc import SimpleESCMenu as _SimpleMenu
    from menus.esc import PagedESCMenu as _PagedMenu
    from menus.esc import PagedESCOption as _PagedOption
    from menus.queue import ESC_SELECTION_CMD

    BUTTON_BACK = 6
    BUTTON_NEXT = 7
    BUTTON_CLOSE = 8
    BUTTON_CLOSE_SLOT = 0
    MAX_ITEM_COUNT = 5
else:
    from menus.radio import SimpleRadioOption as _SimpleOption
    from menus.radio import SimpleRadioMenu as _SimpleMenu
    from menus.radio import PagedRadioMenu as _PagedMenu
    from menus.radio import PagedRadioOption as _PagedOption
    from menus.radio import BUTTON_BACK
    from menus.radio import BUTTON_NEXT
    from menus.radio import BUTTON_CLOSE
    from menus.radio import BUTTON_CLOSE_SLOT
    from menus.radio import MAX_ITEM_COUNT

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
if GAME_NAME in ('hl2mp', ):
    class SimpleOption(_SimpleOption):
        def _render(self, player_index, choice_index=None):
            return _translate_text(self.text, player_index)


    class SimpleMenu(_SimpleMenu):
        def _get_menu_data(self, player_index):
            data = KeyValues('menu')
            data.set_string(
                'msg', _translate_text(self.description or '', player_index))

            if self.title is not None:
                data.set_string(
                    'title', _translate_text(self.title, player_index))

            data.set_color('color', self.title_color)

            page = self._player_pages[player_index]
            page.options = {}

            for raw_data in self:
                if isinstance(raw_data, SimpleOption):
                    page.options[raw_data.choice_index] = raw_data
                    button = data.find_key(str(raw_data.choice_index), True)
                    button.set_string('msg', raw_data._render(player_index))
                    button.set_string('command', '{0} {1}'.format(
                        ESC_SELECTION_CMD, raw_data.choice_index))

            return data


    class PagedMenu(_PagedMenu):
        def _format_header(self, player_index, page, data):
            if self.title is not None:
                data.set_string('title', _translate_text(self.title, player_index))

            data.set_color('color', self.title_color)

        def _format_footer(self, player_index, page, data):
            button = data.find_key('6', True)
            button.set_string('msg', _translate_text(menu_strings['back'], player_index) if page.index > 0 or self.parent_menu is not None else '')
            button.set_string('command', '{0} 6'.format(ESC_SELECTION_CMD))

            button = data.find_key('7', True)
            button.set_string('msg', _translate_text(menu_strings['next'], player_index) if page.index < self.last_page_index else '')
            button.set_string('command', '{0} 7'.format(ESC_SELECTION_CMD))

            button = data.find_key('0', True)
            button.set_string('msg', _translate_text(menu_strings['close'], player_index))
            button.set_string('command', '{0} 0'.format(ESC_SELECTION_CMD))


    class PagedPageCountMenu(PagedMenu):
        def _format_header(self, player_index, page, data):
            info = '[{0}/{1}]'.format(page.index + 1, self.page_count)

            if self.title is not None:
                data.set_string('title', '{0} {1}'.format(
                    _translate_text(self.title, player_index), info))
            else:
                data.set_string('title', info)

            data.set_color('color', self.title_color)


    class PagedOption(_PagedOption):
        def __init__(self, text, value=None, highlight=True, selectable=True, show_index=True):
            super().__init__(text, value, highlight, selectable)

            self.show_index = show_index

        def _render(self, player_index, choice_index):
            return '{0}{1}'.format(
                '{}. '.format(choice_index) if self.show_index else '', _translate_text(self.text, player_index))
else:
    class SimpleOption(_SimpleOption):
        pass


    class SimpleMenu(_SimpleMenu):
        pass


    class PagedMenu(_PagedMenu):
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
                buffer += PagedOption(menu_strings['back'])._render(player_index, BUTTON_BACK)

                slots.add(BUTTON_BACK)
            else:
                buffer += ' \n'

            if page.index < self.last_page_index:
                buffer += PagedOption(menu_strings['next'])._render(player_index, BUTTON_NEXT)

                slots.add(BUTTON_NEXT)
            else:
                buffer += ' \n'

            buffer += PagedOption(
                menu_strings['close'], highlight=False)._render(player_index, BUTTON_CLOSE_SLOT)

            return buffer


    class PagedPageCountMenu(PagedMenu):
        def _format_header(self, player_index, page, slots):
            return _PagedMenu._format_header(self, player_index, page, slots)


    class PagedOption(_PagedOption):
        def __init__(self, text, value=None, highlight=True, selectable=True, show_index=True):
            super().__init__(text, value, highlight, selectable)

            self.show_index = show_index

        def _render(self, player_index, choice_index):
            return '{0}{1}{2}\n'.format(
                self._get_highlight_prefix(),
                '{}. '.format(choice_index) if self.show_index else '',
                _translate_text(self.text, player_index)
            )
