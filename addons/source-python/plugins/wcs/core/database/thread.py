# ../wcs/core/database/thread.py

# ============================================================================
# >> IMPORTS
# ============================================================================
# Python Imports
#   PyMySQL
from pymysql.err import InterfaceError
from pymysql.err import OperationalError
#   Queue
from queue import PriorityQueue
from queue import Queue
#   Sys
from sys import exc_info
#   Threading
from threading import Event
from threading import Thread
#   Time
from time import sleep

# Source.Python Imports
#   Hooks
from hooks.exceptions import except_hooks
#   Listeners
from listeners.tick import Repeat
from listeners.tick import RepeatStatus

# WCS Imports
#   Constants
from ..constants import NodeType


# ============================================================================
# >> CLASSES
# ============================================================================
class _PriorityQueue(PriorityQueue):
    _entry = 0

    def put(self, node):
        node._entry = self._entry

        self._entry += 1

        super().put(node)

        if node._blocking:
            assert _repeat.status == RepeatStatus.RUNNING

            node.priority = 2

            node._executed.wait()

            exception = node._result.exception

            if exception:
                raise exception[1].with_traceback(exception[2])

            return node._result


class _Result(object):
    def __init__(self, query=None, data=None, args=None, exception=None):
        self._query = query
        self._data = data
        self._args = args
        self._exception = exception

        self._curindex = 0

    def __getitem__(self, name):
        return self._args[name]

    def fetchone(self):
        if len(self._data) <= self._curindex:
            return None

        data = self._data[self._curindex]
        self._curindex += 1

        return data

    def fetchall(self):
        data = self._data[self._curindex:]
        self._curindex = len(self._data)

        return data

    @property
    def query(self):
        return self._query

    @property
    def exception(self):
        return self._exception


class _Node(object):
    def __init__(self, type_, query=None, arguments=None, callback=None, keywords=None, priority=0, blocking=False):
        self.type = type_
        self.query = query
        self.arguments = arguments
        self.callback = callback
        self.keywords = keywords
        self.priority = priority
        self._entry = None

        self._blocking = blocking

        if blocking:
            self._executed = Event()
            self._result = None

    def __lt__(self, other):
        return other.priority < self.priority or other._entry > self._entry


class _Thread(Thread):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._use_database = None
        self._unloading = Event()
        self._counter = 0
        self._reconnect_delay = 10

    def run(self):
        self.con = None
        self.cur = None

        self.connector = _queue.get().query

        while True:
            node = _queue.get()

            if node.type in (NodeType.QUERY, NodeType.QUERY_MANY):
                if self.con is None or self.cur is None:
                    if not self.connect():
                        node.priority = 1

                        _queue.put(node)

                        sleep(self._reconnect_delay)

                        continue

                result = _Result(args=node.keywords, query=node.query)

                try:
                    if node.type is NodeType.QUERY:
                        self.cur.execute(node.query, node.arguments)
                    else:
                        self.cur.executemany(node.query, node.arguments)
                except (InterfaceError, OperationalError) as e:
                    if node._blocking:
                        result._exception = exc_info()

                        node._result = result
                        node._executed.set()
                    else:
                        node.priority = 1

                        _queue.put(node)

                        if isinstance(e, InterfaceError):
                            self.close()

                            if not self.connect():
                                sleep(self._reconnect_delay)
                except:
                    result._exception = exc_info()

                    if node._blocking:
                        node._result = result
                        node._executed.set()
                    else:
                        node.priority = 1

                        _queue.put(node)

                        _output.put((None, result))
                else:
                    if node.callback is not None:
                        result._data = self.cur.fetchall()

                        _output.put((node.callback, result))
                    elif node._blocking:
                        result._data = self.cur.fetchall()

                        node._result = result
                        node._executed.set()
            elif node.type is NodeType.CALLBACK:
                _output.put((node.callback, _Result(args=node.keywords)))
            elif node.type is NodeType.CONNECT:
                if not self.connect():
                    sleep(self._reconnect_delay)
            elif node.type is NodeType.USE:
                self._use_database = node.query

                if self.cur is not None:
                    self.cur.execute(self._use_database)
            elif node.type is NodeType.CLOSE:
                break

            if _queue.empty():
                self.close()

        self.close()

        _output.put((True, True))

    def _tick(self):
        for _ in range(16):
            if _output.empty():
                break

            callback, result = _output.get_nowait()

            if callback is True and result is True:
                _repeat.stop()
            else:
                if callback is not None:
                    try:
                        callback(result)
                    except:
                        except_hooks.print_exception()

                if result.exception:
                    except_hooks.print_exception(*result.exception)

    def connect(self):
        try:
            self.con = self.connector()
            self.cur = self.con.cursor()

            if self._use_database is not None:
                self.cur.execute(self._use_database)
        except OperationalError:
            if self.unloading:
                if self._counter >= 4:
                    _queue.put(_Node(NodeType.CLOSE, priority=4))

                    return False

                self._counter += 1

            _queue.put(_Node(NodeType.CONNECT, priority=3))

            return False
        except:
            _output.put((None, _Result(exception=exc_info())))
            _output.put((True, True))

            raise
        else:
            self._counter = 0

        return True

    def close(self):
        if self.cur is not None:
            self.cur.close()

            self.cur = None

        if self.con is not None:
            try:
                self.con.commit()
            except InterfaceError:
                pass

            self.con.close()

            self.con = None

    @property
    def unloading(self):
        return self._unloading.is_set()

    @unloading.setter
    def unloading(self, value):
        getattr(self._unloading, 'set' if value else 'clear')()


class Repeat2(Repeat):
    def _unload_instance(self):
        # I need to be sure the repeat does NOT stop at unload
        pass


# ============================================================================
# >> GLOBAL VARIABLES
# ============================================================================
_queue = _PriorityQueue()
_output = Queue()
_thread = _Thread(name='wcs.database')
_repeat = Repeat2(_thread._tick)
