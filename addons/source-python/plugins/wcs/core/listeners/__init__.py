# ../wcs/core/listeners/__init__.py

# ============================================================================
# >> IMPORTS
# ============================================================================
# Source.Python Imports
#   Listeners
from listeners import ListenerManager
from listeners import ListenerManagerDecorator


# ============================================================================
# >> ALL DECLARATION
# ============================================================================
__all__ = (
    'OnClientAuthorized',
    'OnClientConnect',
    'OnClientDisconnect',
    'OnGithubCommitsRefresh',
    'OnGithubCommitsRefreshed',
    'OnGithubModuleFailed',
    'OnGithubModuleInstalled',
    'OnGithubModuleUpdated',
    'OnGithubModuleUninstalled',
    'OnGithubModulesRefresh',
    'OnGithubModulesRefreshed',
    'OnGithubNewVersionChecked',
    'OnGithubNewVersionInstalled',
    'OnGithubNewVersionUpdating',
    'OnIsItemUsable',
    'OnIsItemUsableText',
    'OnIsRaceUsable',
    'OnIsRaceUsableText',
    'OnIsSkillExecutable',
    'OnIsSkillExecutableText',
    'OnPlayerChangeRace',
    'OnPlayerDelete',
    'OnPlayerDestroy',
    'OnPlayerLevelDown',
    'OnPlayerLevelUp',
    'OnPlayerQuery',
    'OnPlayerRankUpdate',
    'OnPlayerReady',
    'OnPluginItemLoad',
    'OnPluginRaceLoad',
    'OnPluginUnload',
    'OnSettingsLoaded',
    'OnTakeDamage',
    'OnTakeDamageAlive',
)


# ============================================================================
# >> CLASSES
# ============================================================================
class OnClientAuthorized(ListenerManagerDecorator):
    manager = ListenerManager()


class OnClientConnect(ListenerManagerDecorator):
    manager = ListenerManager()


class OnClientDisconnect(ListenerManagerDecorator):
    manager = ListenerManager()


class OnGithubCommitsRefresh(ListenerManagerDecorator):
    manager = ListenerManager()


class OnGithubCommitsRefreshed(ListenerManagerDecorator):
    manager = ListenerManager()


class OnGithubModuleFailed(ListenerManagerDecorator):
    manager = ListenerManager()


class OnGithubModulesRefresh(ListenerManagerDecorator):
    manager = ListenerManager()


class OnGithubModulesRefreshed(ListenerManagerDecorator):
    manager = ListenerManager()


class OnGithubModuleInstalled(ListenerManagerDecorator):
    manager = ListenerManager()


class OnGithubModuleUpdated(ListenerManagerDecorator):
    manager = ListenerManager()


class OnGithubModuleUninstalled(ListenerManagerDecorator):
    manager = ListenerManager()


class OnGithubNewVersionChecked(ListenerManagerDecorator):
    manager = ListenerManager()


class OnGithubNewVersionInstalled(ListenerManagerDecorator):
    manager = ListenerManager()


class OnGithubNewVersionUpdating(ListenerManagerDecorator):
    manager = ListenerManager()


class OnIsItemUsable(ListenerManagerDecorator):
    manager = ListenerManager()


class OnIsItemUsableText(ListenerManagerDecorator):
    manager = ListenerManager()


class OnIsRaceUsable(ListenerManagerDecorator):
    manager = ListenerManager()


class OnIsRaceUsableText(ListenerManagerDecorator):
    manager = ListenerManager()


class OnIsSkillExecutable(ListenerManagerDecorator):
    manager = ListenerManager()


class OnIsSkillExecutableText(ListenerManagerDecorator):
    manager = ListenerManager()


class OnPlayerChangeRace(ListenerManagerDecorator):
    manager = ListenerManager()


class OnPlayerDelete(ListenerManagerDecorator):
    manager = ListenerManager()


class OnPlayerDestroy(ListenerManagerDecorator):
    manager = ListenerManager()


class OnPlayerLevelDown(ListenerManagerDecorator):
    manager = ListenerManager()


class OnPlayerLevelUp(ListenerManagerDecorator):
    manager = ListenerManager()


class OnPlayerQuery(ListenerManagerDecorator):
    manager = ListenerManager()


class OnPlayerRankUpdate(ListenerManagerDecorator):
    manager = ListenerManager()


class OnPlayerReady(ListenerManagerDecorator):
    manager = ListenerManager()


class OnPluginItemLoad(ListenerManagerDecorator):
    manager = ListenerManager()


class OnPluginRaceLoad(ListenerManagerDecorator):
    manager = ListenerManager()


class OnPluginUnload(ListenerManagerDecorator):
    manager = ListenerManager()


class OnSettingsLoaded(ListenerManagerDecorator):
    manager = ListenerManager()


class OnTakeDamage(ListenerManagerDecorator):
    manager = ListenerManager()


class OnTakeDamageAlive(ListenerManagerDecorator):
    manager = ListenerManager()
