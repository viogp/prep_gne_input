"""
Program to prepare input files for generate_nebular_emission from hdf5 files
"""


from src.config import get_config
from src.validate import validate_hdf5_files
from src.generate_input import generate_input_file

verbose = True

simtype = 'GP20'
snap = 39
subvols = list(range(64))

localtest = True # Laptop paths
if localtest:
    subvols = list(range(2))

# Get the corresponding configuration
config = get_config(simtype,snap,localtest=localtest)
    
# Validate that files have the expected structure
validate_files = True
if validate_files:
    valid = validate_hdf5_files(config, subvols, verbose=verbose)

# Generate input data for generate_nebular_emission
generate_input = False
if generate_input:
    for ivol in subvols:
        success = generate_input_file(config, ivol, verbose=verbose)

# Random subsampling of the input files
generate_exdata= False
subsampling = 0.1 # Percentage
min_subvols = 2

