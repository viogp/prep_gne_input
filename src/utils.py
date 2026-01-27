import os
from glob import glob
import h5py
import numpy as np


def get_path(root, ivol, ending=None):
    """
    Generate the appropriate file path based on the izivol flag.
    
    Parameters
    ----------
    root : str
        Root path from config
    ivol : int
        Volume index number
    ending : str
        If None, path structure appends ivol at the end: root + ivol + '/'
        Otherwise: root + ivol + '/' + ending

    Returns
    -------
    path : str
    """
    # Append volume number to root
    path = root + str(ivol) + '/'

    if ending is not None: # Append the ending
        path = path + ending
        
    return path


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
    # Check that input shapes are consistent
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


def get_group_name(root, snap, group_base='Output',ndigits=3, dir_base='iz'):
    """
    Get the name of the hdf5 group to be read for a given snapshot.
    
    Scans the root directory for subdirectories matching 'iz<number>',
    sorts the numbers in descending order, and returns a n-character
    string representing the 1-based index of the given snap.
    
    Parameters
    ----------
    root : str
        Root to higher level directories
    snap : str or int
        The snapshot number to find (the number after 'iz')
    group_base : str
        The base for the group name
    ndigits : int
        Number of characters to convert digits to
    dir_base : str
        The base for the redshift directories

    Returns
    -------
    group_name : str
    """
    group_name = group_base
    
    # Find output snapshots
    vol_dirs = glob(root+'*')
    if len(vol_dirs) < 1:
        print(f'STOP: No adequate directories with root {root}')
        return None
    zroot = os.path.join(vol_dirs[0],dir_base)
    z_dirs = glob(zroot+'*')
    if len(z_dirs) < 1:
        print(f'STOP: No adequate directories with root {zroot}')
        return None
    zz = [int(os.path.basename(d).replace(dir_base, '')) for d in z_dirs]
    zz.sort(reverse=True)

    # Get the index of the snapshot as n-digits characters
    oonum = zz.index(int(snap)) + 1
    group_name += f'{oonum:0{ndigits}d}'
    return group_name

#---------------hdf5 files-----------------------------------------
def open_hdf5_group(hdf_file, group):
    """
    Get the appropriate group or root from an HDF5 file
    
    Parameters
    ----------
    hdf_file : h5py.File
        Open HDF5 file object
    group : str or None
        Group name
    
    Returns
    -------
    h5py.Group or h5py.File or None
    """   
    if group is None:
        return hdf_file
    elif group in hdf_file:
        return hdf_file[group]
    else:
        return None


def check_h5_structure(infile, datasets, group=None, verbose=True):
    """
    Check that the names given correspond to datasets in a hdf5 file

    Parameters
    ----------
    infile : string
      Name of input file (this should be a hdf5 file)
    datasets : list
      Names of expected datasets
    group : string
      Name of group where datasets are, or 'Output###' for auto-detect) 

    Return
    -------
    structure_ok : bool
    """
    try:
        with h5py.File(infile, 'r') as hdf_file:
            hf = open_hdf5_group(hdf_file, group)
            if hf is None:
                if verbose:
                    print(f'WARNING: Group (pattern) {group} not found in {infile}')
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
