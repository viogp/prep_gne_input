''' Generate and submit SLURM jobs for preparing Galform input '''
import src.slurm_utils as u

verbose = True
nvol = 64

SIM = "GP20"

submit_jobs = True  # False for only generating the scripts
check_all_jobs = True
clean = False

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
    #('GP20SU_1', [109, 104, 98, 90, 87, 128, 96, 78], list(range(nvol))),
    ('GP20SU_1', [109, 104, 98, 90, 96, 78], list(range(nvol))),
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

# Select which simulations to process
hpc = 'taurus'

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

# Submit, check or clean
if clean:
    u.clean_all_jobs(simulations, only_show=True)
elif check_all_jobs:
    results = u.check_all_jobs(simulations,verbose=True)
else:            
    job_count = 0
    for sim, snaps, subvols in simulations:
        for snap in snaps:
            # Generate SLURM script
            script_path, job_name= u.create_slurm_script(
                hpc, sim, snap, subvols, verbose=verbose)
            if verbose: 
                print(f'  Created script: {script_path}')
                
            # Submit the job
            if submit_jobs:
                u.submit_slurm_job(script_path, job_name)
                job_count += 1
    
    if submit_jobs and verbose:
        print(f'Total jobs submitted: {job_count}')
            
