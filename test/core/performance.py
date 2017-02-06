import unittest

import numpy as np

from core.performance import PearsonCoefficient, DistanceCorrelation, EnergyDistance


class TestScript(unittest.TestCase):
    list1 = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15])
    list2 = np.array([-8, -72, 80, -9, -8, 25, -54, 65, 52, -1, -72, 66, 91, -65, -73])

    def testPearsonCoefficient(self):
        a = np.array(
            [5.1, 4.9, 4.7, 4.6, 5.0, 5.4, 4.6, 5.0, 4.4, 4.9, 5.4, 4.8, 4.8, 4.3, 5.8, 5.7, 5.4, 5.1, 5.7, 5.1, 5.4,
             5.1, 4.6, 5.1, 4.8, 5.0, 5.0, 5.2, 5.2, 4.7, 4.8, 5.4, 5.2, 5.5, 4.9, 5.0, 5.5, 4.9, 4.4, 5.1, 5.0, 4.5,
             4.4, 5.0, 5.1, 4.8, 5.1, 4.6, 5.3, 5.0])
        b = np.array(
            [7.0, 6.4, 6.9, 5.5, 6.5, 5.7, 6.3, 4.9, 6.6, 5.2, 5.0, 5.9, 6.0, 6.1, 5.6, 6.7, 5.6, 5.8, 6.2, 5.6, 5.9,
             6.1, 6.3, 6.1, 6.4, 6.6, 6.8, 6.7, 6.0, 5.7, 5.5, 5.5, 5.8, 6.0, 5.4, 6.0, 6.7, 6.3, 5.6, 5.5, 5.5, 6.1,
             5.8, 5.0, 5.6, 5.7, 5.7, 6.2, 5.1, 5.7])

        res = PearsonCoefficient().compute(a, b)
        # correct value created by scipy.stats.pearsonr
        self.assertAlmostEqual(0.91915027298242991, res[0])
        self.assertAlmostEqual(0.57674252108659729, res[1])

    def testDistanceCorrelation(self):
        a = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        b = np.array([-1, 2, -3, 4, -5, 6, -7, 8, -9, 10])

        res = DistanceCorrelation().compute(a, b)
        # correct value created by R's 'energy' package (dcor)
        self.assertAlmostEqual(0.46821276026821812, res[0])
        self.assertAlmostEqual(0.3, res[1], delta=0.05)

    def testEnergyDistance(self):
        a = np.array(
            [5.1, 4.9, 4.7, 4.6, 5.0, 5.4, 4.6, 5.0, 4.4, 4.9, 5.4, 4.8, 4.8, 4.3, 5.8, 5.7, 5.4, 5.1, 5.7, 5.1, 5.4,
             5.1, 4.6, 5.1, 4.8, 5.0, 5.0, 5.2, 5.2, 4.7, 4.8, 5.4, 5.2, 5.5, 4.9, 5.0, 5.5, 4.9, 4.4, 5.1, 5.0, 4.5,
             4.4, 5.0, 5.1, 4.8, 5.1, 4.6, 5.3, 5.0])
        b = np.array(
            [7.0, 6.4, 6.9, 5.5, 6.5, 5.7, 6.3, 4.9, 6.6, 5.2, 5.0, 5.9, 6.0, 6.1, 5.6, 6.7, 5.6, 5.8, 6.2, 5.6, 5.9,
             6.1, 6.3, 6.1, 6.4, 6.6, 6.8, 6.7, 6.0, 5.7, 5.5, 5.5, 5.8, 6.0, 5.4, 6.0, 6.7, 6.3, 5.6, 5.5, 5.5, 6.1,
             5.8, 5.0, 5.6, 5.7, 5.7, 6.2, 5.1, 5.7])

        res = EnergyDistance().compute(a, b)
        # correct value created by R's 'energy' package (eqdist.etest)
        self.assertAlmostEqual(0.49413184617945721, res[0])
        self.assertEqual(1, res[1])

    def testPValues(self):
        res = PearsonCoefficient().compute(self.list1, self.list1)
        self.assertLess(res[1], 0.05)
        res = PearsonCoefficient().compute(self.list1, self.list2)
        self.assertGreater(res[1], 0.05)

        res = DistanceCorrelation().compute(self.list1, self.list1)
        self.assertLess(res[1], 0.05)
        res = DistanceCorrelation().compute(self.list1, self.list2)
        self.assertGreater(res[1], 0.05)

        res = EnergyDistance().compute(self.list1, self.list1)
        self.assertLess(res[1], 0.05)
        res = EnergyDistance().compute(self.list1, self.list2)
        self.assertGreater(res[1], 0.05)

    def testScores(self):
        res = PearsonCoefficient().compute(self.list1, self.list1)
        self.assertLess(res[0], 0.5)
        res = PearsonCoefficient().compute(self.list1, self.list2)
        self.assertGreater(res[0], 0.5)

        res = DistanceCorrelation().compute(self.list1, self.list1)
        self.assertLess(res[0], 0.5)
        res = DistanceCorrelation().compute(self.list1, self.list2)
        self.assertGreater(res[0], 0.5)

        res = EnergyDistance().compute(self.list1, self.list1)
        self.assertLess(res[1], 0.5)
        res = EnergyDistance().compute(self.list1, self.list2)
        self.assertGreater(res[1], 0.5)
