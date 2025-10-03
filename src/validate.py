import sys
import src.utils as u

def validate_hdf5_file(config, ivol, verbose=True):
    """
    Validate that all HDF5 files have the expected structure
    
    Parameters
    ----------
    config : dict
        Configuration dictionary containing paths and file properties
    ivol : integer
        Number of subvolume
    verbose : bool
        Enable verbose output
        
    Returns
    -------
    bool
        True if all files are valid, False otherwise
    """
    
    count_fails = 0
    root = config['root']
    selection = config['selection']
    file_props = config['file_props']
    
    path = root + str(ivol) + '/'
    
    # Combine selection and file_props for validation
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
    
    if count_fails > 0:
        print(f"VALIDATION FAILED for ivol{ivol}.")
        return False    
    return True
