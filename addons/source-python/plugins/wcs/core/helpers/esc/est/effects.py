# ../wcs/core/helpers/esc/est/effects.py

# ============================================================================
# >> IMPORTS
# ============================================================================
# WCS Imports
#   Helpers
from .converts import convert_userid_identifier_to_players
from .overwrites import ESTCommand
from ..converts import clamp
from ..converts import convert_to_vector
from ..converts import convert_to_qangle
from ..converts import optional
from ..converts import valid_userid
from ...effects import effect101
from ...effects import effect102
from ...effects import effect103
from ...effects import effect104
from ...effects import effect105
from ...effects import effect106
from ...effects import effect107
from ...effects import effect108
from ...effects import effect109
from ...effects import effect110
from ...effects import effect111
from ...effects import effect112
from ...effects import effect113
from ...effects import effect114
from ...effects import effect115
from ...effects import effect116
from ...effects import effect117
from ...effects import effect118
from ...effects import effect119
from ...effects import effect120
from ...effects import effect121
from ...effects import effect122
from ...effects import effect123
from ...effects import effect124
from ...effects import effect125
from ...effects import effect126
from ...effects import effect127
from ...effects import effect128
from ...effects import effect129
from ...effects import effect130
from ...effects import effect131
from ...effects import effect132
from ...effects import effect133
from ...effects import effect134
from ...effects import effect135
from ...effects import effect1
from ...effects import effect2
from ...effects import effect3
from ...effects import effect4
from ...effects import effect5
from ...effects import effect6
from ...effects import effect7
from ...effects import effect8
from ...effects import effect9
from ...effects import effect10
from ...effects import effect11
from ...effects import effect12


# ============================================================================
# >> ALL DECLARATION
# ============================================================================
__all__ = ()


# ============================================================================
# >> COMMANDS
# ============================================================================
@ESTCommand('Effect_01')
def effect101_command(command_info, filter_:convert_userid_identifier_to_players, delay:float, model:str, position:convert_to_vector, direction:convert_to_vector):
    effect101(position, direction).create(filter_, delay=delay)


@ESTCommand('Effect_02')
def effect102_command(command_info, filter_:convert_userid_identifier_to_players, delay:float, model:str, start_entity_index:optional(int), start_point:optional(convert_to_vector), end_entity_index:optional(int), end_point:optional(convert_to_vector), frame_rate:clamp(0), life_time:float, start_width:clamp(0, is_int=False), end_width:clamp(0, is_int=False), fade_length:int, amplitude:clamp(0, is_int=False), red:clamp(0, 255), green:clamp(0, 255), blue:clamp(0, 255), alpha:clamp(0, 255), speed:clamp(0)):
    effect102(model, start_entity_index, start_point, end_entity_index, end_point, frame_rate, life_time, start_width, end_width, fade_length, amplitude, red, green, blue, alpha, speed).create(filter_, delay=delay)


@ESTCommand('Effect_03')
def effect103_command(command_info, filter_:convert_userid_identifier_to_players, delay:float, model:str, start_entity_index:int, end_entity_index:int, frame_rate:clamp(0), start_width:clamp(0, is_int=False), end_width:clamp(0, is_int=False), fade_length:int, amplitude:clamp(0, is_int=False), red:clamp(0, 255), green:clamp(0, 255), blue:clamp(0, 255), alpha:clamp(0, 255), speed:clamp(0)):
    effect103(model, start_entity_index, end_entity_index, frame_rate, start_width, end_width, fade_length, amplitude, red, green, blue, alpha, speed).create(filter_, delay=delay)


@ESTCommand('Effect_04')
def effect104_command(command_info, filter_:convert_userid_identifier_to_players, delay:float, model:str, entity_index:int, life_time:float, start_width:clamp(0, is_int=False), end_width:clamp(0, is_int=False), fade_length:int, red:clamp(0, 255), green:clamp(0, 255), blue:clamp(0, 255), alpha:clamp(0, 255)):
    effect104(model, entity_index, life_time, start_width, end_width, fade_length, red, green, blue, alpha).create(filter_, delay=delay)


@ESTCommand('Effect_05')
def effect105_command(command_info, filter_:convert_userid_identifier_to_players, delay:float, model:str, start_entity_index:int, end_entity_index:int, frame_rate:clamp(0), life_time:float, start_width:clamp(0, is_int=False), end_width:clamp(0, is_int=False), fade_length:int, amplitude:clamp(0, is_int=False), red:clamp(0, 255), green:clamp(0, 255), blue:clamp(0, 255), alpha:clamp(0, 255), speed:clamp(0)):
    effect105(model, start_entity_index, end_entity_index, frame_rate, life_time, start_width, end_width, fade_length, amplitude, red, green, blue, alpha, speed).create(filter_, delay=delay)


@ESTCommand('Effect_06')
def effect106_command(command_info, filter_:convert_userid_identifier_to_players, delay:float, model:str, start_point:convert_to_vector, end_point:convert_to_vector, frame_rate:clamp(0), life_time:float, start_width:clamp(0, is_int=False), end_width:clamp(0, is_int=False), fade_length:int, amplitude:clamp(0, is_int=False), red:clamp(0, 255), green:clamp(0, 255), blue:clamp(0, 255), alpha:clamp(0, 255), speed:clamp(0)):
    effect106(model, start_point, end_point, frame_rate, life_time, start_width, end_width, fade_length, amplitude, red, green, blue, alpha, speed).create(filter_, delay=delay)


@ESTCommand('Effect_07')
def effect107_command(command_info, filter_:convert_userid_identifier_to_players, delay:float, model:str, start_point:convert_to_vector, end_point:convert_to_vector, frame_rate:clamp(0), life_time:float, width:float, fade_length:int, amplitude:clamp(0, is_int=False), red:clamp(0, 255), green:clamp(0, 255), blue:clamp(0, 255), alpha:clamp(0, 255), speed:clamp(0)):
    effect107(model, start_point, end_point, frame_rate, life_time, width, fade_length, amplitude, red, green, blue, alpha, speed).create(filter_, delay=delay)


@ESTCommand('Effect_08')
def effect108_command(command_info, filter_:convert_userid_identifier_to_players, delay:float, model:str, center:convert_to_vector, start_radius:float, end_radius:float, frame_rate:clamp(0), life_time:float, width:float, fade_length:int, amplitude:clamp(0, is_int=False), red:clamp(0, 255), green:clamp(0, 255), blue:clamp(0, 255), alpha:clamp(0, 255), speed:clamp(0), flags:int):
    effect108(model, center, start_radius, end_radius, frame_rate, life_time, width, fade_length, amplitude, red, green, blue, alpha, speed, flags).create(filter_, delay=delay)


@ESTCommand('Effect_09')
def effect109_command(command_info, filter_:convert_userid_identifier_to_players, delay:float, model:str, points_length:float, points:int):
    effect109(model, points_length, points).create(filter_, delay=delay)


@ESTCommand('Effect_10')
def effect110_command(command_info, filter_:convert_userid_identifier_to_players, delay:float, model:str, origin:convert_to_vector, direction:convert_to_vector, red:clamp(0, 255), green:clamp(0, 255), blue:clamp(0, 255), alpha:clamp(0, 255), size:int):
    effect110(model, origin, direction, red, green, blue, alpha, size).create(filter_, delay=delay)


@ESTCommand('Effect_11')
def effect111_command(command_info, filter_:convert_userid_identifier_to_players, delay:float, model:str, origin:convert_to_vector, direction:convert_to_vector, red:clamp(0, 255), green:clamp(0, 255), blue:clamp(0, 255), alpha:clamp(0, 255), amount:int):
    effect111(model, origin, direction, red, green, blue, alpha, amount).create(filter_, delay=delay)


@ESTCommand('Effect_12')
def effect112_command(command_info, filter_:convert_userid_identifier_to_players, delay:float, model, origin:convert_to_vector, angle:convert_to_qangle, size:convert_to_vector, velocity:convert_to_vector, randomization:int, count:int, time:float, flags:int):
    effect112(model, origin, angle, size, velocity, randomization, count, time, flags).create(filter_, delay=delay)


@ESTCommand('Effect_13')
def effect113_command(command_info, filter_:convert_userid_identifier_to_players, delay:float, decal:str, origin:convert_to_vector, index:int):
    effect113(decal, origin, index).create(filter_, delay=delay)


@ESTCommand('Effect_14')
def effect114_command(command_info, filter_:convert_userid_identifier_to_players, delay:float, model:str, mins:convert_to_vector, maxs:convert_to_vector, height:float, count:int, speed:clamp(0)):
    effect114(model, mins, maxs, height, count, speed).create(filter_, delay=delay)


@ESTCommand('Effect_15')
def effect115_command(command_info, filter_:convert_userid_identifier_to_players, delay:float, model:str, mins:convert_to_vector, maxs:convert_to_vector, height:float, count:int, speed:clamp(0)):
    effect115(model, mins, maxs, height, count, speed).create(filter_, delay=delay)


@ESTCommand('Effect_16')
def effect116_command(command_info, filter_:convert_userid_identifier_to_players, delay:float, decal:str, position:convert_to_vector, start:convert_to_vector, index:int, hitbox:int):
    effect116(decal, position, start, index, hitbox).create(filter_, delay=delay)


@ESTCommand('Effect_17')
def effect117_command(command_info, filter_:convert_userid_identifier_to_players, delay:float, position:convert_to_vector, direction:convert_to_vector, size:float, speed:clamp(0)):
    effect117(position, direction, size, speed).create(filter_, delay=delay)


@ESTCommand('Effect_18')
def effect118_command(command_info, filter_:convert_userid_identifier_to_players, delay:float, origin:convert_to_vector, red:clamp(0, 255), green:clamp(0, 255), blue:clamp(0, 255), exponent:int, radius:float, life_time:float, decay:int):
    effect118(origin, red, green, blue, exponent, radius, life_time, decay).create(filter_, delay=delay)


@ESTCommand('Effect_19')
def effect119_command(command_info, filter_:convert_userid_identifier_to_players, delay:float, position:convert_to_vector, direction:convert_to_vector, explosive:int):
    effect119(position, direction, explosive).create(filter_, delay=delay)


@ESTCommand('Effect_20')
def effect120_command(command_info, filter_:convert_userid_identifier_to_players, delay:float, model:str, position:convert_to_vector, scale:float, frame_rate:int, flags:int, radius:int, magnitude:int, normal:convert_to_vector=None, material:str=None):
    effect120(model, position, scale, frame_rate, flags, radius, magnitude, normal, material).create(filter_, delay=delay)


@ESTCommand('Effect_21')
def effect121_command(command_info, filter_:convert_userid_identifier_to_players, delay:float, model:str, index:int, density:int, current:int):
    effect121(model, index, density, current).create(filter_, delay=delay)


@ESTCommand('Effect_22')
def effect122_command(command_info, filter_:convert_userid_identifier_to_players, delay:float, position:convert_to_vector, direction:convert_to_vector, type_:int):
    effect122(position, direction, type_).create(filter_, delay=delay)


@ESTCommand('Effect_23')
def effect123_command(command_info, filter_:convert_userid_identifier_to_players, delay:float, model:str, position:convert_to_vector, life_time:float, size:float, brightness:int):
    effect123(model, position, life_time, size, brightness).create(filter_, delay=delay)


@ESTCommand('Effect_24')
def effect124_command(command_info, filter_:convert_userid_identifier_to_players, delay:float, model:str, origin:convert_to_vector, reversed_:int):
    effect124(model, origin, reversed_).create(filter_, delay=delay)


@ESTCommand('Effect_25')
def effect125_command(command_info, filter_:convert_userid_identifier_to_players, delay:float, position:convert_to_vector, direction:convert_to_vector):
    effect125(position, direction).create(filter_, delay=delay)


@ESTCommand('Effect_26')
def effect126_command(command_info, filter_:convert_userid_identifier_to_players, delay:float, position:convert_to_vector, angle:convert_to_qangle, scale:float, type_:int):
    effect126(position, angle, scale, type_).create(filter_, delay=delay)


@ESTCommand('Effect_27')
def effect127_command(command_info, filter_:convert_userid_identifier_to_players, delay:float, model:str, skin:int, position:convert_to_vector, angle:convert_to_qangle, velocity:convert_to_vector, flags:int, effects:int):
    effect127(model, skin, position, angle, velocity, flags, effects).create(filter_, delay=delay)


@ESTCommand('Effect_28')
def effect128_command(command_info, filter_:convert_userid_identifier_to_players, delay:float, position:convert_to_vector, player_index:int, entity_index:int):
    effect128(position, player_index, entity_index).create(filter_, delay=delay)


@ESTCommand('Effect_29')
def effect129_command(command_info, filter_:convert_userid_identifier_to_players, delay:float, decal:str, position:convert_to_vector, angle:convert_to_qangle, distance:float):
    effect129(decal, position, angle, distance).create(filter_, delay=delay)


@ESTCommand('Effect_30')
def effect130_command(command_info, filter_:convert_userid_identifier_to_players, delay:float, start:convert_to_vector, end:convert_to_vector):
    effect130(start, end).create(filter_, delay=delay)


@ESTCommand('Effect_31')
def effect131_command(command_info, filter_:convert_userid_identifier_to_players, delay:float, model:str, position:convert_to_vector, scale:float, frame_rate:int):
    effect131(model, position, scale, frame_rate).create(filter_, delay=delay)


@ESTCommand('Effect_32')
def effect132_command(command_info, filter_:convert_userid_identifier_to_players, delay:float, position:convert_to_vector, magnitude:int, trail_length:int, direction:convert_to_vector):
    effect132(position, magnitude, trail_length, direction).create(filter_, delay=delay)


@ESTCommand('Effect_33')
def effect133_command(command_info, filter_:convert_userid_identifier_to_players, delay:float, model:str, position:convert_to_vector, size:float, brightness:int):
    effect133(model, position, size, brightness).create(filter_, delay=delay)


@ESTCommand('Effect_34')
def effect134_command(command_info, filter_:convert_userid_identifier_to_players, delay:float, model:str, position:convert_to_vector, direction:convert_to_vector, speed:int, noise:float, count:int):
    effect134(model, position, direction, speed, noise, count).create(filter_, delay=delay)


@ESTCommand('Effect_35')
def effect135_command(command_info, filter_:convert_userid_identifier_to_players, delay:float, decal:str, position:convert_to_vector):
    effect135(decal, position).create(filter_, delay=delay)


@ESTCommand(['est_Effect', '1'])
def effect1_command(command_info, filter_:convert_userid_identifier_to_players, delay:float, model:str, x:float, y:float, z:float, dx:float, dy:float, dz:float):
    effect1(model, x, y, z, dx, dy, dz).create(filter_, delay=delay)


@ESTCommand(['est_Effect', '2'])
def effect2_command(command_info, filter_:convert_userid_identifier_to_players, delay:float, model:str, start_userid:valid_userid, end_userid:valid_userid, life_time:float, start_width:clamp(0, is_int=False), end_width:clamp(0, is_int=False), red:clamp(0, 255), green:clamp(0, 255), blue:clamp(0, 255), alpha:clamp(0, 255)):
    effect2(model, start_userid, end_userid, life_time, start_width, end_width, red, green, blue, alpha).create(filter_, delay=delay)


@ESTCommand(['est_Effect', '3'])
def effect3_command(command_info, filter_:convert_userid_identifier_to_players, delay:float, model:str, x1:float, y1:float, z1:float, x2:float, y2:float, z2:float, life_time:float, start_width:clamp(0, is_int=False), end_width:clamp(0, is_int=False), red:clamp(0, 255), green:clamp(0, 255), blue:clamp(0, 255), alpha:clamp(0, 255)):
    effect3(model, x1, y1, z1, x2, y2, z2, life_time, start_width, end_width, red, green, blue, alpha).create(filter_, delay=delay)


@ESTCommand(['est_Effect', '4'])
def effect4_command(command_info, filter_:convert_userid_identifier_to_players, delay:float, model:str, userid:valid_userid, life_time:float, start_width:clamp(0, is_int=False), end_width:clamp(0, is_int=False), fade_length:int, red:clamp(0, 255), green:clamp(0, 255), blue:clamp(0, 255), alpha:clamp(0, 255)):
    effect4(model, userid, life_time, start_width, end_width, fade_length, red, green, blue, alpha).create(filter_, delay=delay)


@ESTCommand(['est_Effect', '5'])
def effect5_command(command_info, filter_:convert_userid_identifier_to_players, delay:float, model:str, start_userid:valid_userid, end_entity_index:int, life_time:float, width:float, fade_length:int, amplitude:clamp(0, is_int=False), red:clamp(0, 255), green:clamp(0, 255), blue:clamp(0, 255), alpha:clamp(0, 255), speed:clamp(0)):
    effect5(model, start_userid, end_entity_index, life_time, width, fade_length, amplitude, red, green, blue, alpha, speed).create(filter_, delay=delay)


@ESTCommand(['est_Effect', '6'])
def effect6_command(command_info, filter_:convert_userid_identifier_to_players, delay:float, model:str, x:float, y:float, z:float, reversed_:int):
    effect6(model, x, y, z, reversed_).create(filter_, delay=delay)


@ESTCommand(['est_Effect', '7'])
def effect7_command(command_info, filter_:convert_userid_identifier_to_players, delay:float, model:str, x:float, y:float, z:float, scale:float, frame_rate:clamp(0)):
    effect7(model, x, y, z, scale, frame_rate).create(filter_, delay=delay)


@ESTCommand(['est_Effect', '8'])
def effect8_command(command_info, filter_:convert_userid_identifier_to_players, delay:float, model:str, x:float, y:float, z:float, dx:float, dy:float, dz:float):
    effect8(model, x, y, z, dx, dy, dz).create(filter_, delay=delay)


@ESTCommand(['est_Effect', '9'])
def effect9_command(command_info, filter_:convert_userid_identifier_to_players, delay:float, model:str, x:float, y:float, z:float, dx:float, dy:float, dz:float, type_:int):
    effect9(model, x, y, z, dx, dy, dz, type_).create(filter_, delay=delay)


@ESTCommand(['est_Effect', '10'])
def effect10_command(command_info, filter_:convert_userid_identifier_to_players, delay:float, model:str, x:float, y:float, z:float, start_radius:float, end_radius:float, life_time:float, width:float, fade_length:int, amplitude:clamp(0, is_int=False), red:clamp(0, 255), green:clamp(0, 255), blue:clamp(0, 255), alpha:clamp(0, 255), speed:clamp(0)):
    effect10(model, x, y, z, start_radius, end_radius, life_time, width, fade_length, amplitude, red, green, blue, alpha, speed).create(filter_, delay=delay)


@ESTCommand(['est_Effect', '11'])
def effect11_command(command_info, filter_:convert_userid_identifier_to_players, delay:float, model:str, x:float, y:float, z:float, life_time:float, scale:float, brightness:int):
    effect11(model, x, y, z, life_time, scale, brightness).create(filter_, delay=delay)


@ESTCommand(['est_Effect', '12'])
def effect12_command(command_info, filter_:convert_userid_identifier_to_players, delay:float, *args):
    effect12(*args).create(filter_, delay=delay)
