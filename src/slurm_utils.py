''' Auxiliary functions for slurm submission '''
import os,sys
import subprocess

def generate_job_name(sim, snap, subvols):
    """Generate a unique job name based on sim, snap, and subvols."""
    # Create a compact subvols representation
    if len(subvols) <= 2:
        subvols_str = '_'.join(map(str, subvols))
    else:
        subvols_str = f'{subvols[0]}-{subvols[-1]}'
    
    return f'prep_{sim}_iz{snap}_ivols{subvols_str}'


def get_slurm_template(hpc):
    dirnom = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    fnom = 'slurm_'+hpc+'_template.sh'
    template_file = os.path.join(dirnom,fnom)

    # Check if template file exists
    if not os.path.exists(template_file):
        print(f'ERROR: Template file {template_file} not found')
        sys.exit()

    # Read template content
    slurm_template = None
    with open(template_file, 'r') as f:
        slurm_template = f.read()
    return slurm_template


def create_slurm_script(hpc, sim, snap, subvols,
                        outdir=None, verbose=True):
    """
    Create a SLURM script for a specific hpc/sim/snap/subvols combination.

    Parameters
    ----------
    hpc : string
        HPC machine to submit jobs
    sim : string
        Simulation name
    snap : string
        Simulation snapshot number 
    subvols : list of integers
        List of subvolumes
    outdir : string
        Name of output directory, if different from output/
    """
    job_name = generate_job_name(sim, snap, subvols)

    # Read the appropriate template file
    slurm_template = get_slurm_template(hpc)

    # Replace placeholders in template
    script_content = slurm_template
    script_content = script_content.replace('JOB_NAME', job_name)
    script_content = script_content.replace('SIM_NAME', sim)
    script_content = script_content.replace('SNAP_NUM', str(snap))
    script_content = script_content.replace('SUBVOLS_LIST', str(subvols))
    script_content = script_content.replace('VERBOSE', str(verbose))
    
    # Write script to file
    if outdir is None:
        output_dir = 'output'
    else:
        output_dir = outdir
    script_path = os.path.join(output_dir, f'submit_{job_name}.sh')

    with open(script_path, 'w') as f:
        f.write(script_content)
    
    return script_path, job_name


def submit_slurm_job(script_path,job_name):
    """Submit a SLURM job and return the job ID."""    
    try:
        process = subprocess.Popen(
            ['sbatch', script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate()
        
        if process.returncode == 0:
            # Extract job ID from output (format: "Submitted batch job XXXXX")
            output = stdout.decode('utf-8').strip()
            job_id = output.split()[-1] if output else 'unknown'
            print(f'  Submitted {job_name}: Job ID {job_id}')
            return job_id
        else:
            print(f'  ERROR submitting {job_name}: {stderr.decode("utf-8")}')
            return None
    except FileNotFoundError:
        print(f'  WARNING: sbatch not found. Script saved to {script_path}')
        return None

