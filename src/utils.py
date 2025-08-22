import h5py
import numpy as np

def combined_mask(alldata,low_lim,high_lim,verbose=True):
    '''
    Combine conditions to different datasets into one mask

    Parameters
    ----------
    alldata : numpy array (N,M)
       Array with N datasets
    low_lim : list (N,1)
       List with the lower limits for each dataset
    high_lim : list (N,1)
       List with the higher limits for each dataset
    
     
    Returns
    -------
    mask : numpy array
       Indexes of those rows passing the combined conditions
    '''
    # Chack that input shapes are consistent
    nd = np.shape(alldata)[0]
    if (nd != len(low_lim) or nd != len(high_lim)):
        if verbose:
            print(f' WARNING (combined_mask): Data, '
                  f'{np.shape(alldata)}, should be (N,M) and '
                  f'limits (N,1), len(low_lim)={len(low_lim)} and '
                  f'len(high_lim)={len(high_lim)}')
        return None

    # Read each dataset and build individual conditions
    cuts = []
    for ii in range(nd):
        data = alldata[ii][:]

        if low_lim[ii] is not None and high_lim[ii] is not None:
            cuts.append((data >= low_lim[ii]) & (data <= high_lim[ii]))
        elif low_lim[ii] is not None:
            cuts.append(data >= low_lim[ii])
        elif high_lim[ii] is not None:
            cuts.append(data <= high_lim[ii])
        else:
            cuts.append(np.ones(len(data), dtype=bool))
    if not cuts:
        return None

    # Combine all conditions
    combined_cuts = cuts[0]
    for cut in cuts[1:]:
        combined_cuts &= cut
    if not np.any(combined_cuts):
        return None

    mask = np.where(combined_cuts)[0]
    return mask

#---------------hdf5 files-----------------------------------------
def check_h5_structure(infile, datasets, group=None, verbose=True):
    """
    Check that the names given correspond to datasets in a hdf5 file

    Parameters
    ----------
    infile : string
      Name of input file (this should be a hdf5 file)
    datasets : list
      Names of expected datasets
    froup : string
      Name of group where datasets are

    Return
    -------
    structure_ok : bool
    """
    try:
        with h5py.File(infile, 'r') as hdf_file:
            if group is None:
                hf = hdf_file
            elif group in hdf_file:
                hf = hdf_file[group]
            else:
                return False

            structure_ok = set(datasets).issubset(list(hf.keys()))
            if not structure_ok and verbose:
                missing = list(set(datasets).difference(list(hf.keys())))
                print(f"  {missing} properties not found in {infile}")
    except FileNotFoundError:
        if verbose:
            print(f"  {infile} could not be opened")
        structure_ok = False
        
    return structure_ok
