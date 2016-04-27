import unittest

import core.distribution


class TestScript(unittest.TestCase):
    def setUp(self):
        """ Set up before test case """
        pass

    def tearDown(self):
        """ Tear down after test case """
        pass

    def test_abstract(self):
        dist = core.distribution.Distribution()
        self.assertEqual(dist.getPDFValue(), None)

    def test_static(self):
        dist = core.distribution.StaticDistribution()
        self.assertEqual(0.5, dist.getPDFValue())
        self.assertEqual(0.5, dist.getPDFValue())
        self.assertEqual(0.5, dist.getCDFValue(0))
        self.assertEqual(0.5, dist.getCDFValue(0))

        dist = core.distribution.StaticDistribution([1, 2], [3, 4])
        self.assertEqual(1, dist.getPDFValue())
        self.assertEqual(2, dist.getPDFValue())
        self.assertEqual(1, dist.getPDFValue())
        self.assertEqual(3, dist.getCDFValue(0))
        self.assertEqual(4, dist.getCDFValue(0))
        self.assertEqual(3, dist.getCDFValue(0))

    def test_normal(self):
        dist = core.distribution.NormalDistribution(0, 1)
        self.assertTrue(isinstance(dist, core.distribution.Distribution))
        self.assertIsNotNone(dist.getPDFValue())

    def test_normal_invalid(self):
        with self.assertRaises(ValueError):
            core.distribution.NormalDistribution(0, 0)

    def test_uniform(self):
        dist = core.distribution.UniformDistribution(0, 1)
        self.assertTrue(isinstance(dist, core.distribution.Distribution))
        self.assertIsNotNone(dist.getPDFValue())

    def test_uniform_invalid(self):
        with self.assertRaises(ValueError):
            core.distribution.UniformDistribution(0, 0)

    def test_powerlaw(self):
        dist = core.distribution.PowerLawDistribution(1)
        self.assertTrue(isinstance(dist, core.distribution.Distribution))
        self.assertIsNotNone(dist.getPDFValue())

    def test_powerlaw_invalid(self):
        with self.assertRaises(ValueError):
            core.distribution.PowerLawDistribution(0)

    def test_exponential(self):
        dist = core.distribution.ExponentialDistribution(1 / 4)
        self.assertAlmostEqual(0.63212055, dist.getCDFValue(4))


if __name__ == '__main__':
    unittest.main()
