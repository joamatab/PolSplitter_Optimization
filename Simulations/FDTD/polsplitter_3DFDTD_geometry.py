#############################################################################
# Python Module: polsplitter_3DFDTD_geometry.py
# Based on: Lumerical Example file:
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

size_x = dev_params['length'] + 2e-6
size_y = 4e-6
size_z = 2e-6

finer_mesh_size_x = dev_params['length']+0.0e-6
finer_mesh_size_y = 2e-6
finer_mesh_size_z = 0.4e-6

wg01_offset_y = dev_params['in_offset']

def y_branch_init_inTE(sim):
    y_branch_init_(sim)

    dev_params['polarization'] = "E mode (TE)"
    sim.select('FDTD')
    sim.set('z min bc', 'Symmetric')
    #sim.set('polarization', dev_params['polarization'])

    # fom waveguide top
    sim.addpower()
    sim.set('name', 'fom')
    sim.set('monitor type','2D X-Normal');
    sim.set('x', size_x / 2 - 0.5e-6)
    sim.set('y', (dev_params['spacing'] + dev_params['wg02']) / 2)
    # sim.set('y span', size_y)
    sim.set('y span', 1e-6)
    sim.set('z', 0)
    sim.set('z span', finer_mesh_size_z)

def y_branch_init_inTM(sim):
    y_branch_init_(sim)
    dev_params['polarization'] = "H mode (TM)"

    sim.select('FDTD')
    sim.set('z min bc', 'Anti-Symmetric')
    #sim.set('polarization', dev_params['polarization'])

    # fom waveguide bottom
    sim.addpower()
    sim.set('name', 'fom')
    sim.set('monitor type','2D X-Normal');
    sim.set('x', size_x / 2 - 0.5e-6)
    sim.set('y', -(dev_params['spacing'] + dev_params['wg02']) / 2)
    sim.set('y span', 1e-6)
    sim.set('z', 0)
    sim.set('z span', finer_mesh_size_z);

def y_branch_init_(sim):
    in_wg_width = dev_params['wg01']
    out_wg_width = dev_params['wg02']
    spacing = dev_params['spacing']
    wg01_offset_y = dev_params['in_offset']


    mesh_x = 10e-9
    mesh_y = 10e-9
    mesh_z = 10e-9

    mesh_accuracy = 3
    lam_c = 1.550e-6

    # Clear session
    sim.switchtolayout()
    sim.selectall()
    sim.delete()
    
    # Input Waveguides
    
    sim.addrect()
    sim.set('name', 'input wg')
    sim.set('x span', 3e-6)
    sim.set('y span', in_wg_width)
    sim.set('z span', 220e-9)
    sim.set('y', wg01_offset_y)
    sim.set('x', -(1.5e-6 + dev_params['length'] / 2) - 0.05e-6)
    sim.set('z', 0)
    sim.set('material', 'Si (Silicon) - Palik')
    
    # Output Waveguides
    
    sim.addrect()
    sim.set('name', 'output wg top')
    sim.set('x span', 3e-6)
    sim.set('y span', out_wg_width)
    sim.set('z span', 220e-9)
    sim.set('y', (out_wg_width + spacing) / 2)
    sim.set('x', 1.5e-6 + dev_params['length'] / 2)
    sim.set('z', 0)
    sim.set('material', 'Si (Silicon) - Palik')
    
    sim.addrect()
    sim.set('name', 'output wg bottom')
    sim.set('x span', 3e-6)
    sim.set('y span', out_wg_width)
    sim.set('z span', 220e-9)
    sim.set('y', -(out_wg_width + spacing) / 2)
    sim.set('x', 1.5e-6 + dev_params['length'] / 2)
    sim.set('z', 0)
    sim.set('material', 'Si (Silicon) - Palik')

    # Substrate
    sim.addrect()
    sim.set('name', 'sub')
    sim.set('x span', 8e-6)
    sim.set('y span', 8e-6)
    sim.set('z span', 10e-6)
    sim.set('y', 0)
    sim.set('x', 0)
    sim.set('z', 0)
    sim.set('material', 'SiO2 (Glass) - Palik')
    sim.set('override mesh order from material database', 1)
    sim.set('mesh order', 3)
    sim.set('alpha', 0.3)
    
    # 3D FDTD solver
    sim.addfdtd()
    sim.set('mesh accuracy', mesh_accuracy)
    sim.set('x min', -size_x / 2)
    sim.set('x max',  size_x / 2)
    sim.set('y min', -size_y / 2)
    sim.set('y max',  size_y / 2)
    sim.set('force symmetric y mesh', 1)
    # sim.set('y min bc','Anti-Symmetric'); #Can be set to symmetric to force the TE1
    sim.set('y min bc', 'PML')
    sim.set('z', 0)
    

    x_t = 0.3e-6 + dev_params['length']/2
    y_t = dev_params['in_offset']

    # MESH IN OPTIMIZABLE REGION
    sim.addmesh()
    sim.set('x', 0)
    sim.set('x span', finer_mesh_size_x)
    sim.set('y', 0)
    sim.set('y span', finer_mesh_size_y)
    sim.set('z', 0)
    sim.set('z span', finer_mesh_size_z)
    sim.set('dx', mesh_x)
    sim.set('dy', mesh_y)
    sim.set('dy', mesh_z)
    
    # OPTIMIZATION FIELDS MONITOR IN OPTIMIZABLE REGION
    
    sim.addpower()
    sim.set('name', 'opt_fields')
    sim.set('monitor type', '2D Z-normal')
    sim.set('x', 0)
    sim.set('x span', finer_mesh_size_x)
    sim.set('y', 0)
    sim.set('y span', finer_mesh_size_y)
    sim.set('z', 0)

    ## SOURCE
    # The fundamental mode is enforced by the symmetry boundary conditions, so we can have
    # a generic mode source to test both TE and TM states.

    sim.addmode()
    sim.set('direction', 'Forward')
    sim.set('injection axis', 'x-axis')
    # sim.set('polarization angle',0)
    sim.set('y', 0)
    sim.set("y span", size_y)
    sim.set('x', -size_x / 2 + 0.5e-6)
    sim.set('center wavelength', 1550e-9)
    sim.set('wavelength span', 100e-9)
    sim.set('mode selection', 'fundamental mode')  # Can be set to 'fundamental mode', 'fundamental TE(M) mode' or 'user select'

    sim.setresource("FDTD", 1, "processes", "8")
    sim.setresource("FDTD", 1, "threads", "4")

if __name__ == "__main__":
    mode = lumapi.FDTD(hide=False)
    y_branch_init_(mode)
    input('Press Enter to escape...')

