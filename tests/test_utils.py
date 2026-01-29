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


    def test_get_zz_subvols(self):
        vb = False    
        # Create multiple subvolume directories with matching iz subdirectories
        for ivol in [0, 1, 2]:
            vol_dir = os.path.join(self.test_dir, f'subvol{ivol}')
            os.makedirs(vol_dir, exist_ok=True)
            for iz in [100, 75, 50, 25]:
                os.makedirs(os.path.join(vol_dir, f'iz{iz}'), exist_ok=True)
        
        # Test: all subvolumes have matching iz directories
        root = os.path.join(self.test_dir, 'subvol')
        result = u.get_zz_subvols(root, [0, 1, 2], verbose=vb)
        self.assertEqual(result, [100, 75, 50, 25])
        
        # Test: some subvolumes don't exist (should skip them)
        result = u.get_zz_subvols(root, [0, 5, 6], verbose=vb)
        self.assertEqual(result, [100, 75, 50, 25])
        
        # Test: single valid subvolume
        result = u.get_zz_subvols(root, [1], verbose=vb)
        self.assertEqual(result, [100, 75, 50, 25])
        
        # Test: custom dir_base
        vol_custom = os.path.join(self.test_dir, 'customvol0')
        os.makedirs(vol_custom, exist_ok=True)
        for snap in [10, 20, 30]:
            os.makedirs(os.path.join(vol_custom, f'snap{snap}'), exist_ok=True)
        
        root_custom = os.path.join(self.test_dir, 'customvol')
        result = u.get_zz_subvols(root_custom, [0], dir_base='snap', verbose=vb)
        self.assertEqual(result, [30, 20, 10])
        
        # Test: no valid directories -> sys.exit(1)
        with self.assertRaises(SystemExit) as cm:
            u.get_zz_subvols('/nonexistent/path/', [0, 1], verbose=vb)
        self.assertEqual(cm.exception.code, 1)
        
        # Test: subvolumes exist but have no iz directories -> sys.exit(1)
        empty_vol = os.path.join(self.test_dir, 'emptyvol0')
        os.makedirs(empty_vol, exist_ok=True)
        with self.assertRaises(SystemExit) as cm:
            u.get_zz_subvols(os.path.join(self.test_dir, 'emptyvol'), [0], verbose=vb)
        self.assertEqual(cm.exception.code, 1)
        
        # Test: mismatched iz directories between subvolumes -> sys.exit(1)
        mismatch_vol0 = os.path.join(self.test_dir, 'mismatchvol0')
        mismatch_vol1 = os.path.join(self.test_dir, 'mismatchvol1')
        os.makedirs(mismatch_vol0, exist_ok=True)
        os.makedirs(mismatch_vol1, exist_ok=True)
        for iz in [100, 50]:
            os.makedirs(os.path.join(mismatch_vol0, f'iz{iz}'), exist_ok=True)
        for iz in [100, 75]:  # Different from vol0
            os.makedirs(os.path.join(mismatch_vol1, f'iz{iz}'), exist_ok=True)
        
        with self.assertRaises(SystemExit) as cm:
            u.get_zz_subvols(os.path.join(self.test_dir, 'mismatchvol'), [0, 1], verbose=vb)
        self.assertEqual(cm.exception.code, 1)
        
        
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
