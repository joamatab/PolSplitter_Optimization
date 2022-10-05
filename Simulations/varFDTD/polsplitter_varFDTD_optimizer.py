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
from lumopt.optimization import Optimization


# Load Base simulation functions
from polsplitter_varFDTD_geometry import y_branch_init_inTE, y_branch_init_inTM

PolSplitter_TE = y_branch_init_inTE
PolSplitter_TM = y_branch_init_inTM

# Save the project directory for the final figure export
project_directory = os.getcwd()
wavelengths = Wavelengths(start=1500e-9, stop=1600e-9, points=21)
num_points = 11

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

    pp.plot(initial_points_x, wg01_offset_y + params[:int(params.size / 2)])
    pp.plot(initial_points_x, wg01_offset_y-params[int(params.size / 2)::])
    polygon_points = splitter(params)

    pp.plot(polygon_points[:, 0], polygon_points[:, 1])
    pp.show()

def splitter(params):
    # Both top and bottom y cooridinates are provided as inputs, where the second half of the inout data is used for the
    # bottom boundary of the polygon. The coordinates for the bottom boundary need to be flipped vertically.
    # This is necessary to make sure that bounds are positive
    np.savetxt('./last_param.txt', params)

    n_interpolation_points = 100
    #wg01_offset_y = dev_params['in_offset']
    #wg02_offset_y = (dev_params['spacing'] + dev_params['wg02']) / 2

    points_x1 = np.concatenate(([initial_points_x.min() - 0.05e-6], initial_points_x,
                                [(initial_points_x.max()) + 0.05e-6]))
    polygon_points_x1 = np.linspace(min(points_x1), max(points_x1), n_interpolation_points)

    # Top edge
    y1 = wg01_offset_y + dev_params['wg01'] / 2
    y2 = wg02_offset_y + dev_params['wg02'] / 2
    points_y1 = np.concatenate(
        ([y1], wg01_offset_y + params[: int(params.size / 2)], [y2])
    )

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
    polygon_points_up = list(zip(polygon_points_x1, polygon_points_y1))
    polygon_points_down = list(zip(polygon_points_x2, polygon_points_y2))
    return np.array(polygon_points_up[::-1] + polygon_points_down)


# Define the span and number of points
initial_points_x = np.linspace(-dev_params['length']/2, dev_params['length']/2, num_points)
initial_points_y1 = np.linspace(wg01_offset_y+dev_params['wg01']/2, (wg02_offset_y + dev_params['wg02']/2), initial_points_x.size) - wg01_offset_y
initial_points_y2 = -(np.linspace(wg01_offset_y-dev_params['wg01']/2,-(wg02_offset_y + dev_params['wg02']/2), initial_points_x.size) - wg01_offset_y)
initial_points_y = np.concatenate((initial_points_y1, initial_points_y2))

print("Initial points: ", initial_points_y)
# L-BFGS methods allows the parameters to be bound. These should enforce the optimization footprint defined in the setup
x = np.linspace(start=0, stop=1, num=initial_points_x.size)

# Top boundaries
finer_mesh_size_y = 5e-6

bstr = dev_params['wg01']/2
bend = bstr + 2e-6 # dev_params['wg02']/2+wg02_offset_y

slope = 10.0*(bend-bstr)/1.0  # To create a smooth transition in the input

bound_min_top = np.array([0.05e-6]*x.size)
bound_max_top = np.minimum(x*slope+bstr, [bend+1.5e-6]*x.size)
# pp.plot(x, bound_max_top, x, bound_min_top)
print('Bounds at bottom max: ', -bound_max_top)
print('Bounds at bottom min: ', -bound_min_top)

# Bottom boundaries
bstr = dev_params['wg01']/2
bend = bstr + 2e-6
slope = 10.0*(bend-bstr)/1.0
bound_min_bot = np.array([0.05e-6]*x.size)
bound_max_bot = np.minimum(x*slope+bstr, [bend+1.5e-6]*x.size)
print('Bounds at bottom max: ', -bound_min_bot)
print('Bounds at bottom min: ', -bound_max_bot)

#pp.plot(x,-np.array(bound_max_bot),x,-np.array(bound_min_bot))
#pp.show()

# Group all boundaries
bound_max = np.concatenate((bound_max_top, bound_max_bot))
bound_min = np.concatenate((bound_min_top, bound_min_bot))
bounds = list(zip(bound_min, bound_max))

# bounds = [(0.5e-6, 1.8e-6)] * initial_points_y.size

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
                 mode_number='fundamental mode',    # TE mode in phase
                 direction='Forward',
                 target_T_fwd=lambda wl: np.ones(wl.size),
                 norm_p=1)

optimizer_1 = ScipyOptimizers(max_iter=30,
                              method='L-BFGS-B',
                              # scaling_factor = scaling_factor,
                              pgtol=1.0e-4,
                              ftol=1.0e-4,
                              # target_fom = 0.0,
                              scale_initial_gradient_to=0.0)

opt1 = Optimization(base_script=PolSplitter_TE,
                    wavelengths=wavelengths,
                    fom=fom1,
                    geometry=polygon,
                    optimizer=optimizer_1,
                    use_var_fdtd=True,
                    hide_fdtd_cad=False,
                    use_deps=True,
                    plot_history=True,
                    store_all_simulations=False)
                   

fom2 = ModeMatch(monitor_name='fom',
                 mode_number='fundamental mode',    #
                 direction='Forward',
                 target_T_fwd=lambda wl: np.ones(wl.size),
                 norm_p=1)

optimizer_2 = ScipyOptimizers(max_iter=30,
                              method='L-BFGS-B',
                              # scaling_factor = scaling_factor,
                              pgtol=1.0e-4,
                              ftol=1.0e-4,
                              # target_fom = 0.0,
                              scale_initial_gradient_to=0.0)

opt2 = Optimization(base_script=PolSplitter_TM,
                    wavelengths=wavelengths,
                    fom=fom2,
                    geometry=polygon,
                    optimizer=optimizer_2,
                    use_var_fdtd=True,
                    hide_fdtd_cad=False,
                    use_deps=True,
                    plot_history=True,
                    store_all_simulations=False)

opt = opt1 + opt2
results = opt.run()
print(results)

# Save parameters to file
np.savetxt('../2D_parameters.txt', results[1])

# Export generated structure
#gds_export_script = str("")

# with lumapi.MODE(hide=False) as mode:
#     mode.cd(project_directory)
#     y_branch_init_inTE(mode)
#     mode.addpoly(vertices=splitter(results[1]))
#     mode.set('x', 0.0)
#     mode.set('y', 0.0)
#     mode.set('z', 0.0)
#     mode.set('z span', depth)
#     mode.set('material', 'Si (Silicon) - Palik')
#     mode.save("y_branch_2D_FINAL")
#     # mode.eval(gds_export_script)
