"""
Program to prepare input files for generate_nebular_emission from hdf5 files
"""

from src.config import get_config
from src.validate import validate_hdf5_file
#from src.generate_input import generate_input_file

verbose = True

validate_files = True  # Check the structure of files
generate_files = False # Generate input for generate_nebular_emission
generate_testing_files = False # Generate reduced input for testing

simtype = 'GP20' # Set the file configuration adequately 
snap = 39
subvols = list(range(64))

laptop   = True     # Tests within laptop (different paths)
if laptop:
    subvols = list(range(2))

# Get the configuration
config = get_config(simtype,snap,laptop=laptop)

# Validate that files have the expected structure
if validate_files:
    count_failures = 0
    for ivol in subvols:
        success = validate_hdf5_file(config, ivol, verbose=verbose)
        if not success: count_failures += 1
    if count_failures<1: print(f'SUCCESS: All {len(subvols)} subvolumes have valid HDF5 files.')
        
# Generate input data for generate_nebular_emission
if generate_files:
    count_failures = 0
    for ivol in subvols:
        success = generate_input_file(config, ivol, verbose=verbose)
        if not success: count_failures += 1
    if count_failures<1: print(f'SUCCESS: All {len(subvols)} HDF5 files have been generated.')

## Random subsampling of the input files
#subsampling = 0.1 # Percentage
#min_subvols = 2

