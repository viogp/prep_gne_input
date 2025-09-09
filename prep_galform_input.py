"""
.. moduleauthor:: Violeta Gonzalez-Perez <violetagp@protonmail.com>

Program to prepare input files from hdf5 files
"""
import h5py
import sys
import numpy as np
import re

import src.utils as u

verbose = True
localtest = True

GP20runs = True
if GP20runs:
    # Path to files
    path = '/cosma5/data/durham/dc-gonz3/Galform_Out/v2.7.0/stable/MillGas/gp19/'
    root = path+'/iz39/ivol'
    subvols = list(range(64))
    if localtest:
        root = '/home/violeta/buds/emlines/gp20data/iz39/ivol'
        subvols = list(range(2))

    # Cosmology and volume of the simulation
    h0     = 0.704
    omega0 = 0.307
    omegab = 0.0482
    lambda0= 0.693
    boxside= 500. #Mpc/h
    mp     = 9.35e8 #Msun/h

    # For the calculation of metallicities
    mcold_disc = 'mcold'    
    mcold_z_disc = 'cold_metal'
    mcold_burst = 'mcold_burst'    
    mcold_z_burst = 'metals_burst'

    # Get snapshop from path
    match = re.search(r'iz(\d+)', root)
    if match:
        snap = int(match.group(1))
    else:
        print('WARNING: No snapnum found in root ',root)
    
    # Define the files and their corresponding properties
    selection = {
        'galaxies.hdf5': {
            'group': 'Output001',
            'datasets': ['mhhalo','xgal','ygal','zgal'],
            'units' : ['Msun/h','Mpc/h','Mpc/h','Mpc/h'],
            'low_limits' : [20*mp,0.,0.,0.],
            'high_limits' : [None,125.,125.,125.]
            }
        }
    file_props = {
        'galaxies.hdf5': {
            'group': 'Output001',
            'datasets': ['redshift','index','type',
                         'rbulge','rcomb','rdisk','mhot','vbulge',
                         'mcold','mcold_burst','cold_metal','metals_burst',
                         'mstars_bulge','mstars_burst','mstars_disk',
                         'mstardot','mstardot_burst','mstardot_average',
                         'M_SMBH','SMBH_Mdot_hh','SMBH_Mdot_stb','SMBH_Spin'],
            'units': ['redshift','Host halo index','Gal. type (central=0)',
                      'Mpc/h','Mpc/h','Mpc/h','Msun/h','km/s',
                      'Msun/h','Msun/h','Msun/h','Msun/h',
                      'Msun/h','Msun/h','Msun/h',
                      'Msun/h/Gyr','Msun/h/Gyr','Msun/h/Gyr',
                      'Msun/h','Msun/h/Gyr','Msun/h/Gyr','Spin']
        },
        'agn.hdf5': {
            'group': 'Output001', 
            'datasets': ['Lbol_AGN'],
            'units': ['1e40 h^-2 erg/s']
        },
        'tosedfit.hdf5': {
            'group': 'Output001',
            'datasets': ['mag_UKIRT-K_o_tot_ext', 'mag_SDSSz0.1-r_o_tot_ext'],
            'units': ['AB','AB']
        }
    }

# Validate that all the files have the expected structure
count_fails = 0
for ivol in subvols:
    path = root+str(subvols[ivol])+'/'

    if selection is None:
        allfiles = file_props
    else:
        allfiles = {**selection, **file_props}

    for ifile, props in allfiles.items():
        datasets = props['datasets']
        group = props.get('group')
        structure_ok = u.check_h5_structure(path+ifile,datasets,group=group)
        if not structure_ok:
            count_fails += 1
if count_fails>0:
    print(f"  STOP: Found {count_fails} problems.")
    sys.exit(1)

# Loop over each subvolume
for ivol in subvols:
    path = root+str(subvols[ivol])+'/'

    # Generate a header for the output file
    outfile = path+'gne_input.hdf5'
    print(f' * Generating file: {outfile}')
    
    hf = h5py.File(outfile, 'w')
    headnom = 'header'
    head = hf.create_dataset(headnom,())
    head.attrs[u'h0'] = h0
    head.attrs[u'omega0'] = omega0
    head.attrs[u'omegab'] = omegab
    head.attrs[u'lambda0'] = lambda0
    head.attrs[u'bside_Mpch'] = boxside
    head.attrs[u'mp_Msunh'] = mp
    head.attrs[u'snap'] = snap
    data_group = hf.create_group('data')
    hf.close()

    # Make the selection, if relevant
    nomask = False; mask = None
    if selection is None:
        nomask = True
    else:
        for ifile, props  in selection.items():
            filename = path+ifile
            group = props['group']
            datasets = props['datasets']
            lowl = props['low_limits']
            highl = props['high_limits']
            units = props['units']

            with h5py.File(filename, 'r') as hdf_file:
                if group is None:
                    hf = hdf_file
                elif group in hdf_file:
                    hf = hdf_file[group]

                # Read datasets and generate conditions
                for ii, dataset in enumerate(datasets):
                    if ii == 0:
                        alldata = hf[dataset][:]
                    else:
                        alldata = np.vstack((alldata,hf[dataset][:]))

            # Build combined mask
            mask = u.combined_mask(alldata,lowl,highl,verbose=verbose)
            if mask is None:
                if verbose:
                    print(f' * No adequate data in {ifile}, continuing')
                continue
            else:
                # Generate galaxy indexes from the original dataset
                with h5py.File(outfile, 'a') as outf:
                    ids = outf['data'].create_dataset('gal_index', data=mask)
                    ids.attrs['units'] = 'Index in original file'

                # Write the properties in the output file
                for ii in range(np.shape(alldata)[0]):
                    vals = alldata[ii][mask]
                    with h5py.File(outfile, 'a') as outf:
                        dd = outf['data'].create_dataset(datasets[ii], data=vals)
                        dd.attrs['units'] = units[ii]

    # Loop over files
    count_props = -1
    for ifile, props  in file_props.items():
        filename = path+ifile
        group = props['group']
        datasets = props['datasets']
        
        # Check that metallicities need to be calculated
        calc_Zdisc = set([mcold_disc,mcold_z_disc]).issubset(datasets)
        if calc_Zdisc:
            Zdisc = np.ones(len(mask), dtype=float)

        calc_Zbst  = set([mcold_burst,mcold_z_burst]).issubset(datasets)
        if calc_Zbst:
            Zbst = np.ones(len(mask), dtype=float)

        # Read data in each file    
        with h5py.File(filename, 'r') as hdf_file:
            if group is None:
                hf = hdf_file
            elif group in hdf_file:
                hf = hdf_file[group]
                    
            # Extract properties
            for ii,prop in enumerate(datasets):
                if prop=='redshift':
                    zz = hf[prop]
                    with h5py.File(outfile, 'a') as outf:
                        outf['header'].attrs['redshift'] = zz
                else:
                    count_props += 1
                    vals = None
                    if nomask:
                        vals = hf[prop][:]                            
                    else:
                        vals = hf[prop][mask]
                    if vals is None: continue

                    if calc_Zdisc and (prop==mcold_disc or prop==mcold_z_disc):
                        if prop==mcold_disc:
                            Zdisc[vals<=0.] = 0.
                            Zdisc[vals>0.] /= vals[vals>0.]
                        else:
                            Zdisc *= vals
                    elif calc_Zbst and (prop==mcold_burst or prop==mcold_z_burst):
                        if prop==mcold_burst:
                            Zbst[vals<=0.] = 0.
                            Zbst[vals>0.] /= vals[vals>0.]
                        else:
                            Zbst *= vals
                    else:
                        with h5py.File(outfile, 'a') as outf:
                            dd = outf['data'].create_dataset(prop, data=vals)
                            dd.attrs['units'] = props['units'][ii]


            # Write out metallicities, if required
            if calc_Zdisc:
                with h5py.File(outfile, 'a') as outf:
                    dd = outf['data'].create_dataset('Zgas_disc', data=Zdisc)
                    dd.attrs['units'] = 'M_Z/M'
            if calc_Zbst:
                with h5py.File(outfile, 'a') as outf:
                    dd = outf['data'].create_dataset('Zgas_bst', data=Zbst)
                    dd.attrs['units'] = 'M_Z/M'
