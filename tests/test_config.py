# python -m unittest tests/test_config.py 

import unittest
from unittest.mock import patch, mock_open
import sys
import os

import src.config as conf

class TestConfigFunctions(unittest.TestCase):
    def setUp(self):
        self.snap = 39
        self.valid_simtype = 'GP20'
        self.invalid_simtype = 'AAA'
        self.expected_keys = [
            'root', 'h0', 'omega0', 'omegab', 'lambda0', 
            'boxside', 'mp', 'mcold_disc', 'mcold_z_disc', 
            'mcold_burst', 'mcold_z_burst', 'snap',
            'selection', 'file_props'
        ]
        self.root = '/home/violeta/buds/emlines/gp20data/iz'+\
            str(self.snap)+'/ivol'
        self.localroot = '/cosma5/data/durham/dc-gonz3/Galform_Out/v2.7.0/stable/MillGas/gp19/'+'iz'+str(self.snap)+'/ivol'
        
    def test_get_config(self):
        # Check that config is returned as dictionary
        config = conf.get_config(self.valid_simtype,self.snap)
        self.assertIsInstance(config, dict)
       
        # Check that all expected keys are present
        for key in self.expected_keys:
            self.assertIn(key, config, f"Key '{key}' missing from config")

        # Test conf.get_config with invalid simulation type"""
        with self.assertRaises(ValueError) as context:
            conf.get_config(self.invalid_simtype,self.snap)
        error_msg = str(context.exception)
        self.assertIn(self.invalid_simtype, error_msg)
        self.assertIn("not supported", error_msg)
            
        # Test with localtest=True
        config = conf.get_config(self.valid_simtype,self.snap,
                                 localtest=True)
        self.assertEqual(self.root, config['root'])
        
        # Test with localtest=False (default)
        config = conf.get_config(self.valid_simtype,self.snap)
        self.assertEqual(self.localroot, config['root'])

    def test_get_GP20_config(self):
        config = conf.get_GP20_config(self.valid_simtype,self.snap)
        self.assertIsInstance(config, dict)
        self.assertEqual(config['h0'], 0.704)
        self.assertEqual(config['omega0'], 0.307)
        self.assertEqual(config['omegab'], 0.0482)
        self.assertEqual(config['lambda0'], 0.693)
        self.assertEqual(config['boxside'], 500.0)
        self.assertEqual(config['mp'], 9.35e8)
        self.assertEqual(config['mcold_disc'], 'mcold')
        self.assertEqual(config['mcold_z_disc'], 'cold_metal')
        self.assertEqual(config['mcold_burst'], 'mcold_burst')
        self.assertEqual(config['mcold_z_burst'], 'metals_burst')

        selection = config['selection']
        self.assertIn('galaxies.hdf5', selection)
        gal_selection = selection['galaxies.hdf5']
        self.assertEqual(gal_selection['group'], 'Output001')
        self.assertEqual(len(gal_selection['datasets']), 4)
        self.assertEqual(len(gal_selection['units']), 4)
        self.assertEqual(len(gal_selection['low_limits']), 4)
        self.assertEqual(len(gal_selection['high_limits']), 4)


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
