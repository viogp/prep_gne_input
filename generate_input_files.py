"""
Program to generate files for generate_nebular_emission from hdf5 files
Ensure you have previously validated the input files with validate_files.py
"""
from src.prep_input import prep_input

verbose = True
nvol = 2

sim = 'GP20SU_1'
snap = 87
subvols = list(range(nvol))

prep_input(sim, snap, subvols, validate_files=False,
           generate_files=True, verbose=verbose)
