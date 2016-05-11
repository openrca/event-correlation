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
        self.assertEqual('A', rules[0].getTrigger())
        self.assertEqual('B', rules[0].getResponse())
        self.assertEqual(0, rules[0].getDistribution().lower)
        self.assertEqual(1, rules[0].getDistribution().upper)
        self.assertEqual(1, rules[0].getResponseConfidence())

        self.assertEqual('A', rules[1].getTrigger())
        self.assertEqual('0', rules[1].getResponse())
        self.assertEqual(0.5, rules[1].distribution.lam)
        self.assertEqual(0.9, rules[1].getResponseConfidence())

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

        self.assertEqual('A', rule.getTrigger())
        self.assertEqual('B', rule.getResponse())
        self.assertEqual(0, rule.getDistribution().lower)
        self.assertEqual(1, rule.getDistribution().upper)
        self.assertEqual(1, rule.getResponseConfidence())

    def test_asJson(self):
        rule = Rule("a", "b", NormalDistribution(0, 1))
        expected = {"trigger": "a", "response": "b", "triggerConfidence": 1.0, "responseConfidence": 1.0, "dist":
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
