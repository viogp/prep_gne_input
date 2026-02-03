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


def clean_job_files(job_name=None, outdir=None, only_show=True, verbose=True):
    """
    Remove .out, .err, and .sh files for a specific job or all jobs.

    Parameters
    ----------
    job_name : string or None
        Name of the job to clean. If None, clean all job files in outdir.
    outdir : string
        Directory containing output files, default is 'output/'
    only_show : bool
        If True, only list files that would be deleted without removing them.
        Set to False to actually delete files.
    verbose : bool
        If True, print information about deleted files

    Returns
    -------
    deleted_files : list
        List of files that were deleted (or would be deleted if only_show=True)
    """
    if outdir is None:
        output_dir = 'output'
    else:
        output_dir = outdir
    
    if not os.path.exists(output_dir):
        if verbose:
            print(f'Directory {output_dir} does not exist')
        return []
    
    deleted_files = []
    
    if job_name is not None:
        # Clean files for a specific job
        extensions = ['.out', '.err']
        for ext in extensions:
            filepath = os.path.join(output_dir, f'{job_name}{ext}')
            if os.path.exists(filepath):
                deleted_files.append(filepath)
                if not only_show:
                    os.remove(filepath)
        
        # Also remove the submit script
        script_path = os.path.join(output_dir, f'submit_{job_name}.sh')
        if os.path.exists(script_path):
            deleted_files.append(script_path)
            if not only_show:
                os.remove(script_path)
    else:
        # Clean all .out, .err, and .sh files in the directory
        for filename in os.listdir(output_dir):
            if filename.endswith('.out') or filename.endswith('.err') or filename.endswith('.sh'):
                filepath = os.path.join(output_dir, filename)
                deleted_files.append(filepath)
                if not only_show:
                    os.remove(filepath)
    
    # Print results
    if verbose:
        action = 'Would delete' if only_show else 'Deleted'
        if deleted_files:
            print(f'{action} {len(deleted_files)} file(s):')
            for f in deleted_files:
                print(f'  {f}')
        else:
            print('No files to delete')
        
        if only_show and deleted_files:
            print('\n(Set only_show=False to delete.)')
    
    return deleted_files


def clean_all_jobs(simulations, outdir=None, only_show=True, verbose=True):
    """
    Remove .out, .err, and .sh files for all jobs in a simulation list.

    Parameters
    ----------
    simulations : list of tuples
        List of (sim, snaps, subvols) tuples
    outdir : string
        Directory containing output files, default is 'output/'
    only_show : bool
        If True, only list files that would be deleted without removing them.
        Set to False to actually delete files.
    verbose : bool
        If True, print information about deleted files

    Returns
    -------
    deleted_files : list
        List of all files that were deleted (or would be deleted if only_show=True)
    """
    all_deleted = []
    
    for sim, snaps, subvols in simulations:
        for snap in snaps:
            job_name = generate_job_name(sim, snap, subvols)
            deleted = clean_job_files(job_name, outdir=outdir,
                                      only_show=only_show, verbose=False)
            all_deleted.extend(deleted)
    
    # Print summary
    if verbose:
        action = 'Would delete' if only_show else 'Deleted'
        if all_deleted:
            print(f'{action} {len(all_deleted)} file(s):')
            for f in all_deleted:
                print(f'  {f}')
        else:
            print('No files to delete')
        
        if only_show and all_deleted:
            print('\n(Set only_show=False to delete.)')
    
    return all_deleted
