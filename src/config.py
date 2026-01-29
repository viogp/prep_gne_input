"""
Configuration of files to be read
"""
import src.utils as u
import numpy as np

sims = ['GP20cosma','GP20SU','GP20UNIT1Gpc'] 

def get_config(sim, snap, subvols, laptop=False, verbose=False):
    """
    Get general configuration
    
    Parameters
    ----------
    sim : str
        Simulation type
    snap : integer
        Snapshot number
    subvols : list of integers
        List of subvolumes to be considered
    laptop : bool
        If True, use local test configuration
    verbose : bool
        If True, print further messages
    
    Returns
    -------
    config: dict
        Configuration dictionary
    """
    simtype = sim
    if simtype not in sims:
        raise ValueError(f"Simulation type '{simtype}' not supported. Available types: {sims}")
    
    if verbose:
        print(f"Getting configuration for simulation type: {simtype}")

    function_name = f'get_{simtype}_config'
    config_function = globals()[function_name]
    config = config_function(snap, subvols, laptop=laptop, verbose=verbose)
    return config


def get_GP20cosma_config(snap, subvols, laptop=False, verbose=False):
    """
    Get configuration for GP20 runs
    
    Parameters
    ----------
    snap : integer
        Snapshot number
    subvols : list of integers
        List of subvolumes to be considered
    laptop : bool, optional
        If True, use local test configuration
    verbose : bool, optional
        If True, print further messages
    
    Returns
    -------
    config: dict
        Configuration dictionary
    """
    # Path to files
    path = '/cosma5/data/durham/dc-gonz3/Galform_Out/v2.7.0/stable/MillGas/gp19/'
    ending = 'iz'+str(snap)+'/ivol'
    outroot = path+ending
    if laptop:
        outroot = '/home/violeta/buds/emlines/gp20data/iz'+str(snap)+'/ivol'
    root = outroot
        
    boxside = 125 #Mpc/h (whole volume 500Mpc/h)
    
    config = {
        # Paths
        'root': root,
        'outroot': outroot,
        
        # Cosmology parameters
        'h0': 0.704,
        'omega0': 0.307,
        'omegab': 0.0482,
        'lambda0': 0.693,
        'boxside': boxside,
        'mp': 9.35e8,  # Msun/h

        # Metallicity calculation parameters
        'mcold_disc': 'mcold',
        'mcold_z_disc': 'cold_metal',
        'mcold_burst': 'mcold_burst',
        'mcold_z_burst': 'metals_burst',
    }
    config['snap'] = snap
    
    # File selection criteria
    config['selection'] = {
        'galaxies.hdf5': {
            'group': 'Output###',
            'datasets': ['mhhalo', 'xgal', 'ygal', 'zgal'],
            'units': ['Msun/h', 'Mpc/h', 'Mpc/h', 'Mpc/h'],
            'low_limits': [20 * config['mp'], 0., 0., 0.],
            'high_limits': [None, boxside, boxside, boxside]
        }
    }


    # Define the lines and luminosity names
    config['lines'] = ['Halpha', 'Hbeta', 'NII6583', 'OII3727', 'OIII5007', 'SII6716']
    config['line_prefix'] = 'L_tot_'
    config['line_suffix_ext'] = '_ext'

    line_datasets = []
    for line in config['lines']:
        line_datasets.append(f"{config['line_prefix']}{line}")
        line_datasets.append(f"{config['line_prefix']}{line}{config['line_suffix_ext']}")

    # File properties to extract
    config['file_props'] = {
        'galaxies.hdf5': {
            'group': 'Output###',
            'datasets': ['redshift', 'index', 'type',
                         'vxgal', 'vygal', 'vzgal',
                         'rbulge', 'rcomb', 'rdisk', 'mhot', 'vbulge',
                         'mcold', 'mcold_burst', 'cold_metal', 'metals_burst',
                         'mstars_bulge', 'mstars_burst', 'mstars_disk',
                         'mstardot', 'mstardot_burst', 'mstardot_average',
                         'M_SMBH', 'SMBH_Mdot_hh', 'SMBH_Mdot_stb', 'SMBH_Spin'],
            'units': ['redshift', 'Host halo index', 'Gal. type (central=0)',
                      'km/s','km/s','km/s',
                      'Mpc/h', 'Mpc/h', 'Mpc/h', 'Msun/h', 'km/s',
                      'Msun/h', 'Msun/h', 'Msun/h', 'Msun/h',
                      'Msun/h', 'Msun/h', 'Msun/h',
                      'Msun/h/Gyr', 'Msun/h/Gyr', 'Msun/h/Gyr',
                      'Msun/h', 'Msun/h/Gyr', 'Msun/h/Gyr', 'Spin']
        },
        'agn.hdf5': {
            'group': 'Output###',
            'datasets': ['Lbol_AGN'],
            'units': ['1e40 h^-2 erg/s']
        },
        'tosedfit.hdf5': {
            'group': 'Output###',
            'datasets': ['mag_UKIRT-K_o_tot_ext', 'mag_SDSSz0.1-r_o_tot_ext'] + line_datasets,
            'units': ['AB apparent'] * 2 + ['1e40 h^2 erg/s'] * len(line_datasets)
        }
    } 
    return config


def get_GP20SU_config(snap, subvols, laptop=False, verbose=False):
    """
    Get configuration for GP20 runs
    
    Parameters
    ----------
    snap : integer
        Snapshot number
    subvols : list of integers
        List of subvolumes to be considered
    laptop : bool, optional
        If True, use local test configuration
    verbose : bool, optional
        If True, print further messages
    
    Returns
    -------
    config: dict
        Configuration dictionary
    """
    # Path to files
    ln_As = 3.064
    # SU1 ----------------------------
    outpath = '/home2/vgonzalez/Data/Galform/SU1/'
    path = '/data2/users/olivia/galform_output/SU1/SU1_z_tests/'
    #path = '/data2/users/olivia/galform_output/SU1/SU1_250MPC_np_corrected/'
    ## SU2 ----------------------------
    #ln_As = ln_As + np.log(1.05)
    #outpath = '/home2/vgonzalez/Data/Galform/SU2/'
    #path = '/data2/users/olivia/galform_output/SU2/SU2_z_tests/'
    ##path = '/data2/users/olivia/galform_output/SU2/SU2_250MPC_np_corrected/'
    # ----------------------------
    ending = 'iz'+str(snap)
    root = path+'ivol'
    outroot = outpath+ending+'/ivol'

    boxside = 250 #Mpc/h

    # Runs with several z output, need to find out group name
    group = u.get_group_name(root,snap,subvols)
    
    config = {
        # Paths
        'root': root,
        'outroot': outroot,
        'ending': ending,
        'except_file': 'galaxies.hdf5',
        
        # Cosmology parameters
        'h0': 0.6774,
        'omega0': 0.3089,
        'omegab': 0.0486,
        'lambda0': 0.6911,
        'boxside': boxside,
        'mp': 1.558975e8,  # Msun/h
        'ln_As' : ln_As,  
        
        # Metallicity calculation parameters
        'mcold_disc': 'mcold',
        'mcold_z_disc': 'cold_metal',
        'mcold_burst': 'mcold_burst',
        'mcold_z_burst': 'metals_burst',
    }
    config['snap'] = snap
    
    # File selection criteria
    config['selection'] = {
        'galaxies.hdf5': {
            'group': group,
            'datasets': ['mhhalo'],
            'units': ['Msun/h'],
            'low_limits': [20 * config['mp']],
            'high_limits': [None]
        }
    }

    # Define the lines and luminosity names
    config['lines'] = ['Halpha', 'Hbeta', 'NII6583', 'OII3727', 'OIII5007', 'SII6716']
    config['line_prefix'] = 'L_tot_'
    config['line_suffix_ext'] = '_ext'

    line_datasets = []
    for line in config['lines']:
        line_datasets.append(f"{config['line_prefix']}{line}")
        line_datasets.append(f"{config['line_prefix']}{line}{config['line_suffix_ext']}")

    # File properties to extract
    config['file_props'] = {
        'galaxies.hdf5': {
            'group': group,
            'datasets': ['redshift', 'index', 'type',
                         'vxgal', 'vygal', 'vzgal',
                         'rbulge', 'rcomb', 'rdisk', 'mhot', 'vbulge',
                         'mcold', 'mcold_burst', 'cold_metal', 'metals_burst',
                         'mstars_bulge', 'mstars_burst', 'mstars_disk',
                         'mstardot', 'mstardot_burst', 'mstardot_average',
                         'M_SMBH', 'SMBH_Mdot_hh', 'SMBH_Mdot_stb', 'SMBH_Spin'],
            'units': ['redshift', 'Host halo index', 'Gal. type (central=0)',
                      'km/s','km/s','km/s',
                      'Mpc/h', 'Mpc/h', 'Mpc/h', 'Msun/h', 'km/s',
                      'Msun/h', 'Msun/h', 'Msun/h', 'Msun/h',
                      'Msun/h', 'Msun/h', 'Msun/h',
                      'Msun/h/Gyr', 'Msun/h/Gyr', 'Msun/h/Gyr',
                      'Msun/h', 'Msun/h/Gyr', 'Msun/h/Gyr', 'Spin']
        },
        'agn.hdf5': {
            'group': group,
            'datasets': ['Lbol_AGN'],
            'units': ['1e40 h^-2 erg/s']
        },
        'tosedfit.hdf5': {
            'group': group,
            'datasets': ['mag_UKIRT-K_o_tot_ext', 'mag_SDSSz0.1-r_o_tot_ext'],
            'units': ['AB apparent'] * 2
        },
        'elgs.hdf5': {
            'group': group,
            'datasets': line_datasets,
            'units': ['1e40 h^2 erg/s'] * len(line_datasets)
        }
    } 
    return config



def get_GP20UNIT1Gpc_config(snap, subvols, laptop=False, verbose=False):
    """
    Get configuration for GP20 runs on the UNIT 1 Gpc/h simulation
    
    Parameters
    ----------
    snap : integer
        Snapshot number
    subvols : list of integers
        List of subvolumes to be considered
    laptop : bool, optional
        If True, use local test configuration
    verbose : bool, optional
        If True, print further messages
    
    Returns
    -------
    config: dict
        Configuration dictionary
    """
    # Path to files
    # ----------------------------
    fnl = 0
    outpath = '/home2/vgonzalez/Data/Galform/UNIT1GPC_fnl0/'
    path = '/data2/users/olivia/galform_output/UNIT_PNG/LRG_1_and_3/'
    #path = '/data2/users/olivia/galform_output/UNIT_PNG/UNIT_1GPC/'
    # ----------------------------
    fnl = 100
    outpath = '/home2/vgonzalez/Data/Galform/UNIT1GPC_fnl100/'
    path = '/data2/users/olivia/galform_output/UNIT_PNG100/UNITPNG100_1GPC/'
    # ----------------------------
    ending = 'iz'+str(snap)
    root = path+'ivol'
    outroot = outpath+ending+'/ivol'

    boxside = 1000 #Mpc/h

    # Runs with several z output, need to find out group name
    group = u.get_group_name(root,snap,subvols)
    
    config = {
        # Paths
        'root': root,
        'outroot': outroot,
        'ending': ending,
        'except_file': 'galaxies.hdf5',
        
        # Cosmology parameters
        'h0': 0.6774,
        'omega0': 0.3089,
        'omegab': 0.0486,
        'lambda0': 0.6911,
        'boxside': boxside,
        'mp': 1.24718e9,  # Msun/h
        'fnl' : fnl,  
        
        # Metallicity calculation parameters
        'mcold_disc': 'mcold',
        'mcold_z_disc': 'cold_metal',
        'mcold_burst': 'mcold_burst',
        'mcold_z_burst': 'metals_burst',
    }
    config['snap'] = snap
    
    # File selection criteria
    config['selection'] = {
        'galaxies.hdf5': {
            'group': group,
            'datasets': ['mhhalo'],
            'units': ['Msun/h'],
            'low_limits': [20 * config['mp']],
            'high_limits': [None]
        }
    }

    # Define the lines and luminosity names
    config['lines'] = ['Halpha', 'Hbeta', 'NII6583', 'OII3727', 'OIII5007', 'SII6716']
    config['line_prefix'] = 'L_tot_'
    config['line_suffix_ext'] = '_ext'

    line_datasets = []
    for line in config['lines']:
        line_datasets.append(f"{config['line_prefix']}{line}")
        line_datasets.append(f"{config['line_prefix']}{line}{config['line_suffix_ext']}")

    # File properties to extract
    config['file_props'] = {
        'galaxies.hdf5': {
            'group': group,
            'datasets': ['redshift', 'index', 'type',
                         'vxgal', 'vygal', 'vzgal',
                         'rbulge', 'rcomb', 'rdisk', 'mhot', 'vbulge',
                         'mcold', 'mcold_burst', 'cold_metal', 'metals_burst',
                         'mstars_bulge', 'mstars_burst', 'mstars_disk',
                         'mstardot', 'mstardot_burst', 'mstardot_average',
                         'M_SMBH', 'SMBH_Mdot_hh', 'SMBH_Mdot_stb', 'SMBH_Spin'],
            'units': ['redshift', 'Host halo index', 'Gal. type (central=0)',
                      'km/s','km/s','km/s',
                      'Mpc/h', 'Mpc/h', 'Mpc/h', 'Msun/h', 'km/s',
                      'Msun/h', 'Msun/h', 'Msun/h', 'Msun/h',
                      'Msun/h', 'Msun/h', 'Msun/h',
                      'Msun/h/Gyr', 'Msun/h/Gyr', 'Msun/h/Gyr',
                      'Msun/h', 'Msun/h/Gyr', 'Msun/h/Gyr', 'Spin']
        },
        'agn.hdf5': {
            'group': group,
            'datasets': ['Lbol_AGN'],
            'units': ['1e40 h^-2 erg/s']
        },
        'tosedfit.hdf5': {
            'group': group,
            'datasets': ['mag_UKIRT-K_o_tot_ext', 'mag_SDSSz0.1-r_o_tot_ext'],
            'units': ['AB apparent'] * 2
        },
        'elgs.hdf5': {
            'group': group,
            'datasets': line_datasets,
            'units': ['1e40 h^2 erg/s'] * len(line_datasets)
        }
    } 
    return config


