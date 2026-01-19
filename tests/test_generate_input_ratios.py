# python -m unittest tests/test_generate_input_ratios.py

import unittest
import tempfile
import shutil
import os
import h5py
import numpy as np
import sys

from src.generate_input import generate_input_file

class TestLuminosityRatioCalculation(unittest.TestCase):
    """Test cases for luminosity ratio calculation"""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create temporary directories for input and output
        self.test_dir = tempfile.mkdtemp()
        self.input_dir = os.path.join(self.test_dir, 'input', '0')
        self.output_dir = os.path.join(self.test_dir, 'output', '0')
        os.makedirs(self.input_dir)
        
        # Define test lines
        self.lines = ['Halpha', 'Hbeta', 'OII3727']
        self.line_prefix = 'L_tot_'
        self.line_suffix_ext = '_ext'
        
        # Create test data with known values
        self.n_galaxies = 100
        np.random.seed(42)  # For reproducibility
        
        # Create luminosity data: L values and L_ext values
        self.L_values = {}
        self.L_ext_values = {}
        self.expected_ratios = {}
        
        for line in self.lines:
            # Base luminosity (some zeros to test edge cases)
            L = np.random.uniform(1e38, 1e42, self.n_galaxies)
            L[0:5] = 0.0  # First 5 galaxies have zero luminosity
            
            # ratio = L_ext/L
            Lratio = np.random.uniform(0.1, 0.9, self.n_galaxies)
            L_ext = L * Lratio
            self.L_values[line] = L
            self.L_ext_values[line] = L_ext
            
            # Expected ratio: L_ext / L (should be 0 where L=0)
            expected = np.zeros(self.n_galaxies)
            valid = L > 0
            expected[valid] = L_ext[valid] / L[valid]
            self.expected_ratios[line] = expected
        
        # Create mock input HDF5 files
        self._create_mock_input_files()
        
        # Create test configuration
        self.config = self._create_test_config()
    
    def tearDown(self):
        """Clean up test fixtures after each test method."""
        shutil.rmtree(self.test_dir)
    
    def _create_mock_input_files(self):
        """Create mock HDF5 input files with test data"""
        # Create galaxies.hdf5 with selection data
        gal_file = os.path.join(self.input_dir, 'galaxies.hdf5')
        with h5py.File(gal_file, 'w') as f:
            grp = f.create_group('Output001')
            # Selection datasets
            grp.create_dataset('mhhalo', data=np.ones(self.n_galaxies) * 1e12)
            grp.create_dataset('xgal', data=np.random.uniform(0, 100, self.n_galaxies))
            grp.create_dataset('ygal', data=np.random.uniform(0, 100, self.n_galaxies))
            grp.create_dataset('zgal', data=np.random.uniform(0, 100, self.n_galaxies))
            # Other required datasets
            grp.create_dataset('redshift', data=0.5)
            grp.create_dataset('index', data=np.arange(self.n_galaxies))
            grp.create_dataset('type', data=np.zeros(self.n_galaxies))
            # Metallicity datasets
            grp.create_dataset('mcold', data=np.ones(self.n_galaxies) * 1e9)
            grp.create_dataset('cold_metal', data=np.ones(self.n_galaxies) * 1e7)
            grp.create_dataset('mcold_burst', data=np.ones(self.n_galaxies) * 1e8)
            grp.create_dataset('metals_burst', data=np.ones(self.n_galaxies) * 1e6)
        
        # Create tosedfit.hdf5 with luminosity data
        sed_file = os.path.join(self.input_dir, 'tosedfit.hdf5')
        with h5py.File(sed_file, 'w') as f:
            grp = f.create_group('Output001')
            for line in self.lines:
                L_name = f"{self.line_prefix}{line}"
                L_ext_name = f"{self.line_prefix}{line}{self.line_suffix_ext}"
                grp.create_dataset(L_name, data=self.L_values[line])
                grp.create_dataset(L_ext_name, data=self.L_ext_values[line])
    
    def _create_test_config(self):
        """Create test configuration dictionary"""
        return {
            'root': os.path.join(self.test_dir, 'input', 'ivol'),
            'outroot': os.path.join(self.test_dir, 'output', 'ivol'),
            'h0': 0.7,
            'omega0': 0.3,
            'omegab': 0.05,
            'lambda0': 0.7,
            'boxside': 125.0,
            'mp': 1e9,
            'snap': 39,
            'mcold_disc': 'mcold',
            'mcold_z_disc': 'cold_metal',
            'mcold_burst': 'mcold_burst',
            'mcold_z_burst': 'metals_burst',
            'lines': self.lines,
            'line_prefix': self.line_prefix,
            'line_suffix_ext': self.line_suffix_ext,
            'selection': {
                'galaxies.hdf5': {
                    'group': 'Output001',
                    'datasets': ['mhhalo', 'xgal', 'ygal', 'zgal'],
                    'units': ['Msun/h', 'Mpc/h', 'Mpc/h', 'Mpc/h'],
                    'low_limits': [1e10, 0., 0., 0.],
                    'high_limits': [None, 125., 125., 125.]
                }
            },
            'file_props': {
                'galaxies.hdf5': {
                    'group': 'Output001',
                    'datasets': ['redshift', 'index', 'type',
                                 'mcold', 'mcold_burst', 'cold_metal', 'metals_burst'],
                    'units': ['redshift', 'index', 'type',
                              'Msun/h', 'Msun/h', 'Msun/h', 'Msun/h']
                },
                'tosedfit.hdf5': {
                    'group': 'Output001',
                    'datasets': self._get_line_datasets(),
                    'units': ['1e40 h^2 erg/s'] * len(self._get_line_datasets())
                }
            }
        }
    
    def _get_line_datasets(self):
        """Generate list of luminosity dataset names"""
        datasets = []
        for line in self.lines:
            datasets.append(f"{self.line_prefix}{line}")
            datasets.append(f"{self.line_prefix}{line}{self.line_suffix_ext}")
        return datasets
    
    def test_ratio_calculation_correctness(self):
        """Test that ratios are correctly calculated as L_ext / L"""
        # Modify config to use correct paths (without 'ivol' in the path)
        self.config['root'] = os.path.join(self.test_dir, 'input', '')
        self.config['outroot'] = os.path.join(self.test_dir, 'output', '')
        
        # Run the function
        result = generate_input_file(self.config, ivol=0, verbose=False)
        self.assertTrue(result, "generate_input_file should return True")
        
        # Read the output file and verify ratios
        outfile = os.path.join(self.test_dir, 'output', '0', 'gne_input.hdf5')
        self.assertTrue(os.path.exists(outfile), f"Output file should exist: {outfile}")
        
        with h5py.File(outfile, 'r') as f:
            data = f['data']
            gal_index = data['gal_index'][:].astype(int)  # Get the mask indices as int
            
            for line in self.lines:
                ratio_name = f"ratio_{line}"
                self.assertIn(ratio_name, data, f"Ratio dataset {ratio_name} should exist")
                calculated_ratio = data[ratio_name][:]
                
                # Get the expected ratio for the selected galaxies
                L_selected = self.L_values[line][gal_index]
                L_ext_selected = self.L_ext_values[line][gal_index]
                expected_ratio = np.zeros(len(gal_index))
                valid = L_selected > 0
                expected_ratio[valid] = L_ext_selected[valid]/L_selected[valid]
                
                # Check that ratios match (within floating point tolerance)
                np.testing.assert_allclose(
                    calculated_ratio, expected_ratio,
                    rtol=1e-10, atol=1e-15,
                    err_msg=f"Ratio mismatch for {line}"
                )
    
    def test_ratio_zero_luminosity_handling(self):
        """Test that ratios are 0 where base luminosity is 0"""
        self.config['root'] = os.path.join(self.test_dir, 'input', '')
        self.config['outroot'] = os.path.join(self.test_dir, 'output', '')
        
        result = generate_input_file(self.config, ivol=0, verbose=False)
        self.assertTrue(result)
        
        outfile = os.path.join(self.test_dir, 'output', '0', 'gne_input.hdf5')
        
        with h5py.File(outfile, 'r') as f:
            data = f['data']
            gal_index = data['gal_index'][:].astype(int)  # Get the mask indices as int
            
            for line in self.lines:
                ratio_name = f"ratio_{line}"
                calculated_ratio = data[ratio_name][:]
                
                # Get the L values that were selected by the mask
                L_selected = self.L_values[line][gal_index]
                
                # Check that ratios are 0 where L was 0
                zero_L_mask = L_selected == 0
                if np.any(zero_L_mask):
                    self.assertTrue(
                        np.all(calculated_ratio[zero_L_mask] == 0),
                        f"Ratio should be 0 where L=0 for {line}"
                    )
    
    def test_ratio_units_attribute(self):
        """Test that ratio datasets have correct units attribute"""
        self.config['root'] = os.path.join(self.test_dir, 'input', '')
        self.config['outroot'] = os.path.join(self.test_dir, 'output', '')
        
        result = generate_input_file(self.config, ivol=0, verbose=False)
        self.assertTrue(result)
        
        outfile = os.path.join(self.test_dir, 'output', '0', 'gne_input.hdf5')
        
        with h5py.File(outfile, 'r') as f:
            data = f['data']
            
            for line in self.lines:
                ratio_name = f"ratio_{line}"
                units = data[ratio_name].attrs['units']
                self.assertEqual(units, 'L_ext/L (dimensionless)',
                               f"Units should be 'L_ext/L (dimensionless)' for {ratio_name}")
    
    def test_base_luminosity_written_to_output(self):
        """Test that base luminosity L is written to output file"""
        self.config['root'] = os.path.join(self.test_dir, 'input', '')
        self.config['outroot'] = os.path.join(self.test_dir, 'output', '')
        
        result = generate_input_file(self.config, ivol=0, verbose=False)
        self.assertTrue(result)
        
        outfile = os.path.join(self.test_dir, 'output', '0', 'gne_input.hdf5')
        
        with h5py.File(outfile, 'r') as f:
            data = f['data']
            
            for line in self.lines:
                L_name = f"{self.line_prefix}{line}"
                self.assertIn(L_name, data, 
                            f"Base luminosity {L_name} should be written to output")
    
    def test_ext_luminosity_not_separately_written(self):
        """Test that L_ext is NOT separately written (only ratio is stored)"""
        self.config['root'] = os.path.join(self.test_dir, 'input', '')
        self.config['outroot'] = os.path.join(self.test_dir, 'output', '')
        
        result = generate_input_file(self.config, ivol=0, verbose=False)
        self.assertTrue(result)
        
        outfile = os.path.join(self.test_dir, 'output', '0', 'gne_input.hdf5')
        
        with h5py.File(outfile, 'r') as f:
            data = f['data']
            
            for line in self.lines:
                L_ext_name = f"{self.line_prefix}{line}{self.line_suffix_ext}"
                self.assertNotIn(L_ext_name, data, 
                               f"Extended luminosity {L_ext_name} should NOT be in output")


class TestLuminosityRatioEdgeCases(unittest.TestCase):
    """Test edge cases for luminosity ratio calculation"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = tempfile.mkdtemp()
        self.input_dir = os.path.join(self.test_dir, 'input', '0')
        os.makedirs(self.input_dir)
        
        self.lines = ['Halpha']
        self.line_prefix = 'L_tot_'
        self.line_suffix_ext = '_ext'
        self.n_galaxies = 50
    
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.test_dir)
    
    def _create_config(self):
        """Create minimal test configuration"""
        return {
            'root': os.path.join(self.test_dir, 'input', ''),
            'outroot': os.path.join(self.test_dir, 'output', ''),
            'h0': 0.7,
            'omega0': 0.3,
            'omegab': 0.05,
            'lambda0': 0.7,
            'boxside': 125.0,
            'mp': 1e9,
            'snap': 39,
            'mcold_disc': 'mcold',
            'mcold_z_disc': 'cold_metal',
            'mcold_burst': 'mcold_burst',
            'mcold_z_burst': 'metals_burst',
            'lines': self.lines,
            'line_prefix': self.line_prefix,
            'line_suffix_ext': self.line_suffix_ext,
            'selection': {
                'galaxies.hdf5': {
                    'group': 'Output001',
                    'datasets': ['mhhalo', 'xgal', 'ygal', 'zgal'],
                    'units': ['Msun/h', 'Mpc/h', 'Mpc/h', 'Mpc/h'],
                    'low_limits': [1e10, 0., 0., 0.],
                    'high_limits': [None, 125., 125., 125.]
                }
            },
            'file_props': {
                'galaxies.hdf5': {
                    'group': 'Output001',
                    'datasets': ['redshift', 'mcold', 'cold_metal', 
                                 'mcold_burst', 'metals_burst'],
                    'units': ['redshift', 'Msun/h', 'Msun/h', 'Msun/h', 'Msun/h']
                },
                'tosedfit.hdf5': {
                    'group': 'Output001',
                    'datasets': ['L_tot_Halpha', 'L_tot_Halpha_ext'],
                    'units': ['1e40 erg/s', '1e40 erg/s']
                }
            }
        }
    
    def _create_input_files(self, L_values, L_ext_values):
        """Create input files with specific luminosity values"""
        gal_file = os.path.join(self.input_dir, 'galaxies.hdf5')
        with h5py.File(gal_file, 'w') as f:
            grp = f.create_group('Output001')
            grp.create_dataset('mhhalo', data=np.ones(self.n_galaxies) * 1e12)
            grp.create_dataset('xgal', data=np.random.uniform(0, 100, self.n_galaxies))
            grp.create_dataset('ygal', data=np.random.uniform(0, 100, self.n_galaxies))
            grp.create_dataset('zgal', data=np.random.uniform(0, 100, self.n_galaxies))
            grp.create_dataset('redshift', data=0.5)
            grp.create_dataset('mcold', data=np.ones(self.n_galaxies) * 1e9)
            grp.create_dataset('cold_metal', data=np.ones(self.n_galaxies) * 1e7)
            grp.create_dataset('mcold_burst', data=np.ones(self.n_galaxies) * 1e8)
            grp.create_dataset('metals_burst', data=np.ones(self.n_galaxies) * 1e6)
        
        sed_file = os.path.join(self.input_dir, 'tosedfit.hdf5')
        with h5py.File(sed_file, 'w') as f:
            grp = f.create_group('Output001')
            grp.create_dataset('L_tot_Halpha', data=L_values)
            grp.create_dataset('L_tot_Halpha_ext', data=L_ext_values)
    
    def test_ratio_all_zeros(self):
        """Test ratio calculation when all L values are zero"""
        L = np.zeros(self.n_galaxies)
        L_ext = np.zeros(self.n_galaxies)
        self._create_input_files(L, L_ext)
        
        config = self._create_config()
        result = generate_input_file(config, ivol=0, verbose=False)
        self.assertTrue(result)
        
        outfile = os.path.join(self.test_dir, 'output', '0', 'gne_input.hdf5')
        with h5py.File(outfile, 'r') as f:
            gal_index = f['data']['gal_index'][:].astype(int)
            ratio = f['data']['ratio_Halpha'][:]
            # All ratios should be 0 when L=0
            np.testing.assert_array_equal(ratio, np.zeros(len(gal_index)),
                                         "All ratios should be 0 when L=0")
    
    def test_ratio_unity(self):
        """Test ratio calculation when L_ext equals L (ratio should be 1)"""
        L = np.ones(self.n_galaxies) * 1e40
        L_ext = L.copy()  # Same values, ratio should be 1
        self._create_input_files(L, L_ext)
        
        config = self._create_config()
        result = generate_input_file(config, ivol=0, verbose=False)
        self.assertTrue(result)
        
        outfile = os.path.join(self.test_dir, 'output', '0', 'gne_input.hdf5')
        with h5py.File(outfile, 'r') as f:
            gal_index = f['data']['gal_index'][:].astype(int)
            ratio = f['data']['ratio_Halpha'][:]
            np.testing.assert_allclose(ratio, np.ones(len(gal_index)),
                                      rtol=1e-10,
                                      err_msg="Ratios should be 1 when L_ext=L")
    
    def test_ratio_specific_values(self):
        """Test ratio with specific known values"""
        L = np.array([100.0, 200.0, 50.0, 0.0, 1000.0] * 10)
        L_ext = np.array([50.0, 100.0, 25.0, 0.0, 800.0] * 10)
        expected_full = np.array([0.5, 0.5, 0.5, 0.0, 0.8] * 10)
        
        self._create_input_files(L, L_ext)
        
        config = self._create_config()
        result = generate_input_file(config, ivol=0, verbose=False)
        self.assertTrue(result)
        
        outfile = os.path.join(self.test_dir, 'output', '0', 'gne_input.hdf5')
        with h5py.File(outfile, 'r') as f:
            gal_index = f['data']['gal_index'][:].astype(int)
            ratio = f['data']['ratio_Halpha'][:]
            expected = expected_full[gal_index]
            np.testing.assert_allclose(ratio, expected, rtol=1e-10,
                                      err_msg="Ratios should match expected values")


if __name__ == '__main__':
    unittest.main(verbosity=2)
