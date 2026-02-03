# python -m unittest tests/test_slurm_utils.py 

import unittest
import os
import tempfile
import shutil

import src.slurm_utils as su

class TestSlurmUtils(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures before running tests in the class"""
        # Create a temporary directory under the output folder
        cls.test_dir = tempfile.mkdtemp(dir='output')
        
        # Create a mock template file for testing
        cls.template_content = '''#!/bin/sh
#SBATCH --job-name=JOB_NAME
#SBATCH --output=output/JOB_NAME.out
#SBATCH --error=output/JOB_NAME.err

srun python -c "
from src.prep_input import prep_input
prep_input('SIM_NAME', SNAP_NUM, SUBVOLS_LIST, verbose=VERBOSE)
"
'''
        # Get the directory where slurm_utils.py expects templates
        # (one level up from src/)
        cls.template_dir = os.path.dirname(os.path.dirname(os.path.abspath(su.__file__)))
        
        # Store original template if it exists (to restore later)
        cls.taurus_template_path = os.path.join(cls.template_dir, 'slurm_taurus_template.sh')
        cls.taurus_backup = None
        if os.path.exists(cls.taurus_template_path):
            with open(cls.taurus_template_path, 'r') as f:
                cls.taurus_backup = f.read()
        
        # Create test template
        with open(cls.taurus_template_path, 'w') as f:
            f.write(cls.template_content)
   
    @classmethod
    def tearDownClass(cls):
        """Clean up after all tests in the class are finished"""
        # Remove temporary test directory
        if os.path.exists(cls.test_dir):
            try:
                shutil.rmtree(cls.test_dir)
            except (OSError, PermissionError) as e:
                print(f"Warning: Could not remove test directory {cls.test_dir}: {e}")
        
        # Restore original template or remove test template
        if cls.taurus_backup is not None:
            with open(cls.taurus_template_path, 'w') as f:
                f.write(cls.taurus_backup)
        elif os.path.exists(cls.taurus_template_path):
            os.remove(cls.taurus_template_path)

    def test_generate_job_name_short_subvols(self):
        # Single subvolume
        job_name = su.generate_job_name('GP20SU_1', 87, [0])
        self.assertEqual(job_name, 'prep_GP20SU_1_iz87_ivols0')
        
        # Two subvolumes
        job_name = su.generate_job_name('GP20SU_1', 128, [0, 1])
        self.assertEqual(job_name, 'prep_GP20SU_1_iz128_ivols0_1')

        # Three subvolumes
        job_name = su.generate_job_name('GP20SU_2', 104, [0, 1, 2])
        self.assertEqual(job_name, 'prep_GP20SU_2_iz104_ivols0-2')
        
        # Many subvolumes
        job_name = su.generate_job_name('GP20cosma', 39, list(range(64)))
        self.assertEqual(job_name, 'prep_GP20cosma_iz39_ivols0-63')

        job_name = su.generate_job_name('GP20UNIT1Gpc_fnl100', 97, [0])
        self.assertEqual(job_name, 'prep_GP20UNIT1Gpc_fnl100_iz97_ivols0')

    def test_get_slurm_template_valid(self):
        """Test reading a valid template file"""
        template = su.get_slurm_template('taurus')
        self.assertIsNotNone(template)
        self.assertIn('JOB_NAME', template)
        self.assertIn('SIM_NAME', template)
        self.assertIn('SNAP_NUM', template)
        self.assertIn('SUBVOLS_LIST', template)
        self.assertIn('VERBOSE', template)

        with self.assertRaises(SystemExit):
            su.get_slurm_template('nonexistent_hpc')

    def test_create_slurm_script(self):
        """Test creating a SLURM script with placeholder substitution"""
        script_path, job_name = su.create_slurm_script(
            'taurus', 'GP20SU_1', 87, [0, 1],
            outdir=self.test_dir, verbose=True
        )
        
        # Check returned values
        self.assertEqual(job_name, 'prep_GP20SU_1_iz87_ivols0_1')
        self.assertTrue(script_path.endswith(f'submit_{job_name}.sh'))
        
        # Check file was created
        self.assertTrue(os.path.exists(script_path))
        
        # Check placeholders were replaced
        with open(script_path, 'r') as f:
            content = f.read()
        
        self.assertIn('prep_GP20SU_1_iz87_ivols0_1', content)
        self.assertIn('GP20SU_1', content)
        self.assertIn('87', content)
        self.assertIn('[0, 1]', content)
        self.assertIn('True', content)
        
        # Ensure placeholders are NOT present
        self.assertNotIn('JOB_NAME', content)
        self.assertNotIn('SIM_NAME', content)
        self.assertNotIn('SNAP_NUM', content)
        self.assertNotIn('SUBVOLS_LIST', content)
        self.assertNotIn('VERBOSE', content)

        # Ensure default output directory exists
        os.makedirs('output', exist_ok=True)
        
        script_path, job_name = su.create_slurm_script(
            'taurus', 'TestSim', 50, [0],
            outdir=None, verbose=False
        )
        
        # Check file was created in default 'output' directory
        self.assertTrue(script_path.startswith('output/'))
        self.assertTrue(os.path.exists(script_path))
        
        """Test creating a SLURM script with invalid HPC -> sys.exit()"""
        with self.assertRaises(SystemExit):
            su.create_slurm_script(
                'invalid_hpc', 'GP20SU_1', 87, [0],
                outdir=self.test_dir, verbose=True
            )
            
        # Clean up
        if os.path.exists(script_path):
            os.remove(script_path)

            
    def test_submit_slurm_job_no_sbatch(self):
        """Test submit_slurm_job when sbatch is not available"""
        # Check if sbatch is available
        import shutil
        if shutil.which('sbatch') is not None:
            self.skipTest("sbatch is available; skipping test to avoid submitting jobs")
        
        # Create a dummy script file
        dummy_script = os.path.join(self.test_dir, 'dummy_script.sh')
        with open(dummy_script, 'w') as f:
            f.write('#!/bin/sh\necho "test"')
        
        # This should handle the FileNotFoundError gracefully
        job_id = su.submit_slurm_job(dummy_script, 'test_job')
        
        # Should return None when sbatch is not found
        self.assertIsNone(job_id)

        
if __name__ == '__main__':
    unittest.main()
