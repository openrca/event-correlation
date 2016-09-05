import unittest
import sys

import numpy as np

from core import distribution
from core.distribution import NormalDistribution, UniformDistribution, KdeDistribution, \
    Distribution, StaticDistribution, ExponentialDistribution, SingularKernel


class TestScript(unittest.TestCase):
    def test_static(self):
        dist = StaticDistribution()
        self.assertEqual(0.5, dist.getPDFValue(0))
        self.assertEqual(0.5, dist.getRandom())
        self.assertEqual(0.5, dist.getRandom())
        self.assertEqual(0.5, dist.getCDFValue(0))
        self.assertEqual(0.5, dist.getCDFValue(0))

        dist = StaticDistribution([1, 2], [3, 4], [5, 6])
        self.assertEqual(1, dist.getPDFValue(0))
        self.assertEqual(2, dist.getPDFValue(0))
        self.assertEqual(1, dist.getPDFValue(0))
        self.assertEqual(3, dist.getCDFValue(0))
        self.assertEqual(4, dist.getCDFValue(0))
        self.assertEqual(3, dist.getCDFValue(0))
        self.assertEqual(5, dist.getRandom())
        self.assertEqual(6, dist.getRandom())
        self.assertEqual(5, dist.getRandom())
        self.assertEqual([6, 5], dist.getRandom(2))
        self.assertEqual("Static: pdf: [1 2] cdf: [3 4] rvs: [5 6]", str(dist))
        self.assertAlmostEqual(0.6931, dist.getDifferentialEntropy(), delta=1e-4)

    def test_normal(self):
        dist = NormalDistribution(0, 1)
        self.assertTrue(isinstance(dist, Distribution))
        self.assertIsNotNone(dist.getRandom())
        self.assertEqual("Norm: Mu: 0 Sigma: 1", str(dist))
        self.assertEqual(0.3989422804014327, dist.getPDFValue(0))
        self.assertEqual(0.5, dist.getCDFValue(0))
        self.assertAlmostEqual(1.4189, dist.getDifferentialEntropy(), delta=1e-4)

    def test_normal_invalid(self):
        with self.assertRaises(ValueError):
            NormalDistribution(0, 0)

    def test_uniform(self):
        dist = UniformDistribution(0, 1)
        self.assertTrue(isinstance(dist, Distribution))
        self.assertIsNotNone(dist.getRandom())
        self.assertEqual("Uniform: Lower: 0 Upper: 1", str(dist))
        self.assertEqual(1, dist.getPDFValue(1))
        self.assertEqual(0.5, dist.getCDFValue(0.5))
        self.assertEqual(0, dist.getDifferentialEntropy())

        dist = UniformDistribution(10, 20)
        self.assertAlmostEqual((10.05, 19.95), dist.getCompleteInterval())
        self.assertAlmostEqual(2.3025, dist.getDifferentialEntropy(), delta=1e-4)

    def test_uniform_invalid(self):
        with self.assertRaises(ValueError):
            UniformDistribution(0, 0)

    def test_exponential(self):
        dist = ExponentialDistribution(0, 4)
        self.assertEqual("Expon: Offset: 0 Beta: 4", str(dist))
        self.assertEqual(0.19470019576785122, dist.getPDFValue(1))
        self.assertEqual(0.1175030974154046, dist.getCDFValue(0.5))
        self.assertIsNotNone(dist.getRandom())
        self.assertAlmostEqual(2.3862, dist.getDifferentialEntropy(), delta=1e-4)

        dist = ExponentialDistribution(1, 4)
        self.assertEqual(0.25, dist.getPDFValue(1))
        self.assertAlmostEqual(2.3862, dist.getDifferentialEntropy(), delta=1e-4)

    def test_exponential_invalid(self):
        with self.assertRaises(ValueError):
            ExponentialDistribution(0, -1)

    def test_kde(self):
        dist = KdeDistribution(
            [0.53266987, -0.87911276, -0.79644153, 1.75727698, 1.50317041, -0.01320105, -1.69201415, 0.34473619,
             -0.37101994, 0.41408906, -1.48207759, 1.26757239, -1.17965448, 0.86855647, 0.68091169, 0.44812157,
             -1.79814044, -0.9382036, 2.14423779, 1.24949646, 1.14469027, -0.94722551, -1.37352194, 0.01401075,
             -0.03112311, 0.22938925, 0.38297998, 0.95724628, -1.45768742, -1.26986495, 1.97802286, 1.69753532,
             0.13657918, 1.36839824, 0.99223266, 0.31505398, -1.97223554, 0.4055926, -0.45988156, -1.5167463,
             -2.51696329, 1.33547539, 0.21477643, -1.76971538, 0.17066193, 0.51446341, -1.92688119, 1.5033893,
             1.63666092, 0.84641658, -0.69233096, 1.11054094, 0.63432753, -0.33795631, -0.29653928, 0.52413929,
             -1.98130907, -1.38801299, 0.67283854, -2.25337999, 2.38823015, -0.24633436, -1.22510007, 2.5473278,
             0.92711728, -2.41044273, -0.35810876, -1.21612683, -0.94402504, 0.14472338, 1.12300682, 0.36176913,
             1.05500101, -0.15193637, -0.00951187, 0.53088684, 0.53433872, -1.27196116, 0.35758436, -0.51375831,
             -0.91315794, -1.14780757, 0.45317547, -0.62264164, -1.58588465, -0.21322892, 0.19709141, 0.56991324,
             0.31440975, 0.54262837, 1.67869985, -0.67444796, 1.05131451, -0.24062371, -0.59172438, 0.54549846,
             -0.36441899, 0.2470415, 2.86109234, 1.22804002])
        self.assertAlmostEqual(0.3989, dist.getPDFValue(0), delta=0.1)
        self.assertAlmostEqual(0.5, dist.getCDFValue(0), delta=0.1)
        self.assertAlmostEqual(-1.4482, dist.getDifferentialEntropy(), delta=0.25)
        self.assertIsNotNone(dist.getRandom())

    def test_kde_invalid(self):
        with self.assertRaises(ValueError):
            KdeDistribution([])

    def test_asJson(self):
        dist = UniformDistribution(0, 1)
        expected = {"name": "Uniform", "param": (0, 1)}
        result = dist.asJson()
        self.assertEqual(expected, result)

    def test_getMaximumPDF(self):
        dist = NormalDistribution()
        self.assertEqual(0.3989422804014327, dist.getMaximumPDF())

    def test___eq__(self):
        dist1 = NormalDistribution()
        dist2 = NormalDistribution(2, 3)
        self.assertEqual(dist1, dist1)
        self.assertNotEqual(dist1, dist2)
        self.assertNotEqual(dist1, "a")

    def test_load(self):
        with self.assertRaises(ValueError):
            distribution.load("{\"name\": \"Norm\"}")
        with self.assertRaises(ValueError):
            distribution.load({"name": "foo", "param": [0]})

        normal = distribution.load({"name": "Norm", "param": [0, 1]})
        self.assertEqual(NormalDistribution(0, 1), normal)
        kde = distribution.load({'param': [[1, 2, 3, 4, 5]], 'name': 'Kde'})
        self.assertEqual(KdeDistribution([1, 2, 3, 4, 5]), kde)

    def test_kstest(self):
        dist1 = NormalDistribution()
        dist2 = NormalDistribution()
        with self.assertRaises(TypeError):
            distribution.kstest("a", dist2)
        with self.assertRaises(TypeError):
            distribution.kstest(dist1, "a")
        self.assertLess(distribution.kstest(dist1, dist2), 1)

    def test_approximateIntervalBorders(self):
        dist = UniformDistribution()
        lower, upper = distribution.approximateIntervalBorders(dist, 0.1)
        self.assertEqual(-10, lower)
        self.assertAlmostEqual(0.10, upper, delta=0.01)

    def test_chi2test(self):
        dist = NormalDistribution()
        self.assertLess(distribution.chi2test(dist, dist), 100000)

    def test_singularKernel(self):
        kernel = SingularKernel(value=0.0)
        self.assertEqual(sys.maxsize, kernel.evaluate(0))
        self.assertEqual(0, kernel.evaluate(1))
        self.assertTrue(np.all(np.array([sys.maxsize] * 5) == kernel.evaluate(np.zeros(5))))
        self.assertTrue(np.all(np.zeros(5) == kernel.evaluate(np.ones(5))))
        self.assertTrue(np.all(np.array([0, sys.maxsize, 0] == kernel.evaluate(np.array([1, 0, -1])))))

        self.assertTrue(np.all(np.zeros(5) == kernel.resample(5)))

        self.assertEqual(0, kernel.integrate_box_1d(-2, -1))
        self.assertEqual(1, kernel.integrate_box_1d(-1, 0))
        self.assertEqual(1, kernel.integrate_box_1d(0, 1))
        self.assertEqual(0, kernel.integrate_box_1d(1, 2))
        self.assertEqual(1, kernel.integrate_box_1d(-1, 1))


if __name__ == '__main__':
    unittest.main()
