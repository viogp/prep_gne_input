"""
Program to prepare input files for generate_nebular_emission from hdf5 files
"""

from src.config import get_config
from src.validate import validate_hdf5_file
from src.generate_input import generate_input_file
from src.generate_test_files import generate_test_files

verbose = True

validate_files = True  # Check the structure of files
generate_files = False # Generate input for generate_nebular_emission
generate_testing_files = False # Generate reduced input for testing

#-------------------------------------------------------------
#sim = 'GP20SU_1' #'GP20SU_2'
#snap = 96
#subvols = list(range(2))
#-------------------------------------------------------------
sim = 'GP20UNIT1Gpc_fnl0' #'GP20UNIT1Gpc_fnl100' 
snap = 109
subvols = [34,35] #list(range(1,63)) #list(range(1))
#-------------------------------------------------------------
#sim = 'GP20cosma' # Set the file configuration adequately 
#snap = 39 #61
#subvols = list(range(64))
#-------------------------------------------------------------

laptop = False  # Tests within laptop (different paths)
if laptop:
    subvols = list(range(2))

percentage = 10 # Percentage for generating testing file
subfiles = 2     # Number of testing files
    
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

