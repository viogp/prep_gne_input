''' Validate a set of simulations'''
from src.prep_input import prep_input

verbose = True
nvol = 2

test_taurus_sims_GP20 = [
    ('GP20SU_1', [87, 128], list(range(nvol))),
]

# Galform in taurus
taurus_sims_GP20 = [
    ('GP20SU_1', [109, 104, 98, 90, 87, 128, 96, 78], list(range(nvol))),
    ('GP20SU_2', [109, 104, 98, 90, 87], list(range(nvol))),
    ('GP20UNIT1Gpc_fnl0', [98, 109, 87, 90, 104], [0] + list(range(3, nvol))),
    ('GP20UNIT1Gpc_fnl0', [128,109,105,104,103,101,98,92,90,87,84,81,79,77], [1,2]),
    ('GP20UNIT1Gpc_fnl100', [127, 108, 103, 97, 95, 89, 86, 77], [0]),
    ('GP20UNIT1Gpc_fnl100', [108, 103, 97, 89, 86], list(range(1, nvol))),
]

# Galform in cosma
cosma_sims_GP20 = [
    ('GP20cosma', [39, 61], list(range(64)))
]

# Loop over the relevant simulations
#simulations = taurus_sims_GP20
simulations = test_taurus_sims_GP20
for sim, snaps, subvols in simulations:
    for snap in snaps:
        prep_input(sim, snap, subvols, validate_files=False,
                   generate_files=True,verbose=verbose)
