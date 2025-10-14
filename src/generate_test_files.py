"""
Program to generate input files for gnerate_nebular_emission
"""
import os
import h5py
import numpy as np

#import src.utils as u

def generate_test_files(config, subvols, p, nf, outpath='output', verbose=True):
    """
    Generate test input file for generate_nebular_emission
    both as hdf5 files and txt
    
    Parameters
    ----------
    config : dict
        Configuration dictionary containing paths and file properties
    subvols : integer
        Number of subvolumes
    p : float
        Percentage of the input file to be stored
    nf : integer
        Number of output files to have
    output :  string
        Path to folder with files for tests
    verbose : bool
        Enable verbose output
        
    Returns
    -------
    bool
        True if the files have been successfully generated, False otherwise
    """
    root = config['root']
    ifile = 0

    # Generate output folder if needed
    if not os.path.exists(outpath):
        os.makedirs(outpath)
    
    # Generate output files with a header and data structure
    infile = root + str(subvols[0]) +'/gne_input.hdf5'
    with h5py.File(infile, 'r') as ff:
        iz = ff['header'].attrs['snapnum']
        outpath1 = outpath+'/iz'+str(iz)+'/ivol'
        outfs_h5 = []; outfs_t = []

        # Generate header for text files
        head = '# '
        for key in ff['data'].keys():
            head += key+' '
        
        # Generate output files
        for ii in range(nf):
            outpath2 = outpath1+str(ii)+'/'
            if not os.path.exists(outpath2):
                os.makedirs(outpath2)

            # Hdf5 files
            outfile = outpath2+'ex.hdf5'
            outfs_h5.append(outfile)
            with h5py.File(outfile, 'w') as outf:
                # Copy header
                ff.copy('header', outf)
                outf['header'].attrs['percentage'] = p

                # Copy data structure (assuming no subgroups)
                dg = outf.create_group('data')
                for key in ff['data'].keys():
                    dtype = ff['data/'+key].dtype
                    dset = dg.create_dataset(key,shape=(0,),dtype=dtype,
                                            maxshape=(None,))

                    # Copy attributes from source dataset
                    for attr_name, attr_value in ff['data'][key].attrs.items():
                        dset.attrs[attr_name] = attr_value
                    
            # Text files
            outfile = outpath2+'ex.txt'
            outfs_t.append(outfile)
            with open(outfile, 'w') as f:
                f.write(head + "\n")

    # Loop over files to be reduced
    sv = len(subvols)
    q = sv//nf; nfcount = 0
    ifile = 0
    print(f'* Output in files {outfs_h5[ifile]}, {outfs_t[ifile]}')
    for ivol in subvols:
        # Output file
        nfcount += 1
        if (nfcount>q and ifile<nf):
            ifile += 1; nfcount=0
            print(f'* Output in files {outfs_h5[ifile]}, {outfs_t[ifile]}')
        outf_h5 = outfs_h5[ifile]
        outf_t  = outfs_t[ifile]

        # Get the file names to be reduced
        path = root + str(ivol) + '/'
        infile = path+'gne_input.hdf5'
        if (not os.path.exists(infile)):
            print(f' No adecuate path: {path}')
            return False

        # Read input file to get number of entries
        with h5py.File(infile, 'r') as inf:
            # Get number of galaxies in data group
            data_group = inf['data']
            dataset_names = list(data_group.keys())
            if len(dataset_names) == 0:
                print(f' No datasets found in {infile}')
                continue
        
            # Get total number of entries from first dataset
            first_dataset = dataset_names[0]
            ntotal = len(data_group[first_dataset])
        
            # Calculate number of entries for this file
            n2file = int(ntotal * p / 100.0)
            if n2file == 0: continue
            
            # Generate random indices for subsample
            random_indices = np.random.choice(ntotal, size=n2file, replace=False)
            random_indices = np.sort(random_indices)
        
            # Append data to output hdf5 file
            with h5py.File(outf_h5, 'a') as outfile:
                for key in dataset_names:
                    subsample = data_group[key][random_indices]

                    # Get current size, resize and write new data
                    current_size = outfile['data'][key].shape[0]
                    outfile['data'][key].resize(current_size + n2file, axis=0)
                    outfile['data'][key][current_size:] = subsample

            # Append data to output text file
            with open(outf_t, 'a') as outfile:
                for idx in random_indices:
                    row_data = [str(data_group[key][idx]) for key in dataset_names]
                    outfile.write('\t'.join(row_data) + '\n')
    return True
