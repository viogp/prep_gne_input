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
