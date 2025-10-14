"""
Program to generate input files for gnerate_nebular_emission
"""
import os
import h5py
import numpy as np

import src.utils as u

def generate_input_file(config, ivol, verbose=True):
    """
    Generate input file for generate_nebular_emission
    
    Parameters
    ----------
    config : dict
        Configuration dictionary containing paths and file properties
    ivol : integer
        Number of subvol
    verbose : bool
        Enable verbose output
        
    Returns
    -------
    bool
        True if the file has been successfully generated, False otherwise
    """
    root = config['root']
    path = root + str(ivol) + '/'
    if (not os.path.exists(path)):
        print(f' No adecuate path: {path}')
        return False

    # Generate a header for the output file
    outfile = path+'gne_input.hdf5'
    try:
        hf = h5py.File(outfile, 'w')
    except:
        print(f' Not able to generate file: {outfile}')
        return False
    headnom = 'header'
    head = hf.create_dataset(headnom,())
    head.attrs[u'h0'] = config['h0']
    head.attrs[u'omega0'] = config['omega0']
    head.attrs[u'omegab'] = config['omegab']
    head.attrs[u'lambda0'] = config['lambda0']
    head.attrs[u'bside_Mpch'] = config['boxside']
    head.attrs[u'mp_Msunh'] = config['mp']
    head.attrs[u'snapnum'] = config['snap']
    data_group = hf.create_group('data')
    hf.close()
    print(f' * Generating file: {outfile}')
    
    # Make the selection, if relevant
    nomask = False; mask = None
    selection = config['selection']
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

    # Metallicity variables
    mcold_disc = config['mcold_disc']
    mcold_z_disc = config['mcold_z_disc']
    mcold_burst = config['mcold_burst']
    mcold_z_burst = config['mcold_z_burst']

    # Loop over files with information
    count_props = -1
    file_props = config['file_props']
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

                    if(prop!=mcold_z_disc and prop!=mcold_z_burst):
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

    return True
