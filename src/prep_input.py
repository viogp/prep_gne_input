from src.config import get_config
from src.validate import validate_hdf5_file
from src.generate_input import generate_input_file
from src.generate_test_files import generate_test_files

def prep_input(sim,snap,subvols,laptop=False,percentage=10,subfiles=2,
               validate_files=True,generate_files=False,
               generate_testing_files=False,verbose=False):
    '''
    Validate input files and generate input for 
    generate_nebular_emission from hdf5 files 

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
    percentage : int
        Percentage for generating testing file
    subfiles : int
        Number of testing files
    validate_files : bool
        True to check the structure of files
    generate_files : bool
        True to generate input for generate_nebular_emission
    generate_testing_files : bool
        True to generate reduced input for testing
    verbose : bool
        If True, print further messages
    ''' 
    laptop = False  # Tests within laptop (different paths)
    if laptop:
        subvols = list(range(2))

    # Get the configuration
    config = get_config(sim,snap,subvols,laptop=laptop,verbose=verbose)
    
    # Validate that files have the expected structure
    if validate_files:
        count_failures = 0
        for ivol in subvols:
            success = validate_hdf5_file(config, snap, ivol, verbose=verbose)
            if not success: count_failures += 1
        if count_failures<1: print(f'SUCCESS: All {len(subvols)} subvolumes have valid hdf5 files.')
            
    # Generate input data for generate_nebular_emission
    if generate_files:
        count_failures = 0
        for ivol in subvols:
            success = generate_input_file(config, ivol, verbose=verbose)
            if not success: count_failures += 1
        if count_failures<1: print(f'SUCCESS: All {len(subvols)} hdf5 files have been generated.')
    
    # Random subsampling of the input files
    if generate_testing_files:
        success = generate_test_files(config, subvols, percentage,
                                      subfiles, verbose=verbose)
        if success: print(f'SUCCESS: All {subfiles*2} test files have been generated.')

    return
