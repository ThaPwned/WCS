# ../wcs/core/helpers/github.py

# ============================================================================
# >> IMPORTS
# ============================================================================
# Python Imports
#   Collections
from collections import OrderedDict
#   Disutils
from distutils.dir_util import copy_tree
#   Github
try:
    from github import Github
except ImportError:
    Github = None
#   IO
from io import BytesIO
#   JSON
from json import dump
from json import load
#   Path
from path import Path
#   Queue
from queue import Queue
#   Tempfile
from tempfile import TemporaryDirectory
#   Threading
from threading import Thread
#   Time
from time import mktime
from time import strptime
#   Urllib
from urllib.request import urlopen
#   Warnings
from warnings import filterwarnings
#   Zipfile
from zipfile import ZipFile

# Source.Python Imports
#   Constants
from paths import GAME_PATH
#   Listeners
from listeners.tick import Repeat
#   Players
from players.helpers import index_from_userid

# WCS Imports
#   Constants
from ..constants import GITHUB_ACCESS_TOKEN
from ..constants import GITHUB_PASSWORD
from ..constants import GITHUB_REPOSITORIES
from ..constants import GITHUB_USERNAME
from ..constants import GithubStatus
from ..constants.info import info
from ..constants.paths import DATA_PATH
from ..constants.paths import MODULE_PATH
from ..constants.paths import MODULE_PATH_ES
#   Helpers
from ..helpers.overwrites import SayText2
#   Listeners
from ..listeners import OnGithubCommitsRefresh
from ..listeners import OnGithubCommitsRefreshed
from ..listeners import OnGithubModuleFailed
from ..listeners import OnGithubModuleInstalled
from ..listeners import OnGithubModuleUpdated
from ..listeners import OnGithubModuleUninstalled
from ..listeners import OnGithubModulesRefresh
from ..listeners import OnGithubModulesRefreshed
from ..listeners import OnGithubNewVersionChecked
from ..listeners import OnGithubNewVersionInstalled
#   Menus
from ..menus import wcsadmin_github_races_options_menu
from ..menus import wcsadmin_github_items_options_menu
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
        self._checking_new_version = False
        self._installing_new_version = False
        self._refreshing_modules = False
        self._refreshing_commits = False

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

            for thread in self._threads.copy():
                if not thread.is_alive():
                    self._threads.remove(thread)

    def _connect(self):
        if GITHUB_ACCESS_TOKEN is not None:
            return Github(GITHUB_ACCESS_TOKEN, per_page=100)

        if GITHUB_USERNAME is None or GITHUB_PASSWORD is None:
            return Github(per_page=100)

        return Github(GITHUB_USERNAME, GITHUB_PASSWORD, per_page=100)

    def _check_new_version(self):
        try:
            _github = self._connect()

            _repo = _github.get_repo(f'{info.author.replace(" ", "")}/WCS')
            info_file = _repo.get_contents('addons/source-python/plugins/wcs/info.ini')

            for line in info_file.decoded_content.decode('utf8').split('\n'):
                if line.startswith('version'):
                    new_version = line.split()[2].strip()[1:-1]
                    break
            else:
                raise ValueError("Unable to locate 'version'.")

            if (DATA_PATH / 'metadata.wcs_install').isfile():
                with open(DATA_PATH / 'metadata.wcs_install') as inputfile:
                    sha = inputfile.read()
            else:
                sha = None
                commits = _repo.get_commits(path='addons/source-python/plugins/wcs/info.ini')

                for commit in commits:
                    for file_ in commit.files:
                        if file_.filename == 'addons/source-python/plugins/wcs/info.ini':
                            for line in file_.patch.splitlines():
                                if line.startswith('+version'):
                                    old_version = line.split()[2].strip()[1:-1]

                                    if old_version == new_version:
                                        sha = commit.sha

                                    break
                            break

                    if sha is not None:
                        break

            commit = _repo.get_commit(sha)
            response = _repo.get_commits(since=commit.commit.committer.date)

            if response.totalCount > 1:
                commits = []

                for response in list(response)[:-1]:
                    commits.append({'date':response.commit.author.date, 'author':response.commit.author.name, 'messages':response.commit.message})

                _output.put((OnGithubNewVersionChecked.manager.notify, new_version, commits))
            else:
                _output.put((OnGithubNewVersionChecked.manager.notify, None, []))
        except:
            _output.put(None)
            raise

    def _install_new_version(self):
        try:
            _github = self._connect()

            _repo = _github.get_repo(f'{info.author.replace(" ", "")}/WCS')

            if (DATA_PATH / 'update_blacklist.txt').isfile():
                with open(DATA_PATH / 'update_blacklist.txt') as inputfile:
                    blacklist = inputfile.read().splitlines()
            else:
                blacklist = []

            with urlopen(_repo.get_archive_link('zipball', 'master')) as response:
                with ZipFile(BytesIO(response.read()), 'r') as ref:
                    files = ref.namelist()
                    unique_name = files[0]

                    files.remove(unique_name)

                    with TemporaryDirectory() as tmpdir:
                        for member in files:
                            name = member.replace(unique_name, '')

                            if name in blacklist:
                                continue

                            ref.extract(member, path=tmpdir)

                        copy_tree(Path(tmpdir) / unique_name, GAME_PATH)

            commits = _repo.get_commits()
            sha = commits[0].sha

            with open(DATA_PATH / 'metadata.wcs_install', 'w') as outputfile:
                outputfile.write(sha)

            _output.put(OnGithubNewVersionInstalled.manager.notify)
        except:
            _output.put(None)
            raise

    def _refresh_modules(self):
        try:
            _github = self._connect()

            for repository in GITHUB_REPOSITORIES:
                _repo = _github.get_repo(repository)
                modules = _repo.get_contents('')

                modules_left = {}

                for module in [x.name for x in modules if x.name in self]:
                    contents = _repo.get_contents(module)
                    path = MODULE_PATH / module
                    modules_left[module] = []

                    for content in contents:
                        modules_left[module].append(content.name)

                        if module not in self or content.name not in self[module]:
                            wcs_install_path = path / content.name / '.wcs_install'

                            if wcs_install_path.isfile():
                                status = GithubStatus.INSTALLED

                                last_updated = wcs_install_path.mtime

                                with open(wcs_install_path) as inputfile:
                                    repository_installed = inputfile.read()
                            else:
                                status = GithubStatus.UNINSTALLED

                                last_updated = None
                                repository_installed = None

                            self[module][content.name] = {'status':status, 'last_updated':last_updated, 'repository':repository_installed, 'repositories':{repository:{}}}

                commits = _repo.get_commits()

                for commit in commits:
                    last_modified = commit.commit.committer.date.timestamp()

                    for file_ in commit.files:
                        tmp = file_.filename.split('/')
                        module = tmp[0]

                        if module in modules_left:
                            name = tmp[1]

                            if name in modules_left[module]:
                                self[module][name]['repositories'][repository]['last_modified'] = last_modified
                                modules_left[module].remove(name)

                                if not modules_left[module]:
                                    del modules_left[module]

                    if not modules_left:
                        break

            _output.put((OnGithubModulesRefreshed.manager.notify, self['races'], self['items']))
        except:
            _output.put(None)
            raise

    def _install_module(self, repository, module, name, userid):
        try:
            _github = self._connect()
            _repo = _github.get_repo(repository)

            self._download_module(_repo, f'{module}/{name}')

            _path = MODULE_PATH / module / name / '.wcs_install'

            with open(_path, 'w') as outputfile:
                outputfile.write(repository)

            self[module][name]['status'] = GithubStatus.INSTALLED
            self[module][name]['last_updated'] = _path.mtime
            self[module][name]['repository'] = repository

            _output.put((OnGithubModuleInstalled.manager.notify, repository, module, name, userid))
        except:
            _output.put((OnGithubModuleFailed.manager.notify, repository, module, name, userid, GithubStatus.INSTALLING))
            raise

    def _update_module(self, repository, module, name, userid):
        try:
            _github = self._connect()
            _repo = _github.get_repo(repository)

            path = MODULE_PATH / module / name
            config_path = path / 'config.json'
            config_tmp_path = path / 'config.tmp.json'

            if config_path.isfile():
                config_path.rename(config_tmp_path)

            self._download_module(_repo, f'{module}/{name}')

            if config_tmp_path.isfile():
                with open(config_tmp_path) as inputfile:
                    old_data = load(inputfile)

                with open(config_path) as inputfile:
                    new_data = load(inputfile)

                config_tmp_path.remove()

                if not old_data == new_data:
                    def merge(container, original, updated):
                        for key in updated:
                            if key in original:
                                if isinstance(original[key], dict) and isinstance(updated[key], dict):
                                    container[key] = merge(OrderedDict(), original[key], updated[key])
                                else:
                                    container[key] = original[key]
                            else:
                                container[key] = updated[key]

                        return container

                    container = merge(OrderedDict(), old_data, new_data)

                    if module == 'races':
                        # Don't modify the author
                        container['author'] = new_data['author']

                    with open(config_path, 'w') as outputfile:
                        dump(container, outputfile, indent=4)

            _path = MODULE_PATH / module / name / '.wcs_install'

            # Update the installation file, so we know it's been updated
            _path.utime(None)

            self[module][name]['status'] = GithubStatus.INSTALLED
            self[module][name]['last_updated'] = _path.mtime

            _output.put((OnGithubModuleUpdated.manager.notify, repository, module, name, userid))
        except:
            _output.put((OnGithubModuleFailed.manager.notify, repository, module, name, userid, GithubStatus.UPDATING))
            raise

    def _uninstall_module(self, repository, module, name, userid):
        try:
            if (MODULE_PATH_ES / module / name).isdir():
                (MODULE_PATH_ES / module / name).rmtree()

            (MODULE_PATH / module / name).rmtree()

            self[module][name]['status'] = GithubStatus.UNINSTALLED
            self[module][name]['last_updated'] = None
            self[module][name]['repository'] = None

            _output.put((OnGithubModuleUninstalled.manager.notify, repository, module, name, userid))
        except:
            _output.put((OnGithubModuleFailed.manager.notify, repository, module, name, userid, GithubStatus.UNINSTALLING))
            raise

    def _download_module(self, repository, from_path):
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

                self._download_module(repository, content.path)
            else:
                if not path.parent.isdir():
                    path.parent.makedirs()

                with open(path, 'wb') as outputfile:
                    outputfile.write(repository.get_contents(content.path).decoded_content)

    def _refresh_commits(self):
        try:
            _github = self._connect()
            _repo = _github.get_repo(f'{info.author.replace(" ", "")}/WCS')

            commits = []

            for response in _repo.get_commits():
                commits.append({'date':response.commit.author.date, 'author':response.commit.author.name, 'messages':response.commit.message})

            _output.put((OnGithubCommitsRefreshed.manager.notify, commits))
        except:
            _output.put(None)
            raise

    if Github is None:
        def stop(self):
            pass

        def check_new_version(self):
            pass

        def install_new_version(self):
            pass

        def refresh_modules(self):
            pass

        def install_module(self, repository, module, name, userid=None):
            pass

        def update_module(self, repository, module, name, userid=None):
            pass

        def uninstall_module(self, repository, module, name, userid=None):
            pass

        def refresh_commits(self):
            pass
    else:
        def stop(self):
            for thread in self._threads:
                if thread.is_alive():
                    thread.join()

            self._repeat.stop()

        def check_new_version(self):
            if self._checking_new_version:
                return

            self._checking_new_version = True

            if not self._counter:
                self._repeat.start(0.1)

            self._counter += 1

            thread = Thread(target=self._check_new_version, name='wcs.checking')
            thread.start()

            self._threads.append(thread)

        def install_new_version(self):
            if self._installing_new_version:
                return

            self._installing_new_version = True

            if not self._counter:
                self._repeat.start(0.1)

            self._counter += 1

            thread = Thread(target=self._install_new_version, name='wcs.installing')
            thread.start()

            self._threads.append(thread)

        def refresh_modules(self):
            if self._refreshing_modules:
                return

            self._refreshing_modules = True

            if not self._counter:
                self._repeat.start(0.1)

            self._counter += 1

            OnGithubModulesRefresh.manager.notify()

            thread = Thread(target=self._refresh_modules, name='wcs.refresh.modules')
            thread.start()

            self._threads.append(thread)

        def install_module(self, repository, module, name, userid=None):
            assert self[module][name]['status'] is GithubStatus.UNINSTALLED

            if not self._counter:
                self._repeat.start(0.1)

            self._counter += 1

            self[module][name]['status'] = GithubStatus.INSTALLING

            thread = Thread(target=self._install_module, name=f'wcs.install.{module}.{name}', args=(repository, module, name, userid))
            thread.start()

            self._threads.append(thread)

        def update_module(self, module, name, userid=None):
            assert self[module][name]['status'] is GithubStatus.INSTALLED

            if not self._counter:
                self._repeat.start(0.1)

            self._counter += 1

            self[module][name]['status'] = GithubStatus.UPDATING

            thread = Thread(target=self._update_module, name=f'wcs.update.{module}.{name}', args=(self[module][name]['repository'], module, name, userid))
            thread.start()

            self._threads.append(thread)

        def uninstall_module(self, module, name, userid=None):
            assert self[module][name]['status'] is GithubStatus.INSTALLED

            if not self._counter:
                self._repeat.start(0.1)

            self._counter += 1

            self[module][name]['status'] = GithubStatus.UNINSTALLING

            thread = Thread(target=self._uninstall_module, name=f'wcs.uninstall.{module}.{name}', args=(self[module][name]['repository'], module, name, userid))
            thread.start()

            self._threads.append(thread)

        def refresh_commits(self):
            if self._refreshing_commits:
                return

            self._refreshing_commits = True

            if not self._counter:
                self._repeat.start(0.1)

            self._counter += 1

            OnGithubCommitsRefresh.manager.notify()

            thread = Thread(target=self._refresh_commits, name='wcs.refresh.commits')
            thread.start()

            self._threads.append(thread)
github_manager = _GithubManager()


# ============================================================================
# >> LISTENERS
# ============================================================================
@OnGithubCommitsRefreshed
def on_github_commits_refreshed(commits):
    github_manager._refreshing_commits = False


@OnGithubModuleFailed
def on_github_failed(repository, module, name, userid, task):
    if task is GithubStatus.INSTALLING:
        _send_message(module, github_installing_failed_message, userid, name=name)

        github_manager[module][name]['status'] = GithubStatus.UNINSTALLED
    elif task is GithubStatus.UPDATING:
        _send_message(module, github_updating_failed_message, userid, name=name)

        github_manager[module][name]['status'] = GithubStatus.INSTALLED
    elif task is GithubStatus.UNINSTALLING:
        _send_message(module, github_uninstalling_failed_message, userid, name=name)

        github_manager[module][name]['status'] = GithubStatus.INSTALLED


@OnGithubNewVersionChecked
def on_github_new_version_checked(version, commits):
    github_manager._checking_new_version = False


@OnGithubNewVersionInstalled
def on_github_new_version_installed():
    github_manager._installing_new_version = False


@OnGithubModulesRefreshed
def on_github_modules_refreshed(races, items):
    github_manager._refreshing_modules = False


@OnGithubModuleInstalled
def on_github_module_installed(repository, module, name, userid):
    _send_message(module, github_installing_success_message, userid, name=name)


@OnGithubModuleUpdated
def on_github_module_updated(repository, module, name, userid):
    _send_message(module, github_updating_success_message, userid, name=name)


@OnGithubModuleUninstalled
def on_github_module_uninstalled(repository, module, name, userid):
    _send_message(module, github_uninstalling_success_message, userid, name=name)


# ============================================================================
# >> HELPER FUNCTIONS
# ============================================================================
def _send_message(module, message, userid, **kwargs):
    if userid is not None:
        try:
            index = index_from_userid(userid)
        except ValueError:
            pass
        else:
            message.send(index, **kwargs)

    menu = wcsadmin_github_races_options_menu if module == 'races' else wcsadmin_github_items_options_menu

    for index in menu._player_pages:
        if menu.is_active_menu(index):
            menu._refresh(index)
