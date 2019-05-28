# ../wcs/core/helpers/esc/converts.py

# ============================================================================
# >> IMPORTS
# ============================================================================
# Source.Python Imports
#   Filters
from filters.players import PlayerIter
#   Mathlib
from mathlib import Vector
#   Players
from players.entity import Player
from players.helpers import index_from_userid

# WCS Imports
#   Players
from ...players.entity import Player as WCSPlayer


# ============================================================================
# >> HELPER FUNCTIONS
# ============================================================================
def valid_userid(userid):
    try:
        userid = int(userid)
        index_from_userid(userid)
    except ValueError:
        return None

    return userid


def valid_userid_and_team(userid):
    new_userid = valid_userid(userid)

    if new_userid is None:
        if userid in ('T', 'CT'):
            return userid

        return None

    return new_userid


def convert_userid_to_player(userid):
    userid = valid_userid(userid)

    if userid is None:
        return None

    player = Player.from_userid(userid)

    if player.dead:
        return None

    return player


def convert_userid_to_wcsplayer(userid):
    userid = valid_userid(userid)

    if userid is None:
        return None

    return WCSPlayer.from_userid(userid)


def convert_identifier_to_players(filter_):
    filter_ = filter_.split(',')
    is_filters = [x.replace('#', '') for x in filter_ if x.startswith('#')]
    not_filters = [x.replace('!', '') for x in filter_ if x.startswith('!')]

    for player in PlayerIter(is_filters=is_filters, not_filters=not_filters):
        yield player


def convert_userid_identifier_to_players(filter_):
    if filter_.isdigit():
        try:
            yield Player.from_userid(int(filter_))
        except ValueError:
            yield StopIteration()
    else:
        yield from convert_identifier_to_players(filter_)


def real_value(value):
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            return value


def valid_operators(operators=('=', '+', '-')):
    def validate_operator(value):
        return value if value in operators else '='

    return validate_operator


def clamp(min_value=None, max_value=None, type_=int):
    def clamping(value):
        value = type_(value)

        return min_value if (min_value is not None and value < min_value) else max_value if (max_value is not None and value > max_value) else value

    return clamping


def convert_to_vector(vector):
    return Vector(*[float(x) for x in vector.split(',')])


def optional(type_):
    def convert(value):
        if value == '0':
            return None

        return type_(value)

    return convert


def split_str(separators=[',', ';']):
    def splitter(value):
        for separator in separators:
            if separator in value:
                return value.split(separator)

        return [value]

    return splitter


def deprecated(value):
    return None
