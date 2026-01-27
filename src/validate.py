import sys
import src.utils as u

def validate_hdf5_file(config, snap, ivol, verbose=True):
    """
    Validate that all HDF5 files have the expected structure
    
    Parameters
    ----------
    config : dict
        Configuration dictionary containing paths and file properties
    snap : integer
        Number of the simulation snapshot
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
    selection = config['selection']
    file_props = config['file_props']
    
    path = u.get_path(config['root'],ivol,ending=config['ending'])
    
    # File to be read a directory above, if applicable
    except_file = config.get('except_file')
    if except_file is not None:
        except_path =  u.get_path(config['root'],ivol)

    # Combine selection and file_props for validation
    if selection is None:
        allfiles = file_props
    else:
        allfiles = {**selection, **file_props}

    for ifile, props in allfiles.items():
        datasets = props['datasets']
        group = props.get('group')

        if except_file is not None and ifile == config['except_file']:
            structure_ok = u.check_h5_structure(except_path+ifile,
                                                datasets,group=group)
        else:
            structure_ok = u.check_h5_structure(path+ifile,datasets,group=group)
            
        if not structure_ok:
            count_fails += 1
    
    if count_fails > 0:
        print(f"VALIDATION FAILED for ivol{ivol}.")
        return False    
    return True
