# ../wcs/core/helpers/effects.py

# ============================================================================
# >> IMPORTS
# ============================================================================
# Python Imports
#   Functools
from functools import wraps
#   Re
from re import sub
#   Shlex
from shlex import split

# Source.Python Imports
#   Commands
from _commands import Command
from commands.typed import TypedServerCommand
#   Effects
from effects.base import TempEntity
#   Engines
from engines.precache import Decal
from engines.precache import Model
#   Mathlib
from mathlib import QAngle
from mathlib import Vector
#   Players
from players.helpers import index_from_userid


# ============================================================================
# >> ALL DECLARATION
# ============================================================================
__all__ = (
    'effect101',
    'effect102',
    'effect103',
    'effect104',
    'effect105',
    'effect106',
    'effect107',
    'effect108',
    'effect109',
    'effect110',
    'effect111',
    'effect112',
    'effect113',
    'effect114',
    'effect115',
    'effect116',
    'effect117',
    'effect118',
    'effect119',
    'effect120',
    'effect121',
    'effect122',
    'effect123',
    'effect124',
    'effect125',
    'effect126',
    'effect127',
    'effect128',
    'effect129',
    'effect130',
    'effect131',
    'effect132',
    'effect133',
    'effect134',
    'effect135',
    'effect1',
    'effect2',
    'effect3',
    'effect4',
    'effect5',
    'effect6',
    'effect7',
    'effect8',
    'effect9',
    'effect10',
    'effect11',
    'effect12',
    'effects_manager',
)


# ============================================================================
# >> CLASSES
# ============================================================================
# Emulates a real Command object (poorly)
class _Command(object):
    def __init__(self, command):
        self._command = command
        self._command_split = split(command)

    def __len__(self):
        return len(self._command_split)

    def __getitem__(self, index):
        return self._command_split[index]

    def _obj(self):
        raise NotImplementedError()

    def _ptr(self):
        raise NotImplementedError()

    def tokenize(self):
        raise NotImplementedError()

    @property
    def arg_string(self):
        return ' '.join(split(self._command)[1:])

    @property
    def command_string(self):
        return self._command

    @property
    def max_command_length(self):
        return Command.max_command_length


class _EffectsManager(dict):
    def __getitem__(self, name):
        return TempEntity(super().__getitem__(name))

    def execute(self, string, **kwargs):
        if kwargs:
            string = sub(r'server_var\(([a-zA-Z0-9_]+)\)', r'{\1}', string).format(**kwargs)

        command = _Command(string)

        TypedServerCommand.on_command(command)
effects_manager = _EffectsManager()


# ============================================================================
# >> FUNCTIONS
# ============================================================================
def register(name=None):
    def decorator(function):
        effects_manager[function.__qualname__] = name

        @wraps(function)
        def wrapper(*args, **kwargs):
            return function(*args, **kwargs)

        return wrapper

    return decorator


# ============================================================================
# >> EFFECTS
# ============================================================================
@register('Armor Ricochet')
def effect101(model, position, direction):
    """
    est_effect_01 <player filter> <delay> <model> <position x y z> <direction x y z>
    """
    if not isinstance(model, Model):
        model = Model(model)

    if not isinstance(position, Vector):
        position = Vector(*position)

    if not isinstance(direction, Vector):
        direction = Vector(*direction)

    te = TempEntity('Armor Ricochet')
    te.position = position
    te.direction = direction

    return te


@register('BeamEntPoint')
def effect102(model, start_entity_index, start_point, end_entity_index, end_point, frame_rate, life_time, start_width, end_width, fade_length, amplitude, red, green, blue, alpha, speed):
    """
    est_effect_02 <player filter> <delay> <model> <start entity> <start position x y z> <end entity> <end position x y z> <framerate> <life> <start width> <end width> <fade distance> <amplitude> <red> <green> <blue> <alpha> <speed>
    """
    if not isinstance(model, Model):
        model = Model(model)

    if not isinstance(start_point, Vector):
        start_point = Vector(*start_point)

    if not isinstance(end_point, Vector):
        end_point = Vector(*end_point)

    te = TempEntity('BeamEntPoint')
    te.model = model
    te.halo = model
    te.start_entity_index = start_entity_index
    te.start_point = start_point
    te.end_entity_index = end_entity_index
    te.end_point = end_point
    te.frame_rate = frame_rate
    te.life_time = life_time
    te.start_width = start_width
    te.end_width = end_width
    te.fade_length = fade_length
    te.amplitude = amplitude
    te.red = red
    te.green = green
    te.blue = blue
    te.alpha = alpha
    te.speed = speed

    return te


@register('BeamEnts')
def effect103(model, start_entity_index, end_entity_index, frame_rate, start_width, end_width, fade_length, amplitude, red, green, blue, alpha, speed):
    """
    est_effect_03 <player filter> <delay> <model> <start entity> <end entity> <framerate> <life> <start width> <end width> <fade distance> <amplitude> <red> <green> <blue> <alpha> <speed>
    """
    if not isinstance(model, Model):
        model = Model(model)

    te = TempEntity('BeamEnts')
    te.model = model
    te.halo = model
    te.start_entity_index = start_entity_index
    te.end_entity_index = end_entity_index
    te.frame_rate = frame_rate
    te.start_width = start_width
    te.end_width = end_width
    te.fade_length = fade_length
    te.amplitude = amplitude
    te.red = red
    te.green = green
    te.blue = blue
    te.alpha = alpha
    te.speed = speed

    return te


@register('BeamFollow')
def effect104(model, entity_index, life_time, start_width, end_width, fade_length, red, green, blue, alpha):
    """
    est_effect_04 <player filter> <delay> <model> <follow entity> <life> <start width> <end width> <fade distance> <red> <green> <blue> <alpha>
    """
    if not isinstance(model, Model):
        model = Model(model)

    te = TempEntity('BeamFollow')
    te.model = model
    te.halo = model
    te.entity_index = entity_index
    te.life_time = life_time
    te.start_width = start_width
    te.end_width = end_width
    te.fade_length = fade_length
    te.red = red
    te.green = green
    te.blue = blue
    te.alpha = alpha

    return te


@register('BeamLaser')
def effect105(model, start_entity_index, end_entity_index, frame_rate, life_time, start_width, end_width, fade_length, amplitude, red, green, blue, alpha, speed):
    """
    est_effect_05 <player filter> <delay> <model> <start entity> <end entity> <framerate> <life> <start width> <end width> <fade distance> <amplitude> <red> <green> <blue> <alpha> <speed>
    """
    if not isinstance(model, Model):
        model = Model(model)

    te = TempEntity('BeamLaser')
    te.model = model
    te.halo = model
    te.start_entity_index = start_entity_index
    te.end_entity_index = end_entity_index
    te.frame_rate = frame_rate
    te.life_time = life_time
    te.start_width = start_width
    te.end_width = end_width
    te.fade_length = fade_length
    te.amplitude = amplitude
    te.red = red
    te.green = green
    te.blue = blue
    te.alpha = alpha
    te.speed = speed

    return te


@register('BeamPoints')
def effect106(model, start_point, end_point, frame_rate, life_time, start_width, end_width, fade_length, amplitude, red, green, blue, alpha, speed):
    """
    est_effect_06 <player filter> <delay> <model> <start position x y z> <end position x y z> <framerate> <life> <start width> <end width> <fade distance> <amplitude> <red> <green> <blue> <alpha> <speed>
    """
    if not isinstance(model, Model):
        model = Model(model)

    if not isinstance(start_point, Vector):
        start_point = Vector(*start_point)

    if not isinstance(end_point, Vector):
        end_point = Vector(*end_point)

    te = TempEntity('BeamPoints')
    te.model = model
    te.halo = model
    te.start_point = start_point
    te.end_point = end_point
    te.frame_rate = frame_rate
    te.life_time = life_time
    te.start_width = start_width
    te.end_width = end_width
    te.fade_length = fade_length
    te.amplitude = amplitude
    te.red = red
    te.green = green
    te.blue = blue
    te.alpha = alpha
    te.speed = speed

    return te


@register('BeamPoints')
def effect107(model, start_point, end_point, frame_rate, life_time, width, fade_length, amplitude, red, green, blue, alpha, speed):
    """
    est_effect_07 <player filter> <delay> <model> <start entity> <end entity> <framerate> <life> <width> <spread> <amplitude> <red> <green> <blue> <alpha> <speed>
    """
    if not isinstance(model, Model):
        model = Model(model)

    if not isinstance(start_point, Vector):
        start_point = Vector(*start_point)

    if not isinstance(end_point, Vector):
        end_point = Vector(*end_point)

    te = TempEntity('BeamPoints')
    te.model = model
    te.halo = model
    te.start_point = start_point
    te.end_point = end_point
    te.frame_rate = frame_rate
    te.life_time = life_time
    te.start_width = width
    te.end_width = width
    te.fade_length = fade_length
    te.amplitude = amplitude
    te.red = red
    te.green = green
    te.blue = blue
    te.alpha = alpha
    te.speed = speed

    return te


@register('BeamRingPoint')
def effect108(model, center, start_radius, end_radius, frame_rate, life_time, width, fade_length, amplitude, red, green, blue, alpha, speed, flags):
    """
    est_effect_08 <player filter> <delay> <model> <middle x y z> <start radius> <end radius> <framerate> <life> <width> <spread> <amplitude> <red> <green> <blue> <alpha> <speed> <flags>
    """
    if not isinstance(model, Model):
        model = Model(model)

    if not isinstance(center, Vector):
        center = Vector(*center)

    te = TempEntity('BeamRingPoint')
    te.model = model
    te.halo = model
    te.center = center
    te.start_radius = start_radius
    te.end_radius = end_radius
    te.frame_rate = frame_rate
    te.life_time = life_time
    te.start_width = width
    te.end_width = width
    te.fade_length = fade_length
    te.amplitude = amplitude
    te.red = red
    te.green = green
    te.blue = blue
    te.alpha = alpha
    te.speed = speed
    te.flags = flags

    return te


@register('BeamSpline')
def effect109(model, points_length, points):
    """
    est_effect_09 <player filter> <delay> <model> <point count> <points x y z>
    """
    if not isinstance(model, Model):
        model = Model(model)

    if not isinstance(points, Vector):
        points = Vector(*points)

    te = TempEntity('BeamSpline')
    te.points_length = points_length
    te.points = points

    return te


@register('Blood Sprite')
def effect110(model, origin, direction, red, green, blue, alpha, size):
    """
    est_effect_10 <player filter> <delay> <model> <origin x y z> <direction x y z> <red> <green> <blue> <alpha> <size>
    """
    if not isinstance(model, Model):
        model = Model(model)

    if not isinstance(origin, Vector):
        origin = Vector(*origin)

    if not isinstance(direction, Vector):
        direction = Vector(*direction)

    te = TempEntity('Blood Sprite')
    te.drop_model = model
    te.spray_model = model
    te.origin = origin
    te.direction = direction
    te.red = red
    te.green = green
    te.blue = blue
    te.alpha = alpha
    te.size = size

    return te


@register('Blood Stream')
def effect111(model, origin, direction, red, green, blue, alpha, amount):
    """
    est_effect_11 <player filter> <delay> <model> <origin x y z> <direction x y z> <red> <green> <blue> <alpha> <amount>
    """
    if not isinstance(model, Model):
        model = Model(model)

    if not isinstance(origin, Vector):
        origin = Vector(*origin)

    if not isinstance(direction, Vector):
        direction = Vector(*direction)

    te = TempEntity('Blood Stream')
    te.origin = origin
    te.direction = direction
    te.red = red
    te.green = green
    te.blue = blue
    te.alpha = alpha
    te.amount = amount

    return te


@register('Break Model')
def effect112(model, origin, angle, size, velocity, randomization, count, time, flags):
    """
    est_effect_12 <player filter> <delay> <model> <origin x y z> <angle p y r> <Size x y z> <velocity x y z> <randomization> <count> <time> <flags>

    """
    if not isinstance(model, Model):
        model = Model(model)

    if not isinstance(origin, Vector):
        origin = Vector(*origin)

    if not isinstance(angle, QAngle):
        angle = QAngle(*angle)

    if not isinstance(size, Vector):
        size = Vector(*size)

    if not isinstance(velocity, Vector):
        velocity = Vector(*velocity)

    te = TempEntity('Break Model')
    te.model = model
    te.origin = origin
    te.rotation = angle
    te.size = size
    te.velocity = velocity
    te.randomization = randomization
    te.count = count
    te.life_time = time
    te.flags = flags

    return te


@register('BSP Decal')
def effect113(decal, origin, index):
    """
    est_effect_13 <player filter> <delay> <decal> <origin x y z> <target entity index>
    """
    if not isinstance(decal, Decal):
        decal = Decal(decal)

    if not isinstance(origin, Vector):
        origin = Vector(*origin)

    te = TempEntity('BSP Decal')
    te.decal = decal
    te.origin = origin
    te.entity_index = index

    return te


@register('Bubbles')
def effect114(model, mins, maxs, height, count, speed):
    """
    est_effect_14 <player filter> <delay> <model> <min x y z> <max x y z> <height> <count> <speed>
    """
    if not isinstance(model, Model):
        model = Model(model)

    if not isinstance(mins, Vector):
        mins = Vector(*mins)

    if not isinstance(maxs, Vector):
        maxs = Vector(*maxs)

    te = TempEntity('Bubbles')
    te.model = model
    te.halo = model
    te.mins = mins
    te.maxs = maxs
    te.height = height
    te.count = count
    te.speed = speed

    return te


@register('Bubble Trail')
def effect115(model, mins, maxs, height, count, speed):
    """
    est_effect_15 <player filter> <delay> <model> <min x y z> <max x y z> <height> <count> <speed>
    """
    if not isinstance(model, Model):
        model = Model(model)

    if not isinstance(mins, Vector):
        mins = Vector(*mins)

    if not isinstance(maxs, Vector):
        maxs = Vector(*maxs)

    te = TempEntity('Bubble Trail')
    te.model = model
    te.halo = model
    te.mins = mins
    te.maxs = maxs
    te.height = height
    te.count = count
    te.speed = speed

    return te


@register('Entity Decal')
def effect116(decal, position, start, index, hitbox):
    """
    est_effect_16 <player filter> <delay> <model> <position x y z> <start x y z> <entity index> <hitbox>
    """
    if not isinstance(decal, Decal):
        decal = Decal(decal)

    if not isinstance(position, Vector):
        position = Vector(*position)

    if not isinstance(start, Vector):
        start = Vector(*start)

    te = TempEntity('Entity Decal')
    te.decal = decal
    te.origin = position
    te.start = start
    te.entity_index = index
    te.hitbox = hitbox

    return te


@register('Dust')
def effect117(position, direction, size, speed):
    """
    est_effect_17 <player filter> <delay> <position x y z> <direction x y z> <size> <speed>
    """
    if not isinstance(position, Vector):
        position = Vector(*position)

    if not isinstance(direction, Vector):
        direction = Vector(*direction)

    te = TempEntity('Dust')
    te.origin = position
    te.direction = direction
    te.size = size
    te.speed = speed

    return te


@register('Dynamic Light')
def effect118(origin, red, green, blue, exponent, radius, life_time, decay):
    """
    est_effect_18 <player filter> <delay> <position x y z> <red> <green> <blue> <exponent> <radius> <time> <decay>
    """
    if not isinstance(origin, Vector):
        origin = Vector(*origin)

    te = TempEntity('Dynamic Light')
    te.origin = origin
    te.red = red
    te.green = green
    te.blue = blue
    te.exponent = exponent
    te.radius = radius
    te.life_time = life_time
    te.decay = decay

    return te


@register('Energy Splash')
def effect119(position, direction, explosive):
    """
    est_effect_19 <player filter> <delay> <position x y z> <direction x y z> <explosive>
    """
    if not isinstance(position, Vector):
        position = Vector(*position)

    if not isinstance(direction, Vector):
        direction = Vector(*direction)

    te = TempEntity('Energy Splash')
    te.position = position
    te.direction = direction
    te.explosive = explosive

    return te


@register('Explosion')
def effect120(model, position, scale, frame_rate, flags, radius, magnitude, normal=None, material=None):
    """
    est_effect_20 <player filter> <delay> <model> <position x y z> <scale> <framerate> <flags> <radius> <magnitude> [normal x y z] [material type]
    """
    if not isinstance(position, Vector):
        position = Vector(*position)

    te = TempEntity('Explosion')
    te.position = position
    te.scale = scale
    te.frame_rate = frame_rate
    te.flags = flags
    te.radius = radius
    te.magnitude = magnitude

    if normal is not None:
        if not isinstance(normal, Vector):
            normal = Vector(*normal)

        te.normal = normal

    if material is not None:
        if isinstance(material, str):
            # /game/server/func_break.h
            # typedef enum { matGlass = 0, matWood, matMetal, matFlesh, matCinderBlock, matCeilingTile, matComputer, matUnbreakableGlass, matRocks, matWeb, matNone, matLastMaterial } Materials;
            material = {'glass':0, 'wood':1, 'metal':2, 'flesh':3, 'cinderblock':4, 'ceilingtile':5, 'computer':6, 'unbreakableglass':7, 'rocks':8, 'web':9}.get(material.lower(), 0)

        te.material_type = material

    return te


@register('Fizz')
def effect121(model, index, density, current):
    """
    est_effect_21 <player filter> <delay> <model> <entity> <density> <current>
    """
    if not isinstance(model, Model):
        model = Model(model)

    te = TempEntity('Fizz')
    te.model = model
    te.entity_index = index
    te.density = density
    te.current = current

    return te


@register('GaussExplosion')
def effect122(position, direction, type_):
    """
    est_effect_22 <player filter> <delay> <position x y z> <direction x y z> <type>
    """
    if not isinstance(position, Vector):
        position = Vector(*position)

    if not isinstance(direction, Vector):
        direction = Vector(*direction)

    te = TempEntity('GaussExplosion')
    te.position = position
    te.direction = direction
    te.type = type_

    return te


@register('GlowSprite')
def effect123(model, position, life_time, size, brightness):
    """
    est_effect_23 <player filter> <delay> <model> <position x y z> <life> <size> <brightness>
    """
    if not isinstance(model, Model):
        model = Model(model)

    if not isinstance(position, Vector):
        position = Vector(*position)

    te = TempEntity('GaussExplosion')
    te.model = model
    te.position = position
    te.life_time = life_time
    te.scale = size
    te.brightness = brightness

    return te


@register('Large Funnel')
def effect124(model, origin, reversed_):
    """
    est_effect_24 <player filter> <delay> <model> <position x y z> <reversed>
    """
    if not isinstance(model, Model):
        model = Model(model)

    if not isinstance(origin, Vector):
        origin = Vector(*origin)

    te = TempEntity('Large Funnel')
    te.model = model
    te.origin = origin
    te.reversed = reversed_

    return te


@register('Metal Sparks')
def effect125(position, direction):
    """
    est_effect_25 <player filter> <delay> <position x y z> <direction x y z>
    """
    if not isinstance(position, Vector):
        position = Vector(*position)

    if not isinstance(direction, Vector):
        direction = Vector(*direction)

    te = TempEntity('Metal Sparks')
    te.position = position
    te.direction = direction

    return te


@register('MuzzleFlash')
def effect126(position, angle, scale, type_):
    """
    est_effect_26 <player filter> <delay> <position x y z> <angle p y r> <scale> <type>
    """
    if not isinstance(position, Vector):
        position = Vector(*position)

    if not isinstance(angle, QAngle):
        angle = QAngle(*angle)

    te = TempEntity('Metal Sparks')
    te.origin = position
    te.angles = angle
    te.scale = scale
    te.type = type_

    return te


@register('physicsprop')
def effect127(model, skin, position, angle, velocity, flags, effects):
    """
    est_effect_27 <player filter> <delay> <model> <subtype/skin> <position x y z> <angle p y r> <velocity x y z> <flags> <effects>
    """
    if not isinstance(model, Model):
        model = Model(model)

    if not isinstance(position, Vector):
        position = Vector(*position)

    if not isinstance(angle, QAngle):
        angle = QAngle(*angle)

    if not isinstance(velocity, Vector):
        velocity = Vector(*velocity)

    te = TempEntity('physicsprop')
    te.model = model
    te.skin = skin
    te.origin = position
    te.angles = angle
    te.velocity = velocity
    te.flags = flags
    te.effects = effects

    return te


@register('Player Decal')
def effect128(position, player_index, entity_index):
    """
    est_effect_28 <player filter> <delay> <position x y z> <playerindex> <entity>
    """
    if not isinstance(position, Vector):
        position = Vector(*position)

    te = TempEntity('Player Decal')
    te.origin = position
    te.player_index = player_index
    te.entity_index = entity_index

    return te


@register('Projected Decal')
def effect129(decal, position, angle, distance):
    """
    est_effect_29 <player filter> <delay> <decal> <position x y z> <angle p y r> <distance>
    """
    if not isinstance(decal, Decal):
        decal = Decal(*decal)

    if not isinstance(position, Vector):
        position = Vector(*position)

    if not isinstance(angle, QAngle):
        angle = QAngle(*angle)

    te = TempEntity('Player Decal')
    te.decal = decal
    te.origin = position
    te.rotation = angle
    te.distance = distance

    return te


@register('Show Line')
def effect130(start, end):
    """
    est_effect_30 <player filter> <delay> <start x y z> <end x y z>
    """
    if not isinstance(start, Vector):
        start = Vector(*start)

    if not isinstance(end, Vector):
        end = Vector(*end)

    te = TempEntity('Show Line')
    te.start = start
    te.end = end

    return te


@register('Smoke')
def effect131(model, position, scale, frame_rate):
    """
    est_effect_31 <player filter> <delay> <model> <position x y z> <scale> <framerate>
    """
    if not isinstance(model, Model):
        model = Model(model)

    if not isinstance(position, Vector):
        position = Vector(*position)

    te = TempEntity('Smoke')
    te.model = model
    te.position = position
    te.scale = scale
    te.frame_rate = frame_rate

    return te


@register('Sparks')
def effect132(position, magnitude, trail_length, direction):
    """
    est_effect_32 <player filter> <delay> <position x y z> <magnitude> <trail length> <direction x y z>
    """
    if not isinstance(position, Vector):
        position = Vector(*position)

    if not isinstance(direction, Vector):
        direction = Vector(*direction)

    te = TempEntity('Smoke')
    te.position = position
    te.magnitude = magnitude
    te.trail_length = trail_length
    te.direction = direction

    return te


@register('Sprite')
def effect133(model, position, size, brightness):
    """
    est_effect_33 <player filter> <delay> <model> <position x y z> <size> <brightness>
    """
    if not isinstance(model, Model):
        model = Model(model)

    if not isinstance(position, Vector):
        position = Vector(*position)

    te = TempEntity('Sprite')
    te.model = model
    te.position = position
    te.size = size
    te.brightness = brightness

    return te


@register('Sprite Spray')
def effect134(model, position, direction, speed, noise, count):
    """
    est_effect_34 <player filter> <delay> <model> <position x y z> <direction x y z> <speed> <noise> <count>
    """
    if not isinstance(model, Model):
        model = Model(model)

    if not isinstance(position, Vector):
        position = Vector(*position)

    if not isinstance(direction, Vector):
        direction = Vector(*direction)

    te = TempEntity('Sprite Spray')
    te.model = model
    te.position = position
    te.direction = direction
    te.speed = speed
    te.noise = noise
    te.count = count

    return te


@register('World Decal')
def effect135(decal, position):
    """
    est_effect_35 <player filter> <delay> <Decal> <Position x y z>
    """
    if not isinstance(decal, Decal):
        decal = Decal(decal)

    if not isinstance(position, Vector):
        position = Vector(*position)

    te = TempEntity('World Decal')
    te.decal = decal
    te.position = position

    return te


@register('Armor Ricochet')
def effect1(model, x, y, z, dx, dy, dz):
    """
    est_effect 1 <player filter> <delay> <model> (position <x> <y> <z>) (direction <x> <y> <z>)
    """
    if not isinstance(model, Model):
        model = Model(model)

    te = TempEntity('Armor Ricochet')
    te.position = Vector(x, y, z)
    te.direction = Vector(dx, dy, dz)

    return te


@register('BeamEntPoint')
def effect2(model, start_userid, end_userid, life_time, start_width, end_width, red, green, blue, alpha):
    """
    est_effect 2 <player filter> <delay> <model> <start userid> <end userid> <life> <width> <end width> <red> <green> <blue> <alpha>
    """
    if not isinstance(model, Model):
        model = Model(model)

    te = TempEntity('BeamEntPoint')
    te.model = model
    te.halo = model
    te.start_entity_index = index_from_userid(start_userid)
    te.end_entity_index = index_from_userid(end_userid)
    te.life_time = life_time
    te.start_width = start_width
    te.end_width = end_width
    te.red = red
    te.green = green
    te.blue = blue
    te.alpha = alpha

    return te


@register('BeamPoints')
def effect3(model, x1, y1, z1, x2, y2, z2, life_time, start_width, end_width, red, green, blue, alpha):
    """
    est_effect 3 <player filter> <delay> <model> (start <x> <y> <z>) (end <x> <y> <z>) <life> <width> <end width> <red> <green> <blue> <alpha>
    """
    if not isinstance(model, Model):
        model = Model(model)

    te = TempEntity('BeamPoints')
    te.model = model
    te.halo = model
    te.start_point = Vector(x1, y1, z1)
    te.end_point = Vector(x2, y2, z2)
    te.life_time = life_time
    te.start_width = start_width
    te.end_width = end_width
    te.red = red
    te.green = green
    te.blue = blue
    te.alpha = alpha

    return te


@register('BeamFollow')
def effect4(model, userid, life_time, start_width, end_width, fade_length, red, green, blue, alpha):
    """
    est_effect 4 <player filter> <delay> <model> <userid> <life> <width> <end width> <time to fade> <red> <green> <blue> <alpha>
    """
    if not isinstance(model, Model):
        model = Model(model)

    te = TempEntity('BeamFollow')
    te.model = model
    te.halo = model
    te.entity_index = index_from_userid(userid)
    te.life_time = life_time
    te.start_width = start_width
    te.end_width = end_width
    te.fade_length = fade_length
    te.red = red
    te.green = green
    te.blue = blue
    te.alpha = alpha

    return te


@register('BeamRing')
def effect5(model, start_userid, end_entity_index, life_time, width, fade_length, amplitude, red, green, blue, alpha, speed):
    """
    est_effect 5 <player filter> <delay> <model> <userid> <end index> <life> <width> <spread> <amplitude> <red> <green> <blue> <alpha> <speed>
    """
    if not isinstance(model, Model):
        model = Model(model)

    te = TempEntity('BeamRing')
    te.model = model
    te.halo = model
    te.start_entity_index = index_from_userid(start_userid)
    te.end_entity_index = end_entity_index
    te.life_time = life_time
    te.start_width = width
    te.end_width = width
    te.fade_length = fade_length
    te.amplitude = amplitude
    te.red = red
    te.green = green
    te.blue = blue
    te.alpha = alpha
    te.speed = speed

    return te


@register('Large Funnel')
def effect6(model, x, y, z, reversed_):
    """
    est_effect 6 <player filter> <delay> <model> <x> <y> <z> <reversed>
    """
    if not isinstance(model, Model):
        model = Model(model)

    te = TempEntity('Large Funnel')
    te.model = model
    te.origin = Vector(x, y, z)
    te.reversed = reversed_

    return te


@register('Smoke')
def effect7(model, x, y, z, scale, frame_rate):
    """
    est_effect 7 <player filter> <delay> <model> <x> <y> <z> <scale> <framerate>
    """
    if not isinstance(model, Model):
        model = Model(model)

    te = TempEntity('Smoke')
    te.model = model
    te.origin = Vector(x, y, z)
    te.scale = scale
    te.frame_rate = frame_rate

    return te


@register('Metal Sparks')
def effect8(model, x, y, z, dx, dy, dz):
    """
    est_effect 8 <player filter> <delay> <model> <x> <y> <z> (towards <x> <y> <z>)
    """
    if not isinstance(model, Model):
        model = Model(model)

    te = TempEntity('Metal Sparks')
    te.position = Vector(x, y, z)
    te.direction = Vector(dx, dy, dz)

    return te


@register('GaussExplosion')
def effect9(model, x, y, z, dx, dy, dz, type_):
    """
    est_effect 9 <player filter> <delay> <model> <x> <y> <z> (towards <x> <y> <z>) <type>
    """
    if not isinstance(model, Model):
        model = Model(model)

    te = TempEntity('GaussExplosion')
    te.origin = Vector(x, y, z)
    te.direction = Vector(dx, dy, dz)
    te.type = type_

    return te


@register('BeamRingPoint')
def effect10(model, x, y, z, start_radius, end_radius, life_time, width, fade_length, amplitude, red, green, blue, alpha, speed):
    """
    est_effect 10 <player filter> <delay> <model> <x> <y> <z> <start radius> <end radius> <life> <width> <spread> <amplitude> <red> <green> <blue> <alpha> <speed>
    """
    if not isinstance(model, Model):
        model = Model(model)

    te = TempEntity('BeamRingPoint')
    te.model = model
    te.halo = model
    te.center = Vector(x, y, z)
    te.start_radius = start_radius
    te.end_radius = end_radius
    te.life_time = life_time
    te.start_width = width
    te.end_width = width
    te.fade_length = fade_length
    te.amplitude = amplitude
    te.red = red
    te.green = green
    te.blue = blue
    te.alpha = alpha
    te.speed = speed

    return te


@register('GlowSprite')
def effect11(model, x, y, z, life_time, scale, brightness):
    """
    est_effect 11 <player filter> <delay> <model> <x> <y> <z> <life> <size> <brightness>
    """
    if not isinstance(model, Model):
        model = Model(model)

    te = TempEntity('GlowSprite')
    te.model = model
    te.origin = Vector(x, y, z)
    te.life_time = life_time
    te.scale = scale
    te.brightness = brightness

    return te


@register()
def effect12(*args):
    """
    est_effect 12 <player filter> <delay> <model> (pos <x> <y> <z>) (angle <x> <y> <z>) (velocity <x> <y> <z>) <subtype> <flags> <randomize>
    """
    raise NotImplementedError()
