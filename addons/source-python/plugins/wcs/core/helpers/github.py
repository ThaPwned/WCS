# ../wcs/core/helpers/github.py

# ============================================================================
# >> IMPORTS
# ============================================================================
# Python Imports
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
from ..listeners import OnDownloadBegin
from ..listeners import OnDownloadComplete
from ..listeners import OnGithubFailed
from ..listeners import OnGithubRefresh
from ..listeners import OnGithubRefreshed
from ..listeners import OnGithubInstalled
from ..listeners import OnGithubUpdated
from ..listeners import OnGithubUninstalled
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
        self._downloading = False
        self._refreshing = False

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
        if GITHUB_ACCESS_TOKEN is not None:
            return Github(GITHUB_ACCESS_TOKEN)

        if GITHUB_USERNAME is None or GITHUB_PASSWORD is None:
            return Github()

        return Github(GITHUB_USERNAME, GITHUB_PASSWORD)

    def _download_update(self):
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

            new_version_epoch = new_version.split('-')
            new_version_epoch = mktime(strptime(new_version_epoch[0], r'%Y.%m.%d')) + int(new_version_epoch[1])

            local_version_epoch = info.version.split('-')
            local_version_epoch = mktime(strptime(local_version_epoch[0], r'%Y.%m.%d')) + int(local_version_epoch[1])

            if new_version_epoch > local_version_epoch:
                if (DATA_PATH / 'update_blacklist.txt').isfile():
                    with open(DATA_PATH / 'update_blacklist.txt') as f:
                        blacklist = f.read().splitlines()
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

                _output.put((OnDownloadComplete.manager.notify, new_version))
            else:
                _output.put((OnDownloadComplete.manager.notify, None))
        except:
            _output.put(None)
            raise

    def _refresh(self):
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

            _output.put((OnGithubRefreshed.manager.notify, self['races'], self['items']))
        except:
            _output.put(None)
            raise

    def _install(self, repository, module, name, userid):
        try:
            _github = self._connect()
            _repo = _github.get_repo(repository)

            self._download(_repo, f'{module}/{name}')

            _path = MODULE_PATH / module / name / '.wcs_install'

            with open(_path, 'w') as outputfile:
                outputfile.write(repository)

            self[module][name]['status'] = GithubStatus.INSTALLED
            self[module][name]['last_updated'] = _path.mtime
            self[module][name]['repository'] = repository

            _output.put((OnGithubInstalled.manager.notify, repository, module, name, userid))
        except:
            _output.put((OnGithubFailed.manager.notify, repository, module, name, userid, GithubStatus.INSTALLING))
            raise

    def _update(self, repository, module, name, userid):
        try:
            _github = self._connect()
            _repo = _github.get_repo(repository)

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

            _path = MODULE_PATH / module / name / '.wcs_install'

            # Update the installation file, so we know it's been updated
            _path.utime(None)

            self[module][name]['status'] = GithubStatus.INSTALLED
            self[module][name]['last_updated'] = _path.mtime

            _output.put((OnGithubUpdated.manager.notify, repository, module, name, userid))
        except:
            _output.put((OnGithubFailed.manager.notify, repository, module, name, userid, GithubStatus.UPDATING))
            raise

    def _uninstall(self, repository, module, name, userid):
        try:
            if (MODULE_PATH_ES / module / name).isdir():
                (MODULE_PATH_ES / module / name).rmtree()

            (MODULE_PATH / module / name).rmtree()

            self[module][name]['status'] = GithubStatus.UNINSTALLED
            self[module][name]['last_updated'] = None
            self[module][name]['repository'] = None

            _output.put((OnGithubUninstalled.manager.notify, repository, module, name, userid))
        except:
            _output.put((OnGithubFailed.manager.notify, repository, module, name, userid, GithubStatus.UNINSTALLING))
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

    if Github is None:
        def download_update(self):
            pass

        def refresh(self):
            pass

        def stop(self):
            pass

        def install(self, repository, module, name, userid=None):
            pass

        def update(self, repository, module, name, userid=None):
            pass

        def uninstall(self, repository, module, name, userid=None):
            pass
    else:
        def download_update(self):
            if self._downloading:
                return

            self._downloading = True

            if not self._counter:
                self._repeat.start(0.1)

            self._counter += 1

            OnDownloadBegin.manager.notify()

            thread = Thread(target=self._download_update)
            thread.start()

            self._threads.append(thread)

        def refresh(self):
            if self._refreshing:
                return

            self._refreshing = True

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

        def install(self, repository, module, name, userid=None):
            assert self[module][name]['status'] is GithubStatus.UNINSTALLED

            if not self._counter:
                self._repeat.start(0.1)

            self._counter += 1

            self[module][name]['status'] = GithubStatus.INSTALLING

            thread = Thread(target=self._install, args=(repository, module, name, userid))
            thread.start()

            self._threads.append(thread)

        def update(self, module, name, userid=None):
            assert self[module][name]['status'] is GithubStatus.INSTALLED

            if not self._counter:
                self._repeat.start(0.1)

            self._counter += 1

            self[module][name]['status'] = GithubStatus.UPDATING

            thread = Thread(target=self._update, args=(self[module][name]['repository'], module, name, userid))
            thread.start()

            self._threads.append(thread)

        def uninstall(self, module, name, userid=None):
            assert self[module][name]['status'] is GithubStatus.INSTALLED

            if not self._counter:
                self._repeat.start(0.1)

            self._counter += 1

            self[module][name]['status'] = GithubStatus.UNINSTALLING

            thread = Thread(target=self._uninstall, args=(self[module][name]['repository'], module, name, userid))
            thread.start()

            self._threads.append(thread)
github_manager = _GithubManager()


# ============================================================================
# >> LISTENERS
# ============================================================================
@OnGithubFailed
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

    _remove_dead_threads()


@OnDownloadComplete
def on_download_complete(version):
    github_manager._downloading = False

    _remove_dead_threads()


@OnGithubRefreshed
def on_github_refreshed(races, items):
    github_manager._refreshing = False

    _remove_dead_threads()


@OnGithubInstalled
def on_github_installed(repository, module, name, userid):
    _send_message(module, github_installing_success_message, userid, name=name)

    _remove_dead_threads()


@OnGithubUpdated
def on_github_updated(repository, module, name, userid):
    _send_message(module, github_updating_success_message, userid, name=name)

    _remove_dead_threads()


@OnGithubUninstalled
def on_github_uninstalled(repository, module, name, userid):
    _send_message(module, github_uninstalling_success_message, userid, name=name)

    _remove_dead_threads()


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


def _remove_dead_threads():
    for thread in github_manager._threads.copy():
        if not thread.is_alive():
            github_manager._threads.remove(thread)
