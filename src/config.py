"""
Configuration of files to be read
"""
sims = ['GP20']

def get_config(simtype, snap, localtest=False, verbose=False):
    """
    Get general configuration
    
    Parameters
    ----------
    simtype : str
        Simulation type (must be in sims list)
    snap : integer
        Snapshot number
    localtest : bool
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
    config = config_function(simtype, snap,
                             localtest=localtest, verbose=verbose)
    return config


def get_GP20_config(simtype, snap, laptop=False, verbose=False):
    """
    Get configuration for GP20 runs
    
    Parameters
    ----------
    simtype : str
        Simulation type (should be 'GP20')
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
    root = path+'iz'+str(snap)+'/ivol'
    if laptop:
        root = '/home/violeta/buds/emlines/gp20data/iz'+str(snap)+'/ivol'

    config = {
        # Paths
        'root': root,
        
        # Cosmology parameters
        'h0': 0.704,
        'omega0': 0.307,
        'omegab': 0.0482,
        'lambda0': 0.693,
        'boxside': 500.0,  # Mpc/h
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
            'high_limits': [None, 125., 125., 125.]
        }
    }
    
    # File properties to extract
    config['file_props'] = {
        'galaxies.hdf5': {
            'group': 'Output001',
            'datasets': ['redshift', 'index', 'type',
                         'rbulge', 'rcomb', 'rdisk', 'mhot', 'vbulge',
                         'mcold', 'mcold_burst', 'cold_metal', 'metals_burst',
                         'mstars_bulge', 'mstars_burst', 'mstars_disk',
                         'mstardot', 'mstardot_burst', 'mstardot_average',
                         'M_SMBH', 'SMBH_Mdot_hh', 'SMBH_Mdot_stb', 'SMBH_Spin'],
            'units': ['redshift', 'Host halo index', 'Gal. type (central=0)',
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
