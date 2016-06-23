import os
import unittest

import core
from core.distribution import NormalDistribution, StaticDistribution
from core.rule import Rule

INPUT_FILE = os.path.join(os.path.dirname(__file__), 'rules.json')


class TestScript(unittest.TestCase):
    def test_loadFromFile(self):
        rules = core.rule.loadFromFile(INPUT_FILE)

        self.assertEqual(2, len(rules))
        self.assertEqual('A', rules[0].trigger)
        self.assertEqual('B', rules[0].response)
        self.assertEqual(0, rules[0].distribution.lower)
        self.assertEqual(1, rules[0].distribution.upper)
        self.assertEqual(1, rules[0].responseConfidence)

        self.assertEqual('A', rules[1].trigger)
        self.assertEqual('0', rules[1].response)
        self.assertEqual(0.5, rules[1].distribution.beta)
        self.assertEqual(0.9, rules[1].responseConfidence)

    def test_load(self):
        rule = core.rule.load("""{
            "trigger": "A",
            "response": "B",
            "dist": {
                "name": "Uniform",
                "param": [0, 1]
            },
            "triggerConfidence": "1",
            "responseConfidence": "1"
        }""")

        self.assertEqual('A', rule.trigger)
        self.assertEqual('B', rule.response)
        self.assertEqual(0, rule.distribution.lower)
        self.assertEqual(1, rule.distribution.upper)
        self.assertEqual(1, rule.responseConfidence)

    def test_asJson(self):
        rule = Rule("a", "b", NormalDistribution(0, 1))
        expected = {"trigger": "a", "response": "b", "triggerConfidence": 1.0, "responseConfidence": 1.0,
                    'likelihood': -1, "dist":
                        NormalDistribution(0, 1).asJson()}
        self.assertEqual(expected, rule.asJson())

    def test___eq__(self):
        rule1 = Rule("a", "b", NormalDistribution(0, 1))
        rule2 = Rule("b", "a", NormalDistribution(0, 1))
        self.assertEqual(True, rule1 == rule1)
        self.assertEqual(False, rule1 == rule2)
        self.assertEqual(False, rule1 == 'A')

    def test___hash__(self):
        rule1 = Rule("a", "b", NormalDistribution(0, 1))
        self.assertTrue(isinstance(hash(rule1), int))

    def test_getResponseTimestamp(self):
        rule = Rule("a", "b", StaticDistribution([1], rvs=[1]))
        self.assertEqual(1, rule.getResponseTimestamp())


if __name__ == '__main__':
    unittest.main()
