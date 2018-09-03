# ../wcs/core/helpers/esc/vars.py

# ============================================================================
# >> IMPORTS
# ============================================================================
# Source.Python Imports
#   CVars
from cvars import ConVar

# WCS Imports
#   Constants
from ...constants.paths import CFG_PATH


# ============================================================================
# >> ALL DECLARATION
# ============================================================================
__all__ = (
    'cvar_wcs_dices',
    'cvar_wcs_userid',
    'cvars',
)


# ============================================================================
# >> GLOBAL VARIABLES
# ============================================================================
cvar_wcs_dices = [ConVar(f'wcs_dice{i}', '0') for i in [''] + list(range(1, 10))]
cvar_wcs_userid = ConVar('wcs_userid', '0')
cvars = {}

# TODO: What am I even...
for variable in ('ex', 'vector1', 'vector2', 'wcs_x', 'wcs_y', 'wcs_z', 'wcs_x1', 'wcs_y1', 'wcs_z1', 'wcs_x2', 'wcs_y2', 'wcs_z2', 'wcs_x3', 'wcs_y3', 'wcs_z3',
                 'wcs_ultinotexec', 'wcs_health', 'wcs_divider', 'wcs_speed', 'wcs_gravity', 'wcs_chance', 'wcs_damage', 'wcs_dmg', 'wcs_tmp', 'wcs_tmp1', 'wcs_tmp2', 'wcs_tmp3',
                 'wcs_tmp4', 'wcs_tmp5', 'wcs_tmp6', 'wcs_tmp7', 'wcs_tmp8', 'wcs_tmp9', 'wcs_tmp10', 'wcs_tmp11', 'wcs_tmp12', 'wcs_tmp13', 'wcs_tmp14', 'wcs_tmp15','wcs_team',
                 'wcs_team2', 'wcs_gamecheck', 'wcs_phoenix', 'wcs_invis', 'wcs_addhealth', 'wcs_range', 'wcs_fadetimer', 'wcs_multiplier', 'wcs_maxtargets', 'wcs_radius',
                 'wcs_alive', 'wcs_freezetime', 'wcs_time', 'wcs_money', 'wcs_hpmana', 'wcs_shaketime', 'wcs_bonushp', 'wcs_jetpack', 'wcs_armor', 'wcs_player', 'wcs_dead',
                 'wcs_uid', 'wcs_lng', 'wcs_rand', 'wcs_wardencounter', 'wcs_trapcounter', 'wcs_healcounter', 'wcs_target', 'wcs_targetid', 'wcs_amount', 'wcs_maxhp', 'wcs_round',
                 'wcs_maxheal', 'wcs_roundcounter', 'wcs_type', 'wcs_removeid', 'wcs_fxtype', 'wcs_op', 'wcs_params', 'wcs_sucxp', 'wcs_skulls', 'wcs_skulls_amount', 'wcs_res_ui',
                 'wcs_res_type', 'wcs_res_wep', 'wcs_res_give', 'wcs_res_knife', 'wcs_res_wep_wep', 'wcs_choice', 'wcs_todo', 'wcs_name', 'wcs_mole', 'wcs_exists', 'wcs_smokestack_counter',
                 'wcs_duration', 'wcs_speed_var', 'wcs_magnitude'):
    cvars[variable] = ConVar(variable, '0')

if (CFG_PATH / 'var.txt').isfile():
    with open(CFG_PATH / 'var.txt') as inputfile:
        for variable in [x.strip() for x in inputfile.readlines() if not x.startswith('//') and x.strip()]:
            if variable not in cvars:
                cvars[variable] = ConVar(variable, '0')
else:
    with open(CFG_PATH / 'var.txt', 'w') as outputfile:
        outputfile.write('// Place all the server variables you want to set under here.\n')
        outputfile.write('// This is only necessary for ESS races.\n')
        outputfile.write('//\n')
        outputfile.write('// Lines with // in front of it will not be read.\n')
