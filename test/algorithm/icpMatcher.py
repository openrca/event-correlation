import unittest

import numpy as np

from algorithms import RESULT_MU
from algorithms.icpMatcher import IcpMatcher


class TestScript(unittest.TestCase):
    def test_square(self):
        a = np.array([5, 20, 27])
        b = np.array([12, 25, 32])

        matcher = IcpMatcher()
        matcher.trimCost = False
        res = matcher._compute(a, b)
        self.assertAlmostEqual(res[RESULT_MU], 17 / 3)
