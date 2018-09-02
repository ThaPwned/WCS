# ../wcs/core/database/manager.py

# ============================================================================
# >> IMPORTS
# ============================================================================
# Python Imports
#   JSON
from json import dump as json_dump
from json import load as json_load
#   PyMySQL
try:
    from pymysql import connect as mysql_connect
except ImportError:
    mysql_connect = None
#   SQLite3
from sqlite3 import connect as sqlite_connect

# WCS Imports
#   Constants
from ..constants.paths import CFG_PATH
from ..constants.paths import DATA_PATH
from ..constants.paths import STRUCTURE_PATH
#   Database
from .thread import _queue
from .thread import _thread
from .thread import _repeat


# ============================================================================
# >> ALL DECLARATION
# ============================================================================
__all__ = (
    'database_manager',
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
# >> CLASSES
# ============================================================================
class _DatabaseManager(object):
    def __init__(self):
        self._unloading = False

    def _put(self, query, arguments, callback, many, keywords):
        _queue.put((query, arguments or tuple(), callback, many, keywords))

    def execute(self, key, arguments=None, callback=None, format_args=(), **keywords):
        self._put(statements[key].format(*format_args), arguments, callback, False, keywords)

    def executemany(self, key, arguments=None, callback=None, format_args=(), **keywords):
        self._put(statements[key].format(*format_args), arguments, callback, True, keywords)

    def callback(self, callback, **keywords):
        self._put(None, None, callback, False, keywords)

    def connect(self):
        _thread.start()
        _repeat.start(0.1)

    def close(self):
        self._put(None, None, None, False, None)
database_manager = _DatabaseManager()


# TODO: Get MySQL working
# if _database['driver'].lower() == 'mysql':
#     if mysql_connect is None:
#         raise NotImplementedError('MySQL is not installed.')

#     with open(STRUCTURE_PATH / 'mysql.json') as inputfile:
#         statements = json_load(inputfile)

#     _queue.put(lambda: mysql_connect(host=_database['host'], port=_database['port'], user=_database['user'], passwd=_database['password'], connect_timeout=_database['timeout']))

#     def _execute(result):
#         _thread._use_database = statements['use database'].format(_database['database'])

#     database_manager.execute('toggle warnings', format_args=(0, ))
#     database_manager.execute('create database', format_args=(_database['database'], ))
#     database_manager.execute('use database', callback=_execute, format_args=(_database['database'], ))
# else:
with open(STRUCTURE_PATH / 'sqlite.json') as inputfile:
    statements = json_load(inputfile)

_queue.put(lambda: sqlite_connect(DATA_PATH.joinpath('players.sqlite')))

for statement in ('create players', 'create races', 'create skills', 'create stats races', 'create stats items'):
    database_manager.execute(statement)

# if _database['driver'].lower() == 'mysql':
#     database_manager.execute('toggle warnings', format_args=(1, ))
