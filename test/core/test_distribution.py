import unittest

from core import distribution
from core.distribution import NormalDistribution, PowerLawDistribution, UniformDistribution, KdeDistribution, \
    Distribution, StaticDistribution, ExponentialDistribution


class TestScript(unittest.TestCase):
    def test_abstract(self):
        dist = Distribution(None, None)
        self.assertIsNone(dist.getRandom())
        self.assertIsNone(dist.getCDFValue(0))
        self.assertIsNone(dist.getPDFValue(0))

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
        self.assertEqual("Static: pdf: [1, 2]\t cdf: [3, 4]\t rvs: [5, 6]", str(dist))

    def test_normal(self):
        dist = NormalDistribution(0, 1)
        self.assertTrue(isinstance(dist, Distribution))
        self.assertIsNotNone(dist.getRandom())
        self.assertEqual("Norm: Mu: 0\t Sigma: 1", str(dist))
        self.assertEqual(0.3989422804014327, dist.getPDFValue(0))
        self.assertEqual(0.5, dist.getCDFValue(0))

    def test_normal_invalid(self):
        with self.assertRaises(ValueError):
            NormalDistribution(0, 0)

    def test_uniform(self):
        dist = UniformDistribution(0, 1)
        self.assertTrue(isinstance(dist, Distribution))
        self.assertIsNotNone(dist.getRandom())
        self.assertEqual("Uniform: Lower: 0\t Upper: 1", str(dist))
        self.assertEqual(1, dist.getPDFValue(1))
        self.assertEqual(0.5, dist.getCDFValue(0.5))

        dist = UniformDistribution(10, 20)
        self.assertAlmostEqual((10.05, 19.95), dist.getCompleteInterval())

    def test_uniform_invalid(self):
        with self.assertRaises(ValueError):
            UniformDistribution(0, 0)

    def test_powerlaw(self):
        dist = PowerLawDistribution(1, 0)
        self.assertTrue(isinstance(dist, Distribution))
        self.assertIsNotNone(dist.getRandom())
        self.assertEqual("Powerlaw: Exponent: 1", str(dist))
        self.assertEqual(1, dist.getPDFValue(1))
        self.assertEqual(0.5, dist.getCDFValue(0.5))

    def test_powerlaw_invalid(self):
        with self.assertRaises(ValueError):
            PowerLawDistribution(0)

    def test_exponential(self):
        dist = ExponentialDistribution(0, 4)
        self.assertEqual("Expon: Offset: 0\t Lambda: 4", str(dist))
        self.assertEqual(0.19470019576785122, dist.getPDFValue(1))
        self.assertEqual(0.1175030974154046, dist.getCDFValue(0.5))
        self.assertIsNotNone(dist.getRandom())

        dist = ExponentialDistribution(1, 4)
        self.assertEqual(0.25, dist.getPDFValue(1))

    def test_exponential_invalid(self):
        with self.assertRaises(ValueError):
            ExponentialDistribution(0, -1)

    def test_kde(self):
        dist = KdeDistribution(
            [29.0636, 23.7378, 14.4818, 18.419, 6.0431, 3.3395, 12.2812, 15.6998, 9.9592, 4.9988, 11.2077, 25.8959,
             22.7192, 19.4778, 17.7977, 4.1812, 5.1253, 3.203, 4.3251, 12.7011, 15.9507, 15.0248, 15.9752, 8.4376,
             18.9881, 12.8122, 7.4235, 9.5878, 3.3641, 3.8647, 7.9739, 9.0641, 6.827, 17.2279, 15.8699, 14.3722, 2.7732,
             2.1239, 16.7671, 27.555, 29.1603, 17.6583, 11.5634, 9.5922, 19.1209, 14.168, 18.8858, 10.7597, 13.1935,
             15.7445, 14.5384, 2.3002, 2.6062, 4.2566, 9.1554, 17.8881, 7.3633, 10.7905, 3.2125, 2.7131, 8.8323, 5.5761,
             9.3102, 9.9232, 19.4521, 18.4323, 7.806, 11.9186, 22.004, 16.3168, 13.3261, 10.6107, 6.0937, 7.3862,
             2.8321, 8.9818, 14.3169, 15.4862, 8.2905, 3.2816, 2.0763, 7.9852, 6.7399, 10.177, 13.7641, 19.9483, 19.297,
             16.5613, 11.3849, 24.4364, 20.6557, 23.4644, 23.5463, 15.1912, 18.1363, 17.1629, 4.2176, 3.5967, 24.6061])
        self.assertIsNotNone(dist.getPDFValue(15))
        self.assertIsNotNone(dist.getCDFValue(10))
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
        power = distribution.load({"name": "Powerlaw", "param": [1, 0]})
        self.assertEqual(PowerLawDistribution(1), power)
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


if __name__ == '__main__':
    unittest.main()
