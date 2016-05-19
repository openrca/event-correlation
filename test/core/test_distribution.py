import unittest

import core.distribution
from core.distribution import NormalDistribution, PowerLawDistribution, UniformDistribution


class TestScript(unittest.TestCase):
    def test_abstract(self):
        dist = core.distribution.Distribution(None, None)
        self.assertIsNone(dist.getRandom())
        self.assertIsNone(dist.getCDFValue(0))
        self.assertIsNone(dist.getPDFValue(0))

    def test_static(self):
        dist = core.distribution.StaticDistribution()
        self.assertEqual(0.5, dist.getPDFValue(0))
        self.assertEqual(0.5, dist.getRandom())
        self.assertEqual(0.5, dist.getRandom())
        self.assertEqual(0.5, dist.getCDFValue(0))
        self.assertEqual(0.5, dist.getCDFValue(0))

        dist = core.distribution.StaticDistribution([1, 2], [3, 4], [5, 6])
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
        self.assertEqual("Static: pdf: [1, 2]\t cdf: [3, 4]\t rvs: [5, 6]", str(dist))

    def test_normal(self):
        dist = core.distribution.NormalDistribution(0, 1)
        self.assertTrue(isinstance(dist, core.distribution.Distribution))
        self.assertIsNotNone(dist.getRandom())
        self.assertEqual("Norm: Mu: 0\t Sigma: 1", str(dist))
        self.assertEqual(0.3989422804014327, dist.getPDFValue(0))
        self.assertEqual(0.5, dist.getCDFValue(0))

    def test_normal_invalid(self):
        with self.assertRaises(ValueError):
            core.distribution.NormalDistribution(0, 0)

    def test_uniform(self):
        dist = core.distribution.UniformDistribution(0, 1)
        self.assertTrue(isinstance(dist, core.distribution.Distribution))
        self.assertIsNotNone(dist.getRandom())
        self.assertEqual("Uniform: Lower: 0\t Upper: 1", str(dist))
        self.assertEqual(1, dist.getPDFValue(1))
        self.assertEqual(0.5, dist.getCDFValue(0.5))

        dist = core.distribution.UniformDistribution(10, 20)
        self.assertEqual((10, 20), dist.dist.interval(1))

    def test_uniform_invalid(self):
        with self.assertRaises(ValueError):
            core.distribution.UniformDistribution(0, 0)

    def test_powerlaw(self):
        dist = core.distribution.PowerLawDistribution(1, 0)
        self.assertTrue(isinstance(dist, core.distribution.Distribution))
        self.assertIsNotNone(dist.getRandom())
        self.assertEqual("Powerlaw: Exponent: 1", str(dist))
        self.assertEqual(1, dist.getPDFValue(1))
        self.assertEqual(0.5, dist.getCDFValue(0.5))

    def test_powerlaw_invalid(self):
        with self.assertRaises(ValueError):
            core.distribution.PowerLawDistribution(0)

    def test_exponential(self):
        dist = core.distribution.ExponentialDistribution(0, 4)
        self.assertEqual("Expon: Offset: 0\t Lambda: 4", str(dist))
        self.assertEqual(0.19470019576785122, dist.getPDFValue(1))
        self.assertEqual(0.1175030974154046, dist.getCDFValue(0.5))
        self.assertIsNotNone(dist.getRandom())

        dist = core.distribution.ExponentialDistribution(1, 4)
        self.assertEqual(0.25, dist.getPDFValue(1))

    def test_exponential_invalid(self):
        with self.assertRaises(ValueError):
            core.distribution.ExponentialDistribution(0, -1)

    def test_asJson(self):
        dist = core.distribution.UniformDistribution(0, 1)
        expected = {"name": "Uniform", "param": (0, 1)}
        result = dist.asJson()
        self.assertEqual(expected, result)

    def test_getMaximumPDF(self):
        dist = core.distribution.NormalDistribution()
        self.assertEqual(0.3989422804014327, dist.getMaximumPDF())

    def test___eq__(self):
        dist1 = NormalDistribution()
        dist2 = NormalDistribution(2, 3)
        self.assertEqual(dist1, dist1)
        self.assertNotEqual(dist1, dist2)
        self.assertNotEqual(dist1, "a")

    def test_load(self):
        with self.assertRaises(ValueError):
            core.distribution.load("{\"name\": \"Norm\"}")
        with self.assertRaises(ValueError):
            core.distribution.load({"name": "foo", "param": [0]})

        normal = core.distribution.load({"name": "Norm", "param": [0, 1]})
        self.assertEqual(NormalDistribution(0, 1), normal)
        power = core.distribution.load({"name": "Powerlaw", "param": [1, 0]})
        self.assertEqual(PowerLawDistribution(1), power)

    def test_kstest(self):
        dist1 = NormalDistribution()
        dist2 = NormalDistribution()
        with self.assertRaises(TypeError):
            core.distribution.kstest("a", dist2)
        with self.assertRaises(TypeError):
            core.distribution.kstest(dist1, "a")
        self.assertLess(core.distribution.kstest(dist1, dist2), 1)

    def test_approximateIntervalBorders(self):
        dist = UniformDistribution()
        lower, upper = core.distribution.approximateIntervalBorders(dist, 0.1)
        self.assertEqual(-10, lower)
        self.assertAlmostEqual(0.10, upper, delta=0.01)

    def test_chi2test(self):
        dist = NormalDistribution()
        self.assertLess(core.distribution.chi2test(dist, dist), 100000)


if __name__ == '__main__':
    unittest.main()
