# python -m unittest tests/test_config.py 

import unittest
from unittest.mock import patch, mock_open
import sys
import os

import src.config as conf

class TestConfigFunctions(unittest.TestCase):
    def setUp(self):
        self.snap = 39
        self.subvols = [0]
        self.valid_simtype = 'GP20cosma'
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
        config = conf.get_config(self.valid_simtype, self.snap, self.subvols)
        self.assertIsInstance(config, dict)
       
        # Check that all expected keys are present
        for key in self.expected_keys:
            self.assertIn(key, config, f"Key '{key}' missing from config")

        # Test conf.get_config with invalid simulation type"""
        with self.assertRaises(ValueError) as context:
            conf.get_config(self.invalid_simtype, self.snap, self.subvols)
        error_msg = str(context.exception)
        self.assertIn(self.invalid_simtype, error_msg)
        self.assertIn("not supported", error_msg)
            
        # Test with localtest=True
        config = conf.get_config(self.valid_simtype, self.snap, self.subvols,
                                 laptop=True)
        self.assertEqual(self.root, config['root'])
        
        # Test with localtest=False (default)
        config = conf.get_config(self.valid_simtype, self.snap, self.subvols)
        self.assertEqual(self.localroot, config['root'])

    def test_get_GP20cosma_config(self):
        config = conf.get_GP20cosma_config(self.snap, self.subvols)
        self.assertIsInstance(config, dict)
        self.assertEqual(config['h0'], 0.704)
        self.assertEqual(config['omega0'], 0.307)
        self.assertEqual(config['omegab'], 0.0482)
        self.assertEqual(config['lambda0'], 0.693)
        self.assertEqual(config['boxside'], 125.0)
        self.assertEqual(config['mp'], 9.35e8)
        self.assertEqual(config['mcold_disc'], 'mcold')
        self.assertEqual(config['mcold_z_disc'], 'cold_metal')
        self.assertEqual(config['mcold_burst'], 'mcold_burst')
        self.assertEqual(config['mcold_z_burst'], 'metals_burst')

        selection = config['selection']
        self.assertIn('galaxies.hdf5', selection)
        gal_selection = selection['galaxies.hdf5']
        self.assertEqual(gal_selection['group'], 'Output###')
        self.assertEqual(len(gal_selection['datasets']), 4)
        self.assertEqual(len(gal_selection['units']), 4)
        self.assertEqual(len(gal_selection['low_limits']), 4)
        self.assertEqual(len(gal_selection['high_limits']), 4)

    def test_get_SharkSU_config(self):
        # Test SharkSU config
        # default cosmo_var='1'
        config = conf.get_SharkSU_config(self.snap, self.subvols, cosmo_var='1')
        self.assertIsInstance(config, dict)
        self.assertEqual(config['mp'], 0) # Shark mp is 0
        self.assertEqual(config['boxside'], 250)
        self.assertEqual(config['mcold_disc'], 'mgas_disk')
        
        # Check selection keys for Shark
        selection = config['selection']
        self.assertIn('galaxies.hdf5', selection)
        gal_selection = selection['galaxies.hdf5']
        self.assertEqual(gal_selection['group'], 'galaxies')

        # Check file_props
        file_props = config['file_props']
        self.assertIn('galaxies.hdf5', file_props)
        self.assertEqual(file_props['galaxies.hdf5']['group'], 'galaxies')
        datasets = file_props['galaxies.hdf5']['datasets']
        self.assertIn('id_halo', datasets)
        self.assertIn('mstars_disk', datasets)

        # Test cosmo_var='2'
        config2 = conf.get_SharkSU_config(self.snap, self.subvols, cosmo_var='2')
        self.assertIn('SU2', config2['outroot'])
        
        # Test invalid cosmo_var
        with self.assertRaises(ValueError):
            conf.get_SharkSU_config(self.snap, self.subvols, cosmo_var='999')

    def test_get_SharkUNIT1Gpc_config(self):
        # Test SharkUNIT1Gpc config
        # default cosmo_var='fnl0'
        config = conf.get_SharkUNIT1Gpc_config(self.snap, self.subvols, cosmo_var='fnl0')
        self.assertIsInstance(config, dict)
        self.assertEqual(config['mp'], 0)
        self.assertEqual(config['boxside'], 1000)
        
        # Check paths
        self.assertIn('UNIT1GPC_fnl0', config['outroot'])
        
        # Test cosmo_var='fnl100'
        config2 = conf.get_SharkUNIT1Gpc_config(self.snap, self.subvols, cosmo_var='fnl100')
        self.assertIn('UNIT1GPC_fnl100', config2['outroot'])

        # Test invalid cosmo_var
        with self.assertRaises(ValueError):
            conf.get_SharkUNIT1Gpc_config(self.snap, self.subvols, cosmo_var='invalid')

if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
