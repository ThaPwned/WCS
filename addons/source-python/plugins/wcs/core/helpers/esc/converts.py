# ../wcs/core/helpers/esc/converts.py

# ============================================================================
# >> IMPORTS
# ============================================================================
# Source.Python Imports
#   Filters
from filters.players import PlayerIter
#   Mathlib
from mathlib import QAngle
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

    return Player.from_userid(userid)


def convert_userid_to_alive_player(userid):
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


def any_value(value):
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

    validate_operator.__name__ = 'operator (' + ', '.join(operators) + ')'

    return validate_operator


def clamp(min_value=None, max_value=None, is_int=True):
    def clamping(value):
        value = int(float(value)) if is_int else float(value)

        return min_value if (min_value is not None and value < min_value) else max_value if (max_value is not None and value > max_value) else value

    clamping.__name__ = 'int' if is_int else 'float'

    if min_value is None and max_value is None:
        return clamping

    clamping.__name__ += ' ('

    if min_value is not None:
        clamping.__name__ += f'min. {min_value}'

        if max_value is not None:
            clamping.__name__ += ' '

    if max_value is not None:
        clamping.__name__ += f'max. {max_value}'

    clamping.__name__ += ')'

    return clamping


def convert_to_vector(vector):
    return Vector(*[float(x) for x in vector.split(',')])


def convert_to_qangle(angle):
    return QAngle(*[float(x) for x in angle.split(',')])


def optional(type_):
    def convert(value):
        if value == '0':
            return None

        return type_(value)

    convert.__name__ = type_.__name__

    return convert


def split_str(separators=[',', ';']):
    def splitter(value):
        for separator in separators:
            if separator in value:
                return value.split(separator)

        return [value]

    splitter.__name__ = 'str (separated by ' + ' or '.join(separators) + ')'

    return splitter


def deprecated(value):
    return None


# ============================================================================
# >> FUNCTION DOCUMENTATION
# ============================================================================
valid_userid.__name__ = 'userid'
valid_userid_and_team.__name__ = 'userid or team (T or CT)'
convert_userid_to_player.__name__ = 'userid'
convert_userid_to_alive_player.__name__ = 'userid'
convert_userid_to_wcsplayer.__name__ = 'userid'
convert_identifier_to_players.__name__ = 'player filter'
convert_userid_identifier_to_players.__name__ = 'userid or player filter'
any_value.__name__ = 'any'
convert_to_vector.__name__ = 'vector (x,y,z)'
convert_to_qangle.__name__ = 'angle (p,y,r)'
