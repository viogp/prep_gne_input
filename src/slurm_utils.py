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


def check_job_status(job_name, outdir=None, success_string='SUCCESS', verbose=True):
    """
    Check the status of a completed SLURM job by examining its output files.

    Parameters
    ----------
    job_name : string
        Name of the job (used to find .out and .err files)
    outdir : string
        Directory containing output files, default is 'output/'
    success_string : string
        String to search for in .out file to confirm success, default is 'SUCCESS'
    verbose : bool
        If True, print detailed status messages

    Returns
    -------
    status : string
        'success' - job completed successfully (.err empty, .out contains success_string)
        'error' - job has errors (.err file is not empty)
        'incomplete' - job may not have finished (.out missing success_string)
        'not_found' - output files not found
    error_content : string or None
        Content of .err file if there are errors, None otherwise
    """
    if outdir is None:
        output_dir = 'output'
    else:
        output_dir = outdir
    
    out_file = os.path.join(output_dir, f'{job_name}.out')
    err_file = os.path.join(output_dir, f'{job_name}.err')
    
    # Check if files exist
    out_exists = os.path.exists(out_file)
    err_exists = os.path.exists(err_file)
    
    if not out_exists and not err_exists:
        if verbose:
            print(f'  {job_name}: NOT FOUND - output files do not exist')
        return 'not_found', None
    
    # Check .err file (should be empty)
    has_errors = False
    error_content = None
    if err_exists:
        with open(err_file, 'r') as f:
            error_content = f.read().strip()
        if error_content:
            has_errors = True
            if verbose:
                print(f'  {job_name}: ERROR - .err file is not empty')
                print(f'    Error content: {error_content[:200]}...' if len(error_content) > 200 else f'    Error content: {error_content}')
    
    # Check .out file for success string
    has_success = False
    if out_exists:
        with open(out_file, 'r') as f:
            out_content = f.read()
        if success_string in out_content:
            has_success = True
    
    # Determine overall status
    if has_errors:
        return 'error', error_content
    elif has_success:
        if verbose:
            print(f'  {job_name}: SUCCESS')
        return 'success', None
    else:
        if verbose:
            print(f'  {job_name}: INCOMPLETE - "{success_string}" not found in .out file')
        return 'incomplete', None


def check_all_jobs(simulations, outdir=None, success_string='SUCCESS', verbose=True):
    """
    Check the status of all jobs for a list of simulations.

    Parameters
    ----------
    simulations : list of tuples
        List of (sim, snaps, subvols) tuples
    outdir : string
        Directory containing output files, default is 'output/'
    success_string : string
        String to search for in .out file to confirm success
    verbose : bool
        If True, print detailed status messages

    Returns
    -------
    results : dict
        Dictionary with keys 'success', 'error', 'incomplete', 'not_found',
        each containing a list of job names in that status
    """
    results = {
        'success': [],
        'error': [],
        'incomplete': [],
        'not_found': []
    }
    
    for sim, snaps, subvols in simulations:
        for snap in snaps:
            job_name = generate_job_name(sim, snap, subvols)
            status, _ = check_job_status(job_name, outdir=outdir,
                                         success_string=success_string,
                                         verbose=verbose)
            results[status].append(job_name)
    
    # Print summary
    if verbose:
        print('\n--- Summary ---')
        print(f'  Success:    {len(results["success"])}')
        print(f'  Error:      {len(results["error"])}')
        print(f'  Incomplete: {len(results["incomplete"])}')
        print(f'  Not found:  {len(results["not_found"])}')
    
    return results
