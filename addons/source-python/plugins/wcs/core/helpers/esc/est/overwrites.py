# ../wcs/core/helpers/esc/est/overwrites.py

# ============================================================================
# >> IMPORTS
# ============================================================================
# Source.Python Imports
#   Commands
from commands.typed import TypedServerCommand as _TypedServerCommand


# ============================================================================
# >> ALL DECLARATION
# ============================================================================
__all__ = (
    'ESTCommand',
)


# ============================================================================
# >> CLASSES
# ============================================================================
class ESTCommand(_TypedServerCommand):
    def __init__(self, commands, permission=None, fail_callback=None):
        if isinstance(commands, list):
            if not commands[0].startswith('est_'):
                commands[0] = f'est_{commands[0]}'
        else:
            if not commands.startswith('est_'):
                commands = f'est_{commands}'

        super().__init__(commands, permission, fail_callback)

    def __call__(self, callback):
        super().__call__(callback)

        commands = self.commands

        if not (commands[0] if isinstance(commands, list) else commands).islower():
            if isinstance(commands, list):
                commands = [*commands]
                commands[0] = commands[0].lower()
            else:
                commands = commands.lower()

            ESTCommand(commands, self.permission, self.fail_callback)(callback)

        return callback
