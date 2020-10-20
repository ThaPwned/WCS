# ../wcs/core/database/manager.py

# ============================================================================
# >> IMPORTS
# ============================================================================
# Python Imports
#   JSON
from json import dump as json_dump
from json import load as json_load
#   PyMySQL
from pymysql import connect as mysql_connect
#   SQLite3
from sqlite3 import connect as sqlite_connect

# WCS Imports
#   Constants
from ..constants import DatabaseVersion
from ..constants import NodeType
from ..constants.paths import CFG_PATH
from ..constants.paths import DATA_PATH
from ..constants.paths import STRUCTURE_PATH
#   Database
from .thread import _Node
from .thread import _queue
from .thread import _thread
from .thread import _repeat
#   Listeners
from ..listeners import OnSettingsLoaded


# ============================================================================
# >> ALL DECLARATION
# ============================================================================
__all__ = (
    'database_manager',
    'settings',
    'statements',
)


# ============================================================================
# >> CONFIGURATION
# ============================================================================
_path = CFG_PATH.joinpath('database.json')

if _path.isfile():
    with open(_path) as inputfile:
        _database = json_load(inputfile)
else:
    _database = {}
    _database['driver'] = 'sqlite'
    _database['host'] = 'localhost'
    _database['database'] = 'wcs_database'
    _database['user'] = 'root'
    _database['password'] = ''
    _database['timeout'] = 60
    _database['port'] = 3306

    with open(_path, 'w') as outputfile:
        json_dump(_database, outputfile, indent=4)


# ============================================================================
# >> GLOBAL VARIABLES
# ============================================================================
_driver = _database['driver'] if _database['driver'] in ('sqlite', 'mysql') else 'sqlite'

with open(STRUCTURE_PATH / f'{_driver}.json') as inputfile:
    statements = json_load(inputfile)

settings = {}


# ============================================================================
# >> CLASSES
# ============================================================================
class _DatabaseManager(object):
    @staticmethod
    def execute(key, arguments=(), callback=None, blocking=False, format_args=(), **keywords):
        return _queue.put(_Node(NodeType.QUERY, query=statements[key].format(*format_args), arguments=arguments, callback=callback, keywords=keywords, blocking=blocking))

    @staticmethod
    def executemany(key, arguments=(), callback=None, blocking=False, format_args=(), **keywords):
        return _queue.put(_Node(NodeType.QUERY_MANY, query=statements[key].format(*format_args), arguments=arguments, callback=callback, keywords=keywords, blocking=blocking))

    @staticmethod
    def callback(callback, **keywords):
        _queue.put(_Node(NodeType.CALLBACK, callback=callback, keywords=keywords))

    @staticmethod
    def connect():
        _thread.start()
        _repeat.start(0.1)

    @staticmethod
    def close():
        _queue.put(_Node(NodeType.CLOSE))
database_manager = _DatabaseManager()


# ============================================================================
# >> FUNCTIONS
# ============================================================================
def _query_settings(result):
    for setting, value in result.fetchall():
        settings[setting] = value

    if 'version' not in settings:
        settings['version'] = DatabaseVersion.CURRENT
        database_manager.execute('setting insert', arguments=('version', str(DatabaseVersion.CURRENT.value)))

        OnSettingsLoaded.manager.notify(settings)

        return

    version = settings[setting] = DatabaseVersion(int(settings['version']))

    if version < DatabaseVersion.CURRENT:
        # Change from using steamid to use accountid and set all bots accountid to NULL
        if version < DatabaseVersion.UPDATE1:
            for statement in [x for x in statements if x.startswith(f'database upgrade {DatabaseVersion.UPDATE1.value}.')]:
                database_manager.execute(statement)

        # Add bank level and rested xp
        if version < DatabaseVersion.UPDATE2:
            for statement in [x for x in statements if x.startswith(f'database upgrade {DatabaseVersion.UPDATE2.value}.')]:
                database_manager.execute(statement)

        database_manager.execute('setting update', arguments=(str(DatabaseVersion.CURRENT.value), ), format_args=('version', ))
        settings['version'] = DatabaseVersion.CURRENT

    OnSettingsLoaded.manager.notify(settings)


# ============================================================================
# >> INITIALIZATION
# ============================================================================
# TODO: Get MySQL working
if _driver == 'mysql':
    _queue.put(_Node(NodeType.CONNECT, query=lambda: mysql_connect(host=_database['host'], port=_database['port'], user=_database['user'], passwd=_database['password'], connect_timeout=_database['timeout'], charset='utf8mb4')))

    database_manager.execute('toggle warnings', format_args=(0, ))
    database_manager.execute('create database', format_args=(_database['database'], ))

    _queue.put(_Node(NodeType.USE, query=statements['use database'].format(_database['database'])))
else:
    _queue.put(_Node(NodeType.CONNECT, query=lambda: sqlite_connect(DATA_PATH.joinpath('players.sqlite'))))

for statement in ('create players', 'create races', 'create skills', 'create stats races', 'create stats items', 'create settings'):
    database_manager.execute(statement)

if _driver == 'mysql':
    database_manager.execute('toggle warnings', format_args=(1, ))

database_manager.execute('setting get', callback=_query_settings)
