#############################################################################
# Python Module: polsplitter_varFDTD_geometry.py
# Based on: Lumerical Example file: polsplitter_varFDTD_geometry.py
#
##############################################################################

import lumapi
import numpy as np


dev_params = {'wg01': 0.5e-6,
              'wg02': 0.5e-6,
              'spacing': 0.35e-6,
              'length': 5.0e-6,
              'in_offset': 0.0e-6,
              'polarization': ""}

size_x = dev_params['length']+2e-6
size_y = 4e-6

wg01_offset_y = dev_params['in_offset']

def y_branch_init_inTE(mode):
    y_branch_init_(mode)

    dev_params['polarization'] = "E sim (TE)"
    mode.select('varFDTD')
    mode.set('polarization', dev_params['polarization'])

    ## SOURCE
    mode.addmodesource()
    mode.set('direction', 'Forward')
    mode.set('injection axis', 'x-axis')
    # sim.set('polarization angle',0)
    mode.set('y', 0)
    mode.set("y span", size_y)
    mode.set('x', -size_x/2+0.5e-6)
    mode.set('center wavelength', 1550e-9)
    mode.set('wavelength span', 100e-9)
    mode.set('sim selection', 'fundamental sim')  # Can be set to 'fundamental sim' or 'user select'
    # sim.updatesourcemode(1)  # TE0
    mode.setresource("varFDTD",1,"processes","5")
    mode.setresource("varFDTD",1,"threads","4")

    # fom waveguide top

    mode.addpower()
    mode.set('name', 'fom')
    mode.set('monitor type', 'Linear Y')
    mode.set('x', size_x / 2 - 0.5e-6)
    mode.set('y', (dev_params['spacing']+dev_params['wg02'])/2)
    # sim.set('y span', size_y)
    mode.set('y span', 1e-6)
    mode.set('z', 0)

def y_branch_init_inTM(mode):
    y_branch_init_(mode)
    dev_params['polarization'] = "H sim (TM)"

    mode.select('varFDTD')
    mode.set('polarization', dev_params['polarization'])
    ## SOURCE
    mode.addmodesource()
    mode.set('direction', 'Forward')
    mode.set('injection axis', 'x-axis')
    # sim.set('polarization angle',0);
    mode.set('y', 0)
    mode.set("y span", size_y)
    mode.set('x', -size_x*0.45)
    mode.set('center wavelength', 1550e-9)
    mode.set('wavelength span', 100e-9)
    mode.set('sim selection', 'fundamental sim')
    # sim.updatesourcemode(1)  # TM
    
    mode.setresource("varFDTD", 1, "processes", "5")
    mode.setresource("varFDTD", 1, "threads", "4")

    # fom waveguide bottom

    mode.addpower()
    mode.set('name', 'fom')
    mode.set('monitor type', 'Linear Y')
    mode.set('x', size_x / 2 - 0.5e-6)
    mode.set('y', -(dev_params['spacing'] + dev_params['wg02']) / 2)
    mode.set('y span', 1e-6)
    mode.set('z', 0)

def y_branch_init_(mode):
    in_wg_width = dev_params['wg01']
    out_wg_width = dev_params['wg02']
    spacing = dev_params['spacing']
    wg01_offset_y = dev_params['in_offset']

    finer_mesh_size_x = dev_params['length']+1e-6
    finer_mesh_size_y = 5e-6
    mesh_x = 10e-9
    mesh_y = 10e-9

    mesh_accuracy = 4
    lam_c = 1.550e-6

    # Clear session
    mode.switchtolayout()
    mode.selectall()
    mode.delete()

    # Input Waveguides

    mode.addrect()
    mode.set('name', 'input wg')
    mode.set('x span', 3e-6)
    mode.set('y span', in_wg_width)
    mode.set('z span', 220e-9)
    mode.set('y', wg01_offset_y)
    mode.set('x', -(1.5e-6+dev_params['length']/2) - 0.05e-6)
    mode.set('z', 0)
    mode.set('material', 'Si (Silicon) - Palik')

    # Output Waveguides

    mode.addrect()
    mode.set('name', 'output wg top')
    mode.set('x span', 3e-6)
    mode.set('y span', out_wg_width)
    mode.set('z span', 220e-9)
    mode.set('y', (out_wg_width+spacing)/2)
    mode.set('x', 1.5e-6+dev_params['length']/2 + 0.05e-6)
    mode.set('z', 0)
    mode.set('material', 'Si (Silicon) - Palik')

    mode.addrect()
    mode.set('name', 'output wg bottom')
    mode.set('x span', 3e-6)
    mode.set('y span', out_wg_width)
    mode.set('z span', 220e-9)
    mode.set('y', -(out_wg_width+spacing)/2)
    mode.set('x', 1.5e-6+dev_params['length']/2)
    mode.set('z', 0)
    mode.set('material', 'Si (Silicon) - Palik')

    # Substrate
    mode.addrect()
    mode.set('name','sub')
    mode.set('x span',8e-6)
    mode.set('y span',8e-6)
    mode.set('z span',10e-6)
    mode.set('y',0)
    mode.set('x',0)
    mode.set('z',0)
    mode.set('material', 'SiO2 (Glass) - Palik')
    mode.set('override mesh order from material database', 1)
    mode.set('mesh order', 3)
    mode.set('alpha', 0.3)

    # varFDTD
    mode.addvarfdtd()
    mode.set('mesh accuracy', mesh_accuracy)
    mode.set('x min', -size_x/2)
    mode.set('x max', size_x/2)
    mode.set('y min', -size_y/2)
    mode.set('y max', size_y/2)
    mode.set('force symmetric y mesh', 1)
    # sim.set('y min bc','Anti-Symmetric'); #Can be set to symmetric to force the TE1
    mode.set('y min bc', 'PML')
    mode.set('z', 0)

    mode.set('effective index method', 'variational')
    mode.set('can optimize mesh algorithm for extruded structures', 1)
    mode.set('clamp values to physical material properties', 1)

    x_t = 0.3e-6+dev_params['length']/2
    y_t = dev_params['in_offset']
    mode.set('x0', -x_t)
    mode.set('y0', y_t)
    mode.set('number of test points', 4)
    mode.set('test points', np.array([[0, 0],[x_t, 0.4e-6], [x_t, -0.4e-6], [x_t, 0]]))

    # MESH IN OPTIMIZABLE REGION
    mode.addmesh()
    mode.set('x', 0)
    mode.set('x span',finer_mesh_size_x)
    mode.set('y', 0)
    mode.set('y span',finer_mesh_size_y)
    mode.set('dx', mesh_x)
    mode.set('dy', mesh_y)

    # OPTIMIZATION FIELDS MONITOR IN OPTIMIZABLE REGION

    mode.addpower()
    mode.set('name','opt_fields')
    mode.set('monitor type','2D Z-normal')
    mode.set('x', 0)
    mode.set('x span', finer_mesh_size_x)
    mode.set('y', 0)
    mode.set('y span', finer_mesh_size_y)
    mode.set('z', 0)


if __name__ == "__main__":
    mode = lumapi.MODE(hide=False)
    y_branch_init_(mode)
    input('Press Enter to escape...')

