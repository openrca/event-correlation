import unittest

import core.distribution


class TestScript(unittest.TestCase):
    def test_abstract(self):
        dist = core.distribution.Distribution(None, None)
        self.assertEqual(dist.getRandom(), None)

    def test_static(self):
        dist = core.distribution.StaticDistribution()
        self.assertEqual(0.5, dist.getRandom())
        self.assertEqual(0.5, dist.getRandom())
        self.assertEqual(0.5, dist.getCDFValue(0))
        self.assertEqual(0.5, dist.getCDFValue(0))

        dist = core.distribution.StaticDistribution([1, 2], [3, 4])
        self.assertEqual(1, dist.getRandom())
        self.assertEqual(2, dist.getRandom())
        self.assertEqual(1, dist.getRandom())
        self.assertEqual(3, dist.getCDFValue(0))
        self.assertEqual(4, dist.getCDFValue(0))
        self.assertEqual(3, dist.getCDFValue(0))
        self.assertEqual("Static: pdf: [1, 2]\t cdf: [3, 4]", str(dist))

    def test_normal(self):
        dist = core.distribution.NormalDistribution(0, 1)
        self.assertTrue(isinstance(dist, core.distribution.Distribution))
        self.assertIsNotNone(dist.getRandom())
        self.assertEqual("Normal: Mu: 0\t Sigma: 1", str(dist))

    def test_normal_invalid(self):
        with self.assertRaises(ValueError):
            core.distribution.NormalDistribution(0, 0)

    def test_uniform(self):
        dist = core.distribution.UniformDistribution(0, 1)
        self.assertTrue(isinstance(dist, core.distribution.Distribution))
        self.assertIsNotNone(dist.getRandom())
        self.assertEqual("Uniform: Lower: 0\t Upper: 1", str(dist))

    def test_uniform_invalid(self):
        with self.assertRaises(ValueError):
            core.distribution.UniformDistribution(0, 0)

    def test_powerlaw(self):
        dist = core.distribution.PowerLawDistribution(1)
        self.assertTrue(isinstance(dist, core.distribution.Distribution))
        self.assertIsNotNone(dist.getRandom())
        self.assertEqual("Power: Exponent: 1", str(dist))

    def test_powerlaw_invalid(self):
        with self.assertRaises(ValueError):
            core.distribution.PowerLawDistribution(0)

    def test_exponential(self):
        dist = core.distribution.ExponentialDistribution(0.25)
        self.assertEqual("Exp: Lambda: 0.25", str(dist))


if __name__ == '__main__':
    unittest.main()
