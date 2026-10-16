''' Validate a set of simulations'''
from src.prep_input import prep_input

verbose = True
nvol = 64
SIM = "Shark"

# Shark in taurus
taurus_sims_Shark = [
    ('SharkSU_1', [128, 109, 104, 98, 96, 90, 87, 78], list(range(nvol))),
    ('SharkSU_2', [128, 109, 104, 98, 96, 90, 87, 78], list(range(nvol))),
    ('SharkUNIT1Gpc_fnl0', [109, 104, 98, 90, 87], list(range(nvol))),
    ('SharkUNIT1Gpc_fnl0', [128], list(range(5))),
    ('SharkUNIT1Gpc_fnl0', [81], [0, 1, 2, 5] + list(range(10, 27)) + [28, 34, 35] + list(range(39, nvol))),
    ('SharkUNIT1Gpc_fnl0', [78], list(range(6))),
    ('SharkUNIT1Gpc_fnl100', [108, 103, 97, 89, 86], list(range(nvol))),
    ('SharkUNIT1Gpc_fnl100', [127, 95, 77], [0]),
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

simtypes = {
    "Shark": taurus_sims_Shark,
    "GP20": taurus_sims_GP20,
    "cosma": cosma_sims_GP20
}

# Loop over the relevant simulations
try:
    simulations = simtypes[SIM]
except KeyError:
    raise ValueError(f"Simulation type '{SIM}' not supported. Available types: {simtypes.keys()}")
for sim, snaps, subvols in simulations:
    for snap in snaps:
        prep_input(sim, snap, subvols, verbose=verbose)
