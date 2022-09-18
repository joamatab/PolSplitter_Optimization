import numpy as np
import scipy as sp
import lumapi
import os
import matplotlib.pyplot as pp

from lumopt.utilities.wavelengths import Wavelengths
from lumopt.geometries.polygon import FunctionDefinedPolygon
from lumopt.utilities.materials import Material
from lumopt.figures_of_merit.modematch import ModeMatch
from lumopt.optimizers.generic_optimizers import ScipyOptimizers
from lumopt.optimizers.fixed_step_gradient_descent import FixedStepGradientDescent
from lumopt.optimization import Optimization
from lumapi import LumApiError
# Load Base simulation functions
from polsplitter_3DFDTD_geometry import y_branch_init_inTE, y_branch_init_inTM


class C: #Usefull class for colored output text in the console
    RED = '\033[31m'
    ENDC = '\033[m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'


PolSplitter_TE = y_branch_init_inTE
PolSplitter_TM = y_branch_init_inTM

# Save the project directory for the final figure export
project_directory = os.getcwd()
wavelengths = Wavelengths(start=1530.0e-9, stop=1570.0e-9, points=11)
num_points = 11
print("Wavelengths: %s"%wavelengths)

dev_params = {'wg01': 0.5e-6,
              'wg02': 0.5e-6,
              'spacing': 0.35e-6,
              'length': 5.0e-6,
              'in_offset': 0.0e-6,
              'polarization': ""}

wg01_offset_y = dev_params['in_offset']
wg02_offset_y = (dev_params['spacing'] + dev_params['wg02']) / 2

def plot_spliter(params):
    n_interpolation_points = 100

    pp.plot(initial_points_x, wg01_offset_y+params[0:int(params.size / 2)])
    pp.plot(initial_points_x, wg01_offset_y-params[int(params.size / 2)::])
    polygon_points = splitter(params)

    pp.plot(polygon_points[:, 0], polygon_points[:, 1])
    pp.show()

def splitter(params):
    # Both top and bottom y coordinates are provided as inputs, where the second half of the inout data is used for the
    # bottom boundary of the polygon. The coordinates for the bottom boundary need to be flipped vertically.
    # This is necessary to make sure that bounds are positive
    with open('./last_param.txt', "ab") as f:
        f.write(b"\n------------------------------------\n")
        np.savetxt(f, params)
    #print('\n params: ------- \n ', params)
    n_interpolation_points = 100
    #wg01_offset_y = dev_params['in_offset']
    #wg02_offset_y = (dev_params['spacing'] + dev_params['wg02']) / 2

    points_x1 = np.concatenate(([initial_points_x.min() - 0.05e-6], initial_points_x,
                                [(initial_points_x.max()) + 0.05e-6]))
    polygon_points_x1 = np.linspace(min(points_x1), max(points_x1), n_interpolation_points)

    # Top edge
    y1 = wg01_offset_y + dev_params['wg01'] / 2
    y2 = wg02_offset_y + dev_params['wg02'] / 2
    points_y1 = np.concatenate(([y1], wg01_offset_y+params[0:int(params.size / 2)], [y2]))
    interpolator = sp.interpolate.interp1d(points_x1, points_y1, kind='cubic')
    polygon_points_y1 = interpolator(polygon_points_x1)

    # Bottom edge
    y1 = wg01_offset_y - dev_params['wg01'] / 2
    y2 = -(wg02_offset_y + dev_params['wg02'] / 2)

    points_x2 = points_x1
    points_y2 = np.concatenate(([y1], wg01_offset_y-params[int(params.size / 2)::], [y2]))

    polygon_points_x2 = np.linspace(min(points_x2), max(points_x2), n_interpolation_points)
    interpolator = sp.interpolate.interp1d(points_x2, points_y2, kind='cubic')
    polygon_points_y2 = interpolator(polygon_points_x2)

    # Zip coordinates into a list of tuples, reflect and reorder. Need to be passed ordered in a CCW sense
    polygon_points_up = [(x, y) for x, y in zip(polygon_points_x1, polygon_points_y1)]
    polygon_points_down = [(x, y) for x, y in zip(polygon_points_x2, polygon_points_y2)]
    polygon_points = np.array(polygon_points_up[::-1] + polygon_points_down)

    return polygon_points

# Define the span and number of points
initial_points_x = np.linspace(-dev_params['length']/2, dev_params['length']/2, num_points)
initial_points_y1 = np.linspace(wg01_offset_y+dev_params['wg01']/2, (wg02_offset_y + dev_params['wg02']/2), initial_points_x.size) - wg01_offset_y
initial_points_y2 = -(np.linspace(wg01_offset_y-dev_params['wg01']/2,-(wg02_offset_y + dev_params['wg02']/2), initial_points_x.size) - wg01_offset_y)
initial_points_y = np.concatenate((initial_points_y1, initial_points_y2))

print("Initial points: ", initial_points_y)
# L-BFGS methods allows the parameters to be bound. These should enforce the optimization footprint defined in the setup
x = np.linspace(start=0, stop=1, num=initial_points_x.size)

bstr = dev_params['wg01']/2
bend = bstr + 2e-6 # dev_params['wg02']/2+wg02_offset_y

slope = 10.0*(bend-bstr)/1.0  # To create a smooth transition in the input

bound_min_top = np.array([0.05e-6]*x.size)
bound_max_top = np.minimum(x*slope+bstr, [bend+0.5e-6]*x.size)
# pp.plot(x, bound_max_top, x, bound_min_top)
print('Bounds at bottom max: ', -bound_max_top)
print('Bounds at bottom min: ', -bound_min_top)

# Bottom boundaries
bstr = dev_params['wg01']/2
bend = bstr + 2e-6
slope = 10.0*(bend-bstr)/1.0
bound_min_bot = np.array([0.05e-6]*x.size)
bound_max_bot = np.minimum(x*slope+bstr, [bend+0.5e-6]*x.size)
print('Bounds at bottom max: ', -bound_min_bot)
print('Bounds at bottom min: ', -bound_max_bot)

#pp.plot(x,-np.array(bound_max_bot),x,-np.array(bound_min_bot))
#pp.show()

# Group all boundaries
bound_max = np.concatenate((bound_max_top, bound_max_bot))
bound_min = np.concatenate((bound_min_top, bound_min_bot))
bounds = list(zip(bound_min, bound_max))

bounds = [(0.2e-6, 1.2e-6)] * initial_points_y.size

# Load from 2D results if available
try:
    prev_results = np.loadtxt('2D_parameters.txt')
    print(prev_results)
except:
    print("Couldn't find the file containing 2D optimization parameters. Starting with default parameters")
    prev_results = initial_points_y

plot_spliter(prev_results)

# Set device and cladding materials, as well as as device layer thickness
eps_in = Material(name='Si (Silicon) - Palik', mesh_order=2)
eps_out = Material(name='SiO2 (Glass) - Palik', mesh_order=3)
depth = 220.0e-9

# Initialize FunctionDefinedPolygon class
polygon = FunctionDefinedPolygon(func=splitter,
                                 initial_params=prev_results,
                                 bounds=bounds,
                                 z=0.0,
                                 depth=depth,
                                 eps_out=eps_out, eps_in=eps_in,
                                 edge_precision=5,
                                 dx=1.0e-9)


# Define figure of merit
fom1 = ModeMatch(monitor_name='fom',
                 mode_number='fundamental mode',    # TE mode in for vertical symmetric condition
                 direction='Forward',
                 target_T_fwd=lambda wl: np.ones(wl.size),
                 norm_p=1)
scaling_factor = 1.0e6

# optimizer_1 = ScipyOptimizers(max_iter=30,
#                               method='Nelder-Mead',
#                               scaling_factor = scaling_factor,
#                               pgtol = 1.0e-9,
#                               ftol=1.0e-6,
#                               #target_fom = 1.0,
#                               scale_initial_gradient_to=0.0
#                               )
#
# optimizer_2 = ScipyOptimizers(max_iter=30,
#                               method='Nelder-Mead', #'L-BFGS-B',
#                               scaling_factor = scaling_factor,
#                               pgtol=1.0e-5,
#                               ftol=1.0e-5,
#                               #target_fom = 1.0,
#                               #scale_initial_gradient_to=0.0
#                               )

optimizer_1 = FixedStepGradientDescent(max_dx=1e-8,
                                       max_iter=30,
                                       all_params_equal=False,
                                       noise_magnitude=0.0,
                                       scaling_factor = scaling_factor
                                       )

optimizer_2 = FixedStepGradientDescent(max_dx=1e-3,
                                       max_iter=30,
                                       all_params_equal=False,
                                       noise_magnitude=0.0,
                                       scaling_factor = scaling_factor
                                       )

opt1 = Optimization(base_script=PolSplitter_TE,
                    wavelengths=wavelengths,
                    fom=fom1,
                    geometry=polygon,
                    optimizer=optimizer_1,
                    use_var_fdtd=False,
                    hide_fdtd_cad=False,
                    use_deps=True,
                    plot_history=True,
                    store_all_simulations=False)

fom2 = ModeMatch(monitor_name='fom',
                 mode_number='fundamental mode',    # TM mode in for vertical asymmetric condition
                 direction='Forward',
                 target_T_fwd=lambda wl: np.ones(wl.size),
                 norm_p=1)



opt2 = Optimization(base_script=PolSplitter_TM,
                    wavelengths=wavelengths,
                    fom=fom2,
                    geometry=polygon,
                    optimizer=optimizer_2,
                    use_var_fdtd=False,
                    hide_fdtd_cad=False,
                    use_deps=True,
                    plot_history=False,
                    store_all_simulations=False)

opt = opt2 + opt1
results = opt.run()
print(results)

# #Save parameters to file
np.savetxt('../2D_parameters.txt', results[1])

# #Export generated structure
gds_export_script = str("")

with lumapi.FDTD(hide=False) as sim:
    try:
        print('Mode is FDTD = ', isinstance(sim, lumapi.FDTD))
        sim.cd(project_directory)
        y_branch_init_inTM(sim)
        sim.addpoly(vertices=splitter(prev_results))
        sim.set('x', 0.0)
        sim.set('y', 0.0)
        sim.set('z', 0.0)
        sim.set('z span', depth)
        sim.set('material', 'Si (Silicon) - Palik')
        # Run Export Script
        # TO DO
        input('Press Enter to escape...')
    except LumApiError as err:
        print(C.YELLOW +f"LumAPI Exception {err=}, {type(err)=}" + C.ENDC)
        sim.close()
        raise
    except BaseException as err:
        print(C.YELLOW +f"Unexpected {err=}, {type(err)=}"+ C.ENDC)
        sim.close()
        raise
