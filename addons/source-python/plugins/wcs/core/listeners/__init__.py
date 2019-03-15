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
    'OnDownloadBegin',
    'OnDownloadComplete',
    'OnGithubFailed',
    'OnGithubRefresh',
    'OnGithubRefreshed',
    'OnGithubInstalled',
    'OnGithubUpdated',
    'OnGithubUninstalled',
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
)


# ============================================================================
# >> CLASSES
# ============================================================================
class OnDownloadBegin(ListenerManagerDecorator):
    manager = ListenerManager()


class OnDownloadComplete(ListenerManagerDecorator):
    manager = ListenerManager()


class OnGithubFailed(ListenerManagerDecorator):
    manager = ListenerManager()


class OnGithubRefresh(ListenerManagerDecorator):
    manager = ListenerManager()


class OnGithubRefreshed(ListenerManagerDecorator):
    manager = ListenerManager()


class OnGithubInstalled(ListenerManagerDecorator):
    manager = ListenerManager()


class OnGithubUpdated(ListenerManagerDecorator):
    manager = ListenerManager()


class OnGithubUninstalled(ListenerManagerDecorator):
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


class OnTakeDamage(ListenerManagerDecorator):
    manager = ListenerManager()


class OnTakeDamageAlive(ListenerManagerDecorator):
    manager = ListenerManager()
