#python -m unittest tests/test_utils.py 

import unittest
import numpy as np
import h5py
import os
import tempfile
import shutil

import src.utils as u

class TestPredict(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures before running tests in the class"""
        # Create output directory if it doesn't exist
        output_dir = 'output'
        os.makedirs(output_dir, exist_ok=True)
        
        # Create a temporary directory under the output folder
        cls.test_dir = tempfile.mkdtemp(dir=output_dir)
        
        # Create test HDF5 file a 'data' group and 'type' dataset
        cls.hf5file = os.path.join(cls.test_dir, 'test_file.hdf5')
        with h5py.File(cls.hf5file, 'w') as f:
            data_group = f.create_group('data')
            type_data = np.array([1, 2, 3, 4, 5]) 
            data_group.create_dataset('type', data=type_data)
   
    @classmethod
    def tearDownClass(cls):
        """Clean up after all tests in the class are finished"""
        if os.path.exists(cls.test_dir):
            try:
                shutil.rmtree(cls.test_dir)
            except (OSError, PermissionError) as e:
                print(f"Warning: Could not remove test directory {cls.test_dir}: {e}")

    def test_get_path(self):
        path = u.get_path('/data/iz39/ivol', 5)
        self.assertEqual(path, '/data/iz39/ivol5/')

        path = u.get_path('/data/39/', 5)
        self.assertEqual(path, '/data/39/5/')
        
        path = u.get_path('/data/ivol', 5, ending='iz39/')
        self.assertEqual(path, '/data/ivol5/iz39/')

        
    def test_combined_mask(self):
        vb = False
        
        alldata = np.array([[0.,100.,200.]])
        low_lim = [0.]
        high_lim = [125.]
        mask = u.combined_mask(alldata,low_lim,high_lim,verbose=vb)
        np.testing.assert_array_equal(mask,[0,1])

        low_lim = [201.]
        mask = u.combined_mask(alldata,low_lim,high_lim,verbose=vb)
        self.assertEqual(mask,None)
        mask = u.combined_mask(alldata,low_lim,[None,None],verbose=vb)
        self.assertEqual(mask,None)
        
        alldata = np.array([[1.1,-3.,-50.],[0.,100.,200.],[1.,3.,5.]])
        low_lim = [None,None,3.]
        high_lim = [None,100,None]
        mask = u.combined_mask(alldata,low_lim,high_lim,verbose=vb)
        np.testing.assert_array_equal(mask,[1])


    def test_get_group_name(self):
        # Create subdirectories to simulate the volume/redshift structure
        vol_dir = os.path.join(self.test_dir, 'ivol0')
        os.makedirs(vol_dir, exist_ok=True)
        
        # Create iz directories with various snapshot numbers
        for iz in [128, 96, 78, 50]:
            os.makedirs(os.path.join(vol_dir, f'iz{iz}'), exist_ok=True)
        
        # Test: sorted descending is [128, 96, 78, 50]
        # snap=128 should be index 1 -> 'Output001'
        root = os.path.join(self.test_dir, 'ivol')
        result = u.get_group_name(root, 128)
        self.assertEqual(result, 'Output001')
        
        # snap=96 should be index 2 -> 'Output002'
        result = u.get_group_name(root, 96)
        self.assertEqual(result, 'Output002')
        
        # snap=50 should be index 4 -> 'Output004'
        result = u.get_group_name(root, '50')  # Test with string input
        self.assertEqual(result, 'Output004')
        
        # Test custom group_base and ndigits
        result = u.get_group_name(root, 78, group_base='Snap', ndigits=5)
        self.assertEqual(result, 'Snap00003')
        
        # Test with non-existent root
        result = u.get_group_name('/nonexistent/path/', 128)
        self.assertIsNone(result)
        
        # Test with root that has no iz directories
        empty_vol = os.path.join(self.test_dir, 'empty_vol')
        os.makedirs(empty_vol, exist_ok=True)
        result = u.get_group_name(os.path.join(self.test_dir, 'empty_'), 128)
        self.assertIsNone(result)

        
    def test_check_h5_structure(self):
        vb = False
        ss = u.check_h5_structure('notfile',['type'],verbose=vb)
        self.assertEqual(False,ss)

        ss = u.check_h5_structure(self.hf5file,['type'],
                                   group='non',verbose=vb)
        self.assertEqual(False,ss)
        
        ss = u.check_h5_structure(self.hf5file,['type'],verbose=vb)
        self.assertEqual(False,ss)
        
        ss = u.check_h5_structure(self.hf5file,['type'],
                                   group='data',verbose=vb)
        self.assertEqual(True,ss)
        
if __name__ == '__main__':
    unittest.main()
