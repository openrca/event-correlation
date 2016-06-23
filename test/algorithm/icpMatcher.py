import unittest

import numpy as np

from algorithms.icpMatcher import IcpMatcher


class TestScript(unittest.TestCase):
    def test_transform(self):
        points = np.array([[0, 0], [1, 1], [2, 2], [3, 3], [4, 4], [5, 5]])
        p = np.array([-0.5, 0.5])
        res = IcpMatcher.transform(p, points)
        self.assertTrue(
            np.array_equal(np.array([[-0.5, 0.5], [0.5, 1.5], [1.5, 2.5], [2.5, 3.5], [3.5, 4.5], [4.5, 5.5]]), res))

        res = IcpMatcher.transform(np.array([[1, 0, p[0]],
                                             [0, 1, p[1]]]), points)
        self.assertTrue(
            np.array_equal(np.array([[-0.5, 0.5], [0.5, 1.5], [1.5, 2.5], [2.5, 3.5], [3.5, 4.5], [4.5, 5.5]]), res))
