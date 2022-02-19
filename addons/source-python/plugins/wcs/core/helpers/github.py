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
from github import Github
from github import UnknownObjectException
#   IO
from io import BytesIO
#   JSON
from json import JSONDecodeError
from json import dump
from json import load
#   Path
from path import Path
#   Queue
from queue import Queue
#   Re
from re import findall
#   Tempfile
from tempfile import TemporaryDirectory
#   Threading
from threading import Thread
#   Time
from time import time
#   Urllib
from urllib.request import urlopen
#   Warnings
from warnings import filterwarnings
#   Zipfile
from zipfile import ZipFile

# Source.Python Imports
#   Constants
from paths import GAME_PATH
#   Hooks
from hooks.exceptions import except_hooks
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
from ..constants import GithubModuleStatus
from ..constants.info import info
from ..constants.paths import DATA_PATH
from ..constants.paths import MODULE_PATH
from ..constants.paths import MODULE_PATH_ES
from ..constants.paths import PLUGIN_PATH
#   Helpers
from ..helpers.overwrites import SayText2
#   Listeners
from ..listeners import OnGithubCommitsRefresh
from ..listeners import OnGithubCommitsRefreshed
from ..listeners import OnGithubModuleFailed
from ..listeners import OnGithubModuleInstalled
from ..listeners import OnGithubModuleUpdated
from ..listeners import OnGithubModuleUninstalled
from ..listeners import OnGithubRaceModulesRefresh
from ..listeners import OnGithubRaceModulesRefreshed
from ..listeners import OnGithubRaceModuleUpdate
from ..listeners import OnGithubItemModulesRefresh
from ..listeners import OnGithubItemModulesRefreshed
from ..listeners import OnGithubItemModuleUpdate
from ..listeners import OnGithubNewVersionChecked
from ..listeners import OnGithubNewVersionInstalled
from ..listeners import OnGithubNewVersionUpdating
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
# >> CONSTANTS
# ============================================================================
RE_PULL_REQUEST = r'\#(\d+)'


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
        self._refreshing_race_modules = False
        self._refreshing_item_modules = False
        self._refreshing_commits = False

        self._threads = []

        self['races'] = {}
        self['items'] = {}

    def _tick(self):
        if not _output.empty():
            value = _output.get_nowait()

            decrease = value[0]
            listener = value[1]

            if listener is not None:
                try:
                    listener(*value[2:])
                except:
                    except_hooks.print_exception()

            if decrease:
                self._counter -= 1

                if not self._counter:
                    self._repeat.stop()

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
            github = self._connect()
            repo = github.get_repo(f'{info.author.replace(" ", "")}/WCS')

            if (DATA_PATH / 'metadata.wcs_install').isfile():
                valid_version = True

                # Update the metadata file to use JSON instead of just holding the SHA value
                try:
                    with open(DATA_PATH / 'metadata.wcs_install') as inputfile:
                        sha = load(inputfile)['sha']
                except JSONDecodeError:
                    with open(DATA_PATH / 'metadata.wcs_install') as inputfile:
                        sha = inputfile.read()

                    with open(DATA_PATH / 'metadata.wcs_install', 'w') as outputfile:
                        dump({'sha':sha}, outputfile, indent=4)
            else:
                if (PLUGIN_PATH / 'info.ini').isfile():
                    with open(PLUGIN_PATH / 'info.ini') as inputfile:
                        for line in inputfile.read().splitlines():
                            if line.startswith('version'):
                                current_version = line.split()[2].strip()[1:-1]
                                break
                        else:
                            current_version = None
                else:
                    current_version = None

                sha = None
                commits = repo.get_commits(path='addons/source-python/plugins/wcs/info.ini')

                if current_version is None:
                    sha = list(commits)[-1].sha
                else:
                    for i, commit in enumerate(commits):
                        for file_ in commit.files:
                            if file_.filename == 'addons/source-python/plugins/wcs/info.ini':
                                for line in file_.patch.splitlines():
                                    if line.startswith('+version'):
                                        old_version = line.split()[2].strip()[1:-1]

                                        if old_version == current_version:
                                            sha = commit.sha

                                        break

                                break

                        if sha is not None:
                            break

                        # Couldn't find the correct version after 10 tries, so just set the sha code to the first ever commit
                        # This is done to avoid spending too much time here since it's not realy important
                        if i == 9:
                            sha = '8892447b0d00d65158c6ad908fe0e06289394211'
                            break
                    else:
                        # Couldn't find the correct version, so just set the sha code to the first ever commit
                        sha = '8892447b0d00d65158c6ad908fe0e06289394211'

                valid_version = current_version is not None

            commit = repo.get_commit(sha)
            response = repo.get_commits(since=commit.commit.committer.date)

            if response.totalCount > 1:
                commits = []
                pull_requests = set()

                for response in (list(response)[:-1] if valid_version else list(response)):
                    commits.append({'date':response.commit.author.date, 'author':response.commit.author.name, 'messages':response.commit.message})

                    pr_numbers = findall(RE_PULL_REQUEST, response.commit.message)

                    pull_requests.update(pr_numbers)

                while pull_requests:
                    pr_number = int(pull_requests.pop())

                    pr = repo.get_pull(pr_number)

                    for response in reversed(list(pr.get_commits())):
                        # TODO: For some reason 'response.commit.author.date' return the wrong value for certain commits (test: set sha in metadata.wcs_install to bff42a5d0546c95d87f053c94284cb9afa133007)
                        commits.append({'date':response.commit.author.date, 'author':response.commit.author.name, 'messages':response.commit.message})

                        pr_numbers = findall(RE_PULL_REQUEST, response.commit.message)

                        pull_requests.update(pr_numbers)

                # Just in case something goes wrong when retrieving the version
                try:
                    info_file = repo.get_contents('addons/source-python/plugins/wcs/info.ini')

                    for line in info_file.decoded_content.decode('utf8').split('\n'):
                        if line.startswith('version'):
                            new_version = line.split()[2].strip()[1:-1]
                            break
                    else:
                        raise ValueError("Unable to locate 'version'.")
                except:
                    except_hooks.print_exception()

                    new_version = f'Unknown (SHA: {sha})'

                _output.put((True, OnGithubNewVersionChecked.manager.notify, new_version, commits))
            else:
                _output.put((True, OnGithubNewVersionChecked.manager.notify, None, []))
        except:
            _output.put((True, None))
            raise

    def _install_new_version(self):
        try:
            _output.put((False, OnGithubNewVersionUpdating.manager.notify, GithubStatus.PREPARING))

            github = self._connect()
            repo = github.get_repo(f'{info.author.replace(" ", "")}/WCS')

            if (DATA_PATH / 'update_blacklist.txt').isfile():
                with open(DATA_PATH / 'update_blacklist.txt') as inputfile:
                    blacklist = inputfile.read().splitlines()
            else:
                blacklist = []

            if (DATA_PATH / 'metadata.wcs_install').isfile():
                try:
                    with open(DATA_PATH / 'metadata.wcs_install') as inputfile:
                        metadata = load(inputfile)
                except JSONDecodeError:
                    with open(DATA_PATH / 'metadata.wcs_install') as inputfile:
                        sha = inputfile.read()

                    metadata = {'sha':sha}
            else:
                metadata = {}

            _output.put((False, OnGithubNewVersionUpdating.manager.notify, GithubStatus.CONNECTING))

            updated_files = set()

            most_recent_commit_sha = repo.get_branch('master').commit.sha

            if metadata.get('sha') is not None:
                _output.put((False, OnGithubNewVersionUpdating.manager.notify, GithubStatus.OPTIMIZING, 0, len(updated_files), 0, 0))
                pull_requests = set()

                commit = repo.get_commit(metadata['sha'])

                commits = list(repo.get_commits(since=commit.commit.committer.date))

                for i, response in enumerate(commits[:-1], 1):
                    updated_files.update([x.filename for x in response.files])

                    pr_numbers = findall(RE_PULL_REQUEST, response.commit.message)

                    pull_requests.update(pr_numbers)

                    _output.put((False, OnGithubNewVersionUpdating.manager.notify, GithubStatus.OPTIMIZING, 0, len(updated_files), i, len(commits) - 1))

                _output.put((False, OnGithubNewVersionUpdating.manager.notify, GithubStatus.OPTIMIZING, 1, len(updated_files), 0, 0))

                while pull_requests:
                    pr_number = int(pull_requests.pop())

                    pr = repo.get_pull(pr_number)

                    commits = list(pr.get_commits())

                    for i, response in enumerate(commits, 1):
                        updated_files.update([x.filename for x in response.files])

                        pr_numbers = findall(RE_PULL_REQUEST, response.commit.message)

                        pull_requests.update(pr_numbers)

                        _output.put((False, OnGithubNewVersionUpdating.manager.notify, GithubStatus.OPTIMIZING, 1, len(updated_files), i, len(commits)))

                _output.put((False, OnGithubNewVersionUpdating.manager.notify, GithubStatus.CONNECTING))

            with urlopen(repo.get_archive_link('zipball', 'master')) as response:
                size = response.headers['Content-Length'] or None

                if size is not None:
                    size = int(size)

                _output.put((False, OnGithubNewVersionUpdating.manager.notify, GithubStatus.DOWNLOADING, 0, size))

                with BytesIO() as data:
                    length = 0
                    next_update = time()

                    while True:
                        chunk = response.read(2 ** 16)

                        if not chunk:
                            break

                        length += len(chunk)

                        data.write(chunk)

                        now = time()

                        if now >= next_update:
                            _output.put((False, OnGithubNewVersionUpdating.manager.notify, GithubStatus.DOWNLOADING, length, size))

                            next_update = now + 0.125

                    with ZipFile(data, 'r') as ref:
                        _output.put((False, OnGithubNewVersionUpdating.manager.notify, GithubStatus.UNZIPPING))

                        files = ref.namelist()
                        unique_name = files[0]

                        files.remove(unique_name)

                        files_count = len(updated_files or files)

                        _output.put((False, OnGithubNewVersionUpdating.manager.notify, GithubStatus.EXTRACTING, 0, files_count))

                        with TemporaryDirectory() as tmpdir:
                            next_update = time()

                            for i, member in enumerate(updated_files or files, 1):
                                now = time()

                                if now >= next_update:
                                    _output.put((False, OnGithubNewVersionUpdating.manager.notify, GithubStatus.EXTRACTING, i, files_count))

                                    next_update = now + 0.125

                                name = member.replace(unique_name, '')

                                if name in blacklist:
                                    continue

                                ref.extract(unique_name + name, path=tmpdir)

                            _output.put((False, OnGithubNewVersionUpdating.manager.notify, GithubStatus.COPYING))

                            copy_tree(Path(tmpdir) / unique_name, GAME_PATH)

            _output.put((False, OnGithubNewVersionUpdating.manager.notify, GithubStatus.FINISHING))

            metadata['sha'] = most_recent_commit_sha

            with open(DATA_PATH / 'metadata.wcs_install', 'w') as outputfile:
                dump(metadata, outputfile, indent=4)

            _output.put((True, OnGithubNewVersionInstalled.manager.notify))
        except:
            _output.put((True, None))
            raise

    def _refresh_modules(self, module_type_name, update_listener):
        github = self._connect()

        for i, repository in enumerate(GITHUB_REPOSITORIES, 1):
            repo = github.get_repo(repository)

            # Try to get the modules from the repository
            try:
                contents = repo.get_contents(module_type_name)
            # Did not find any modules
            except UnknownObjectException:
                continue

            path = MODULE_PATH / module_type_name

            # The modules from the repository
            modules = list([x.name for x in contents])

            # Are we in the last repository?
            if i == len(GITHUB_REPOSITORIES):
                # Loop through all the modules that has been added, and is not in the modules
                for name in [name for name in self[module_type_name] if name not in modules]:
                    # Send the module to the listener since there's no more repositories that has it
                    _output.put((False, update_listener.manager.notify, name, self[module_type_name][name]))

            for name in modules:
                if module_type_name not in self or name not in self[module_type_name]:
                    wcs_install_path_old = path / name / '.wcs_install'
                    wcs_install_path = path / name / 'metadata.wcs_install'

                    if wcs_install_path_old.isfile():
                        with open(wcs_install_path_old) as inputfile:
                            repository_installed = inputfile.read()

                        with open(wcs_install_path, 'w') as outputfile:
                            dump({'last_updated':wcs_install_path_old.mtime, 'repository':repository_installed}, outputfile, indent=4)

                        wcs_install_path_old.remove()

                    if wcs_install_path.isfile():
                        status = GithubModuleStatus.INSTALLED

                        with open(wcs_install_path) as inputfile:
                            data = load(inputfile)

                        last_updated = data['last_updated']
                        repository_installed = data['repository']
                    else:
                        status = GithubModuleStatus.UNINSTALLED

                        last_updated = None
                        repository_installed = None

                    self[module_type_name][name] = {'status':status, 'last_updated':last_updated, 'repository':repository_installed, 'repositories':{repository:{}}}

                    # TODO: Move this out of here (takes over twice as long with this)
                    commits = repo.get_commits(path=module_type_name + '/' + name + '/')

                    try:
                        self[module_type_name][name]['repositories'][repository]['last_modified'] = commits[0].commit.committer.date.timestamp()
                    except IndexError:
                        self[module_type_name][name]['repositories'][repository]['last_modified'] = None

                # Are we in the last repository?
                if i == len(GITHUB_REPOSITORIES):
                    _output.put((False, update_listener.manager.notify, name, self[module_type_name][name]))

    def _refresh_race_modules(self):
        try:
            self._refresh_modules('races', OnGithubRaceModuleUpdate)

            _output.put((True, OnGithubRaceModulesRefreshed.manager.notify, self['races']))
        except:
            _output.put((True, None))
            raise

    def _refresh_item_modules(self):
        try:
            self._refresh_modules('items', OnGithubItemModuleUpdate)

            _output.put((True, OnGithubItemModulesRefreshed.manager.notify, self['items']))
        except:
            _output.put((True, None))
            raise

    def _install_module(self, repository, module, name, userid):
        try:
            github = self._connect()
            repo = github.get_repo(repository)

            self._download_module(repo, f'{module}/{name}')

            metadata_path = MODULE_PATH / module / name / 'metadata.wcs_install'
            last_updated = time()

            with open(metadata_path, 'w') as outputfile:
                dump({'last_updated':last_updated, 'repository':repository}, outputfile, indent=4)

            self[module][name]['status'] = GithubModuleStatus.INSTALLED
            self[module][name]['last_updated'] = last_updated
            self[module][name]['repository'] = repository

            _output.put((True, OnGithubModuleInstalled.manager.notify, repository, module, name, userid))
        except:
            _output.put((True, OnGithubModuleFailed.manager.notify, repository, module, name, userid, GithubModuleStatus.INSTALLING))
            raise

    def _update_module(self, repository, module, name, userid):
        try:
            github = self._connect()
            repo = github.get_repo(repository)

            path = MODULE_PATH / module / name
            config_path = path / 'config.json'
            config_tmp_path = path / 'config.tmp.json'

            if config_path.isfile():
                config_path.rename(config_tmp_path)

            self._download_module(repo, f'{module}/{name}')

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

            metadata_path = MODULE_PATH / module / name / 'metadata.wcs_install'
            last_updated = time()

            with open(metadata_path) as inputfile:
                data = load(inputfile)

            data['last_updated'] = last_updated

            with open(metadata_path, 'w') as outputfile:
                dump(data, outputfile, indent=4)

            self[module][name]['status'] = GithubModuleStatus.INSTALLED
            self[module][name]['last_updated'] = last_updated

            _output.put((True, OnGithubModuleUpdated.manager.notify, repository, module, name, userid))
        except:
            _output.put((True, OnGithubModuleFailed.manager.notify, repository, module, name, userid, GithubModuleStatus.UPDATING))
            raise

    def _uninstall_module(self, repository, module, name, userid):
        try:
            if (MODULE_PATH_ES / module / name).isdir():
                (MODULE_PATH_ES / module / name).rmtree()

            (MODULE_PATH / module / name).rmtree()

            self[module][name]['status'] = GithubModuleStatus.UNINSTALLED
            self[module][name]['last_updated'] = None
            self[module][name]['repository'] = None

            _output.put((True, OnGithubModuleUninstalled.manager.notify, repository, module, name, userid))
        except:
            _output.put((True, OnGithubModuleFailed.manager.notify, repository, module, name, userid, GithubModuleStatus.UNINSTALLING))
            raise

    def _download_module(self, repo, from_path):
        contents = repo.get_contents(from_path)
        name = from_path.split('/')[1]

        for content in contents:
            if content.name.endswith(f'{name}.py') or content.name.endswith(f'es_{name}.txt'):
                path = MODULE_PATH_ES / content.path
            else:
                path = MODULE_PATH / content.path

            if content.type == 'dir':
                if not path.isdir():
                    path.makedirs()

                self._download_module(repo, content.path)
            else:
                if not path.parent.isdir():
                    path.parent.makedirs()

                with open(path, 'wb') as outputfile:
                    outputfile.write(repo.get_contents(content.path).decoded_content)

    def _refresh_commits(self):
        try:
            github = self._connect()
            repo = github.get_repo(f'{info.author.replace(" ", "")}/WCS')

            commits = []

            for response in repo.get_commits():
                commits.append({'date':response.commit.author.date, 'author':response.commit.author.name, 'messages':response.commit.message})

            _output.put((True, OnGithubCommitsRefreshed.manager.notify, commits))
        except:
            _output.put((True, None))
            raise

    def _start_thread(self, target, name, args=None):
        if not self._counter:
            self._repeat.start(0.1)

        self._counter += 1

        thread = Thread(target=target, name=name, args=args or ())
        thread.start()

        self._threads.append(thread)

    def stop(self):
        for thread in self._threads:
            if thread.is_alive():
                thread.join()

        self._repeat.stop()

    def check_new_version(self):
        if self._checking_new_version:
            return

        self._checking_new_version = True

        self._start_thread(self._check_new_version, 'wcs.checking')

    def install_new_version(self):
        if self._installing_new_version:
            return

        self._installing_new_version = True

        self._start_thread(self._install_new_version, 'wcs.installing')

    def refresh_race_modules(self):
        if self._refreshing_race_modules:
            return

        self._refreshing_race_modules = True

        OnGithubRaceModulesRefresh.manager.notify()

        self._start_thread(self._refresh_race_modules, 'wcs.refresh.race.modules')

    def refresh_item_modules(self):
        if self._refreshing_item_modules:
            return

        self._refreshing_itemmodules = True

        OnGithubItemModulesRefresh.manager.notify()

        self._start_thread(self._refresh_item_modules, 'wcs.refresh.item.modules')

    def install_module(self, repository, module, name, userid=None):
        assert self[module][name]['status'] is GithubModuleStatus.UNINSTALLED

        self[module][name]['status'] = GithubModuleStatus.INSTALLING

        self._start_thread(self._install_module, f'wcs.install.{module}.{name}', (repository, module, name, userid))

    def update_module(self, module, name, userid=None):
        assert self[module][name]['status'] is GithubModuleStatus.INSTALLED

        self[module][name]['status'] = GithubModuleStatus.UPDATING

        self._start_thread(self._update_module, f'wcs.update.{module}.{name}', (self[module][name]['repository'], module, name, userid))

    def uninstall_module(self, module, name, userid=None):
        assert self[module][name]['status'] is GithubModuleStatus.INSTALLED

        self[module][name]['status'] = GithubModuleStatus.UNINSTALLING

        self._start_thread(self._uninstall_module, f'wcs.uninstall.{module}.{name}', (self[module][name]['repository'], module, name, userid))

    def refresh_commits(self):
        if self._refreshing_commits:
            return

        self._refreshing_commits = True

        OnGithubCommitsRefresh.manager.notify()

        self._start_thread(self._refresh_commits, 'wcs.refresh.commits')
github_manager = _GithubManager()


# ============================================================================
# >> LISTENERS
# ============================================================================
@OnGithubCommitsRefreshed
def on_github_commits_refreshed(commits):
    github_manager._refreshing_commits = False


@OnGithubModuleFailed
def on_github_failed(repository, module, name, userid, task):
    if task is GithubModuleStatus.INSTALLING:
        _send_message(module, github_installing_failed_message, userid, name=name)

        github_manager[module][name]['status'] = GithubModuleStatus.UNINSTALLED
    elif task is GithubModuleStatus.UPDATING:
        _send_message(module, github_updating_failed_message, userid, name=name)

        github_manager[module][name]['status'] = GithubModuleStatus.INSTALLED
    elif task is GithubModuleStatus.UNINSTALLING:
        _send_message(module, github_uninstalling_failed_message, userid, name=name)

        github_manager[module][name]['status'] = GithubModuleStatus.INSTALLED


@OnGithubNewVersionChecked
def on_github_new_version_checked(version, commits):
    github_manager._checking_new_version = False


@OnGithubNewVersionInstalled
def on_github_new_version_installed():
    github_manager._installing_new_version = False


@OnGithubRaceModulesRefreshed
def on_github_race_modules_refreshed(races):
    github_manager._refreshing_race_modules = False


@OnGithubItemModulesRefreshed
def on_github_item_modules_refreshed(items):
    github_manager._refreshing_item_modules = False


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
