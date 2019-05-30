# ../wcs/core/helpers/esc/est/converts.py

# ============================================================================
# >> IMPORTS
# ============================================================================
# Python Imports
#   Operator
from operator import add
from operator import sub

# Source.Python Imports
#   Filters
from filters.players import PlayerIter
#   Players
from players.entity import Player
from players.helpers import index_from_userid

# EventScripts Imports
#   ES
import es


# ============================================================================
# >> ALL DECLARATION
# ============================================================================
__all__ = ()


# ============================================================================
# >> CONSTANTS
# ============================================================================
_team_convert = {
    'c':'ct',
    't':'t',
    'a':'all',
    'l':'alive',
    's':'spec',
    'h':'human',
    'b':'bot',
    'd':'dead',
    'u':'un',
    '0':'un',
    '1':'spec',
    '2':'t',
    '3':'ct'
}

_operator_convert = {
    '+': add,
    '-': sub,
    '=': lambda dummy, value: value
}


# ============================================================================
# >> HELPER FUNCTIONS
# ============================================================================
def convert_userid_identifier_to_players(filter_):
    # TODO: Do not use es.getuserid
    userid = es.getuserid(filter_)

    try:
        index_from_userid(userid)
    except ValueError:
        players = set()
        append = True

        for x in filter_:
            if x == '#':
                append = True
            elif x == '!':
                append = False
            else:
                found_players = PlayerIter(_team_convert.get(x, x))

                if append:
                    players.update(found_players)
                else:
                    players = players.difference(found_players)

        yield from players
    else:
        yield from (Player.from_userid(userid), )


def convert_operator(value):
    return _operator_convert.get(value, _operator_convert['='])
