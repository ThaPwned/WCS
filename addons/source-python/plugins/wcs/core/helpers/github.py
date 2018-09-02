# ../wcs/core/helpers/github.py

# ============================================================================
# >> IMPORTS
# ============================================================================
# Python Imports
#   Github
from github import Github
#   JSON
from json import dump
from json import load
#   Queue
from queue import Queue
#   Threading
from threading import Thread
#   Time
from time import mktime
from time import strptime
#   Warnings
from warnings import filterwarnings

# Source.Python Imports
#   Listeners
from listeners.tick import Repeat
#   Players
from players.helpers import index_from_userid

# WCS Imports
#   Constants
from ..constants import GITHUB_ACCESS_TOKEN
from ..constants import GithubStatus
from ..constants.info import info
from ..constants.paths import MODULE_PATH
from ..constants.paths import MODULE_PATH_ES
#   Helpers
from ..helpers.overwrites import SayText2
#   Listeners
from ..listeners import OnGithubFailed
from ..listeners import OnGithubRefresh
from ..listeners import OnGithubRefreshed
from ..listeners import OnGithubInstalled
from ..listeners import OnGithubUpdated
from ..listeners import OnGithubUninstalled
#   Menus
from ..menus import wcsadmin_github_options_menu
#   Translations
from ..translations import chat_strings


# ============================================================================
# >> ALL DECLARATION
# ============================================================================
__all__ = (
    'github_manager',
)


# ============================================================================
# >> GLOBAL VARIABLES
# ============================================================================
# Removes a ResourceWarning caused by the requests library
filterwarnings('ignore', category=ResourceWarning, message='unclosed.*<ssl.SSLSocket.*>')

_output = Queue()

_github_time_format = '%a, %d %b %Y %H:%M:%S GMT'

github_installing_failed_message = SayText2(chat_strings['github installing failed'])
github_installing_success_message = SayText2(chat_strings['github installing success'])
github_updating_failed_message = SayText2(chat_strings['github updating failed'])
github_updating_success_message = SayText2(chat_strings['github updating success'])
github_uninstalling_failed_message = SayText2(chat_strings['github uninstalling failed'])
github_uninstalling_success_message = SayText2(chat_strings['github uninstalling success'])


# ============================================================================
# >> CLASSES
# ============================================================================
class _GithubManager(dict):
    def __init__(self):
        super().__init__()

        self._counter = 0
        self._repeat = Repeat(self._tick)

        self._threads = []

        self['races'] = {}
        self['items'] = {}

    def _tick(self):
        if not _output.empty():
            self._counter -= 1

            if not self._counter:
                self._repeat.stop()

            items = _output.get_nowait()

            if items is not None:
                if isinstance(items, tuple):
                    items[0](*items[1:])
                else:
                    items()

    def _connect(self):
        _github = Github(GITHUB_ACCESS_TOKEN)
        _repo = _github.get_repo(f'{info.author.replace(" ", "")}/WCS-Contents')

        return _repo

    def _refresh(self):
        try:
            _repo = self._connect()
            modules = _repo.get_contents('')

            for module in [x.name for x in modules if x.name in self]:
                contents = _repo.get_contents(module)
                path = MODULE_PATH / module

                for content in contents:
                    wcs_install_path = path / content.name / '.wcs_install'

                    if wcs_install_path.isfile():
                        status = GithubStatus.INSTALLED

                        last_updated = wcs_install_path.mtime
                    else:
                        status = GithubStatus.UNINSTALLED

                        last_updated = None

                    self[module][content.name] = {'status':status, 'last_modified':mktime(strptime(content.last_modified, _github_time_format)), 'last_updated':last_updated}

            _output.put((OnGithubRefreshed.manager.notify, self['races'], self['items']))
        except:
            _output.put(None)
            raise

    def _install(self, module, name, userid):
        try:
            _repo = self._connect()

            self._download(_repo, f'{module}/{name}')

            with open(MODULE_PATH / module / name / '.wcs_install', 'w') as outputfile:
                outputfile.write('')

            self[module][name]['status'] = GithubStatus.INSTALLED

            _output.put((OnGithubInstalled.manager.notify, module, name, userid))
        except:
            _output.put((OnGithubFailed.manager.notify, module, name, userid, GithubStatus.INSTALLING))
            raise

    def _update(self, module, name, userid):
        try:
            _repo = self._connect()

            path = MODULE_PATH / module / name
            config_path = path / 'config.json'
            config_tmp_path = path / 'config.tmp.json'

            if config_path.isfile():
                config_path.rename(config_tmp_path)

            self._download(_repo, f'{module}/{name}')

            if config_tmp_path.isfile():
                with open(config_tmp_path) as inputfile:
                    old_data = load(inputfile)

                with open(config_path) as inputfile:
                    new_data = load(inputfile)

                config_tmp_path.remove()

                if not old_data == new_data:
                    modified = False

                    # TODO: Make this prettier...
                    if module == 'races':
                        for key in old_data:
                            if key == 'skills':
                                if 'skills' in new_data:
                                    for skill_name in old_data['skills']:
                                        if skill_name in new_data['skills']:
                                            for key, value in old_data['skills'][skill_name].items():
                                                if key == 'variables':
                                                    for variable, value in old_data['skills'][skill_name]['variables'].items():
                                                        new_value = new_data['skills'][skill_name]['variables'].get(variable)

                                                        if new_value is not None and not value == new_value:
                                                            new_data['skills'][skill_name]['variables'][variable] = value

                                                            modified = True
                                                else:
                                                    new_value = new_data['skills'][skill_name].get(key)

                                                    if new_value is not None and not value == new_value:
                                                        new_data['skills'][skill_name][key] = value

                                                        modified = True
                            # Don't modify the author
                            elif not key == 'author':
                                value = old_data[key]

                                if not value == new_data.get(key):
                                    new_data[key] = value

                                    modified = True
                    elif module == 'items':
                        for key, value in old_data.items():
                            if not value == new_data.get(key):
                                new_data[key] = value

                                modified = True
                    else:
                        raise ValueError(f'Invalid module name: "{module}"')

                    if modified:
                        with open(config_path, 'w') as outputfile:
                            dump(new_data, outputfile, indent=4)

            self[module][name]['status'] = GithubStatus.INSTALLED

            _output.put((OnGithubUpdated.manager.notify, module, name, userid))
        except:
            _output.put((OnGithubFailed.manager.notify, module, name, userid, GithubStatus.UPDATING))
            raise

    def _uninstall(self, module, name, userid):
        try:
            if (MODULE_PATH_ES / module / name).isdir():
                (MODULE_PATH_ES / module / name).rmtree()

            (MODULE_PATH / module / name).rmtree()

            self[module][name]['status'] = GithubStatus.UNINSTALLED

            _output.put((OnGithubUninstalled.manager.notify, module, name, userid))
        except:
            _output.put((OnGithubFailed.manager.notify, module, name, userid, GithubStatus.UNINSTALLING))
            raise

    def _download(self, repository, from_path):
        contents = repository.get_contents(from_path)
        name = from_path.split('/')[1]

        for content in contents:
            if content.name.endswith(f'{name}.py') or content.name.endswith(f'es_{name}.txt'):
                path = MODULE_PATH_ES / content.path
            else:
                path = MODULE_PATH / content.path

            if content.type == 'dir':
                if not path.isdir():
                    path.makedirs()

                self._download(repository, content.path)
            else:
                if not path.parent.isdir():
                    path.parent.makedirs()

                with open(path, 'wb') as outputfile:
                    outputfile.write(repository.get_contents(content.path).decoded_content)

    def refresh(self):
        if not self._counter:
            self._repeat.start(0.1)

        self._counter += 1

        OnGithubRefresh.manager.notify()

        thread = Thread(target=self._refresh)
        thread.start()

        self._threads.append(thread)

    def stop(self):
        for thread in self._threads:
            if thread.is_alive():
                thread.join()

        self._repeat.stop()

    def install(self, module, name, userid=None):
        assert self[module][name]['status'] is GithubStatus.UNINSTALLED

        if not self._counter:
            self._repeat.start(0.1)

        self._counter += 1

        self[module][name]['status'] = GithubStatus.INSTALLING

        thread = Thread(target=self._install, args=(module, name, userid))
        thread.start()

        self._threads.append(thread)

    def update(self, module, name, userid=None):
        assert self[module][name]['status'] is GithubStatus.INSTALLED

        if not self._counter:
            self._repeat.start(0.1)

        self._counter += 1

        self[module][name]['status'] = GithubStatus.UPDATING

        thread = Thread(target=self._update, args=(module, name, userid))
        thread.start()

        self._threads.append(thread)

    def uninstall(self, module, name, userid=None):
        assert self[module][name]['status'] is GithubStatus.INSTALLED

        if not self._counter:
            self._repeat.start(0.1)

        self._counter += 1

        self[module][name]['status'] = GithubStatus.UNINSTALLING

        thread = Thread(target=self._uninstall, args=(module, name, userid))
        thread.start()

        self._threads.append(thread)
github_manager = _GithubManager()


# ============================================================================
# >> LISTENERS
# ============================================================================
@OnGithubFailed
def on_github_failed(module, name, userid, task):
    if task is GithubStatus.INSTALLING:
        _send_message(github_installing_failed_message, userid, name=name)

        github_manager[module][name]['status'] = GithubStatus.UNINSTALLED
    elif task is GithubStatus.UPDATING:
        _send_message(github_updating_failed_message, userid, name=name)

        github_manager[module][name]['status'] = GithubStatus.INSTALLED
    elif task is GithubStatus.UNINSTALLING:
        _send_message(github_uninstalling_failed_message, userid, name=name)

        github_manager[module][name]['status'] = GithubStatus.INSTALLED

    _remove_dead_threads()


@OnGithubRefreshed
def on_github_refreshed(races, items):
    _remove_dead_threads()


@OnGithubInstalled
def on_github_installed(module, name, userid):
    _send_message(github_installing_success_message, userid, name=name)

    _remove_dead_threads()


@OnGithubUpdated
def on_github_updated(module, name, userid):
    _send_message(github_updating_success_message, userid, name=name)

    _remove_dead_threads()


@OnGithubUninstalled
def on_github_uninstalled(module, name, userid):
    _send_message(github_uninstalling_success_message, userid, name=name)

    _remove_dead_threads()


# ============================================================================
# >> HELPER FUNCTIONS
# ============================================================================
def _send_message(message, userid, **kwargs):
    if userid is not None:
        try:
            index = index_from_userid(userid)
        except ValueError:
            pass
        else:
            message.send(index, **kwargs)

    for index in wcsadmin_github_options_menu._player_pages:
        if wcsadmin_github_options_menu.is_active_menu(index):
            wcsadmin_github_options_menu._refresh(index)


def _remove_dead_threads():
    for thread in github_manager._threads.copy():
        if not thread.is_alive():
            github_manager._threads.remove(thread)
