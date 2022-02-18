# ../wcs/core/players/__init__.py

# ============================================================================
# >> IMPORTS
# ============================================================================
import warnings

# Source.Python Imports
from engines.server import engine_server
from engines.server import global_vars
from entities.helpers import edict_from_index
from entities.helpers import index_from_edict
#   Entities
from entities.entity import Entity
#   Filters
from filters.players import PlayerIter
#   Listeners
from listeners import OnClientConnect as _OnClientConnect
from listeners import OnClientDisconnect as _OnClientDisconnect
from listeners import OnClientPutInServer
from listeners import OnEntityDeleted
from listeners import OnTick
from players.helpers import playerinfo_from_edict
from players.helpers import userid_from_edict

from ..listeners import OnClientAuthorized
from ..listeners import OnClientConnect
from ..listeners import OnClientDisconnect
from ..listeners import OnSettingsLoaded


# ============================================================================
# >> ALL DECLARATION
# ============================================================================
__all__ = (
    'BasePlayer',
    'set_weapon_name',
    'team_data',
    'index_from_accountid',
)


# ============================================================================
# >> GLOBAL VARIABLES
# ============================================================================
team_data = {2:{}, 3:{}}

_global_weapon_entity = None
_allow_authentication = False
_authenticate = set()
_bots = set()


# ============================================================================
# >> CLASSES
# ============================================================================
class _PlayerMeta(type):
    def __new__(mcs, name, bases, odict):
        cls = super().__new__(mcs, name, bases, odict)
        cls._players = {}

        return cls

    def __call__(cls, index):
        assert isinstance(index, int), index

        baseplayer = cls._players.get(index)

        if baseplayer is None:
            baseplayer = cls._players[index] = super().__call__(index)

        return baseplayer


class BasePlayer(object, metaclass=_PlayerMeta):
    def __init__(self, index):
        self._index = index
        self._userid = None
        self._name = None
        self._edict = None
        self._authorized = False
        self._connected = False
        self._fake_client = False
        self._accountid = None
        self._steamid2 = None
        self._steamid3 = None
        self._uniqueid = None

    @property
    def index(self):
        return self._index

    @property
    def userid(self):
        return self._userid

    @property
    def name(self):
        return self._name

    @property
    def edict(self):
        return self._edict

    @property
    def authorized(self):
        return self._authorized

    @property
    def connected(self):
        return self._connected

    @property
    def fake_client(self):
        return self._fake_client

    @property
    def accountid(self):
        return self._accountid

    @property
    def steamid2(self):
        return self._steamid2

    @property
    def steamid3(self):
        return self._steamid3

    @property
    def uniqueid(self):
        return self._uniqueid

    @classmethod
    def from_edict(cls, edict):
        return cls(index_from_edict(edict))

    @classmethod
    def from_userid(cls, userid):
        for baseplayer in cls._players.values():
            if userid == baseplayer.userid:
                return baseplayer

        raise ValueError(userid)


# ============================================================================
# >> FUNCTIONS
# ============================================================================
def set_weapon_name(name, prefix='wcs'):
    global _global_weapon_entity

    if _global_weapon_entity is None:
        _global_weapon_entity = Entity.create('info_target')

    _global_weapon_entity.set_key_value_string('classname', ('' if prefix is None else prefix + '_') + name)

    return _global_weapon_entity.index


def index_from_accountid(accountid):
    if isinstance(accountid, str):
        for player in PlayerIter('bot'):
            if player.name == accountid:
                return player.index

        raise ValueError(accountid)

    for player in PlayerIter('human'):
        if player.raw_steamid.account_id == accountid:
            return player.index

    raise ValueError(accountid)


# ============================================================================
# >> LISTENERS
# ============================================================================
@OnEntityDeleted
def on_entity_deleted(base_entity):
    if not base_entity.is_networked():
        return

    global _global_weapon_entity

    if _global_weapon_entity is not None:
        if base_entity.index == _global_weapon_entity.index:
            _global_weapon_entity = None


@_OnClientConnect
def _on_client_connect(allow_connect_ptr, edict, name, address, reject_msg_ptr, reject_msg_len):
    baseplayer = BasePlayer.from_edict(edict)
    baseplayer._edict = edict
    baseplayer._name = name

    if baseplayer.connected:
        _on_client_disconnect(baseplayer.index)

        baseplayer = BasePlayer.from_edict(edict)

    baseplayer._connected = True
    baseplayer._userid = userid_from_edict(edict)

    if not baseplayer._authorized:
        if baseplayer._fake_client:
            baseplayer._accountid = name
            baseplayer._steamid2 = 'BOT'
            baseplayer._uniqueid = f'BOT_{name}'
            baseplayer._authorized = True
        else:
            _authenticate.add(baseplayer)

    OnClientConnect.manager.notify(baseplayer)


@_OnClientDisconnect
def _on_client_disconnect(index):
    baseplayer = BasePlayer(index)

    if not baseplayer.connected:
        return

    baseplayer = BasePlayer._players.pop(index)

    OnClientDisconnect.manager.notify(baseplayer)
    baseplayer._connected = False

    _authenticate.discard(baseplayer)


@OnClientPutInServer
def on_client_put_in_server(edict, name):
    baseplayer = BasePlayer.from_edict(edict)

    if not baseplayer.connected:
        baseplayer._fake_client = True

        _on_client_connect(None, edict, name, None, None, None)

        baseplayer._accountid = name
        baseplayer._steamid2 = 'BOT'
        baseplayer._uniqueid = f'BOT_{name}'
        baseplayer._authorized = True

        if _authenticate:
            _bots.add(baseplayer)
        else:
            OnClientAuthorized.manager.notify(baseplayer)


@OnTick
def on_tick():
    if _allow_authentication:
        for baseplayer in _authenticate.copy():
            if engine_server.is_client_fully_authenticated(baseplayer.edict):
                _initialize(baseplayer)


@OnSettingsLoaded
def on_settings_loaded(settings):
    # The settings has been loaded, and any updates to the database has been queued
    global _allow_authentication
    _allow_authentication = True


# ============================================================================
# >> FUNCTIONS
# ============================================================================
def _initialize_players():
    for i in range(1, global_vars.max_clients + 1):
        try:
            edict = edict_from_index(i)
        except ValueError:
            pass
        else:
            baseplayer = BasePlayer(i)
            baseplayer._edict = edict
            baseplayer._userid = userid_from_edict(edict)
            baseplayer._name = playerinfo_from_edict(edict).name
            baseplayer._connected = True
            baseplayer._fake_client = playerinfo_from_edict(edict).is_fake_client()

            if baseplayer._fake_client:
                baseplayer._accountid = baseplayer._name
                baseplayer._steamid2 = 'BOT'
                baseplayer._uniqueid = f'BOT_{baseplayer.name}'
                baseplayer._authorized = True

                _bots.add(baseplayer)
            else:
                if _allow_authentication and engine_server.is_client_fully_authenticated(baseplayer.edict):
                    _initialize(baseplayer)
                else:
                    _authenticate.add(baseplayer)

    if not _authenticate:
        for baseplayer in _bots:
            OnClientAuthorized.manager.notify(baseplayer)

        _bots.clear()


def _initialize(baseplayer):
    # Wait until we can retrieve a playerinfo from the baseplayer (prevents a lot of errors further on)
    try:
        playerinfo_from_edict(baseplayer.edict)
    except ValueError:
        pass
    else:
        steamid = engine_server.get_client_steamid(baseplayer._edict)

        _authenticate.discard(baseplayer)

        baseplayer._accountid = steamid.account_id
        baseplayer._uniqueid = baseplayer._steamid2 = steamid.to_steamid2()
        baseplayer._steamid3 = steamid.to_steamid3()
        baseplayer._authorized = True

        OnClientAuthorized.manager.notify(baseplayer)

    # Are there no more human players waiting to get authenticated?
    if not _authenticate:
        for baseplayer in _bots:
            OnClientAuthorized.manager.notify(baseplayer)

        _bots.clear()


def add_race_limit(team, race, userid):
    race_key = f'_internal_{race}_limit_allowed'

    if race_key not in team_data[team]:
        team_data[team][race_key] = []

    team_data[team][race_key].append(userid)

def _remove_race_limit_key(team, race_key, userid):
    team_data[team][race_key].remove(userid)

    if not team_data[team][race_key]:
        del team_data[team][race_key]

def remove_race_limit(team, race, userid):
    race_key = f'_internal_{race}_limit_allowed'

    try:
        _remove_race_limit_key(team, race_key, userid)

    except (KeyError, ValueError) as e:
        other_teams = (x for x in team_data.keys() if x != team)
        for t in other_teams:
            if race_key in team_data[t] and userid in team_data[t][race_key]:
                _remove_race_limit_key(t, race_key, userid)
                warnings.warn(
                    "After failing to remove userid:%s from teamlimit, "
                    "they were found counting toward the enemy's (team:%s) limit" % (userid, t)
                )
                break
        else:
            warnings.warn("Could not remove userid:%s from teamlimit for any team:\n %s" % (userid, e))
