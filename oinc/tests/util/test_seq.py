###############################################################################
# test_seq.py                                                                 #
# Author: Jon Brandvein                                                       #
###############################################################################

"""Unit tests for the seq module."""


import unittest

from oinc.util.seq import *


class TestSeq(unittest.TestCase):
    
    def test_zip_strict(self):
        zip_strict([1, 2], [3, 4])
        
        with self.assertRaises(AssertionError):
            zip_strict([1, 2], [3, 4, 5])
    
    def test_no_duplicates(self):
        self.assertTrue(no_duplicates([1, 2, 3]))
        self.assertFalse(no_duplicates([1, 2, 2]))
    
    def test_get_duplicates(self):
        result = get_duplicates([1, 2, 3, 4, 2, 4, 5, 4])
        expected = [2, 4]
        self.assertEqual(result, expected)
    
    def test_elim_duplicates(self):
        result = elim_duplicates([1, 2, 3, 4, 2, 4, 5, 4])
        expected = [1, 2, 3, 4, 5]
        self.assertEqual(result, expected)
    
    def test_map_tuple(self):
        f = lambda x: 2 * x
        
        inputs = [
            4,
            (1, 2),
            [1, 2]
        ]
        
        expecteds = [
            8,
            (2, 4),
            [2, 4]
        ]
        
        for i in range(len(inputs)):
            result = map_tuple(f, inputs[i])
            self.assertEqual(result, expecteds[i],
                             msg='(In case ' + str(i) + ')')
    
    def test_map_tuple_rec(self):
        f = lambda x: 2 * x if isinstance(x, int) else x
        
        input = (1, (2, 3))
        norec_output = (2, (2, 3))
        rec_output = (2, (4, 6))
        
        self.assertEqual(map_tuple(f, input), norec_output)
        self.assertEqual(map_tuple_rec(f, input), rec_output)


if __name__ == '__main__':
    unittest.main()
