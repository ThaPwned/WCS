# ../wcs/core/players/__init__.py

# ============================================================================
# >> IMPORTS
# ============================================================================
# Source.Python Imports
#   Entities
from entities.entity import Entity
#   Listeners
from listeners import OnEntityDeleted


# ============================================================================
# >> ALL DECLARATION
# ============================================================================
__all__ = (
    'set_weapon_name',
    'team_data',
)


# ============================================================================
# >> GLOBAL VARIABLES
# ============================================================================
team_data = {2:{}, 3:{}}

_global_weapon_entity = None


# ============================================================================
# >> FUNCTIONS
# ============================================================================
def set_weapon_name(name, prefix='wcs'):
    global _global_weapon_entity

    if _global_weapon_entity is None:
        _global_weapon_entity = Entity.create('info_target')

    _global_weapon_entity.set_key_value_string('classname', ('' if prefix is None else prefix + '_') + name)

    return _global_weapon_entity.index


# ============================================================================
# >> LISTENERS
# ============================================================================
@OnEntityDeleted
def on_entity_deleted(base_entity):
    if not base_entity.is_networked():
        return

    global _global_weapon_entity

    if _global_weapon_entity is not None:
        if base_entity.index == _global_weapon_entity.index:
            _global_weapon_entity = None
