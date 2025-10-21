"""
Configuration of files to be read
"""
sims = ['GP20','GP20UNIT1Gpc']

def get_config(simtype, snap, laptop=False, verbose=False):
    """
    Get general configuration
    
    Parameters
    ----------
    simtype : str
        Simulation type (must be in sims list)
    snap : integer
        Snapshot number
    laptop : bool
        If True, use local test configuration
    verbose : bool
        If True, print further messages
    
    Returns
    -------
    config: dict
        Configuration dictionary
    """

    if simtype not in sims:
        raise ValueError(f"Simulation type '{simtype}' not supported. Available types: {sims}")
    
    if verbose:
        print(f"Getting configuration for simulation type: {simtype}")

    function_name = f'get_{simtype}_config'
    config_function = globals()[function_name]
    config = config_function(snap,laptop=laptop, verbose=verbose)
    return config


def get_GP20_config(snap, laptop=False, verbose=False):
    """
    Get configuration for GP20 runs
    
    Parameters
    ----------
    snap : integer
        Snapshot number
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
            'group': 'Output001',
            'datasets': ['mhhalo', 'xgal', 'ygal', 'zgal'],
            'units': ['Msun/h', 'Mpc/h', 'Mpc/h', 'Mpc/h'],
            'low_limits': [20 * config['mp'], 0., 0., 0.],
            'high_limits': [None, boxside, boxside, boxside]
        }
    }
    
    # File properties to extract
    config['file_props'] = {
        'galaxies.hdf5': {
            'group': 'Output001',
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
            'group': 'Output001',
            'datasets': ['Lbol_AGN'],
            'units': ['1e40 h^-2 erg/s']
        },
        'tosedfit.hdf5': {
            'group': 'Output001',
            'datasets': ['mag_UKIRT-K_o_tot_ext', 'mag_SDSSz0.1-r_o_tot_ext'],
            'units': ['AB', 'AB']
        }
    }
    
    return config


def get_GP20UNIT1Gpc_config(snap, laptop=False, verbose=False):
    """
    Get configuration for UNIT 1Gpc runs
    
    Parameters
    ----------
    snap : integer
        Snapshot number
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
    path = '/data2/users/olivia/galform_output/UNIT_PNG/UNIT_1GPC/'
    ending = 'iz'+str(snap)+'/ivol'
    outroot = '/home2/vgonzalez/Data/Galform/UNIT1GPC_fnl0/'+ending
    root = path+ending
    if laptop:
        root = '/home/violeta/buds/emlines/gp20data/iz'+str(snap)+'/ivol'  
        
    boxside = 30 #Mpc/h (whole volume 1000Mpc/h)
    
    config = {
        # Paths
        'root': root,
        'outroot': outroot,
        
        # Cosmology parameters
        'h0': 0.6773999929428101,
        'omega0': 0.30889999866485596,
        'omegab': 0.04859999939799309,
        'lambda0': 0.691100001335144,
        'boxside': boxside,
        'mp': 1.24718e9 ,  # Msun/h

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
            'group': 'Output001',
            'datasets': ['mhhalo', 'xgal', 'ygal', 'zgal'],
            'units': ['Msun/h', 'Mpc/h', 'Mpc/h', 'Mpc/h'],
            'low_limits': [20 * config['mp'], 0., 0., 0.],
            'high_limits': [None, boxside, boxside, boxside]
        }
    }
    
    # File properties to extract
    config['file_props'] = {
        'galaxies.hdf5': {
            'group': 'Output001',
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
            'group': 'Output001',
            'datasets': ['Lbol_AGN'],
            'units': ['1e40 h^-2 erg/s']
        },
        #'tosedfit.hdf5': {
        'samp_dust.hdf5': {
            'group': 'Output001',
            #'datasets': ['mag_UKIRT-K_o_tot_ext', 'mag_SDSSz0.1-r_o_tot_ext'],
            'datasets': ['mag_WISE-3.6_o_tot_ext', 'mag_SDSS-r_o_tot_ext'],
            'units': ['AB', 'AB']
        }
    }
    
    return config
