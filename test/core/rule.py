import os
import unittest

import core
from core.distribution import NormalDistribution, StaticDistribution, UniformDistribution
from core.rule import Rule

INPUT_FILE = os.path.join(os.path.dirname(__file__), 'rules.json')


class TestScript(unittest.TestCase):
    def test_loadFromFile(self):
        rules = core.rule.loadFromFile(INPUT_FILE)

        self.assertEqual(2, len(rules))
        self.assertEqual('A', rules[0].trigger)
        self.assertEqual('B', rules[0].response)
        self.assertEqual(0, rules[0].distributionResponse.lower)
        self.assertEqual(1, rules[0].distributionResponse.upper)
        self.assertEqual(1, rules[0].successResponse)

        self.assertEqual('A', rules[1].trigger)
        self.assertEqual('0', rules[1].response)
        self.assertEqual(0.5, rules[1].distributionResponse.beta)
        self.assertEqual(0.9, rules[1].successResponse)

    def test_load(self):
        rule = core.rule.load("""{
            "trigger": {
                "event": "A",
                "dist": "",
                "success": "1"
            },
            "response": {
                "event": "B",
                "dist": {
                    "name": "Uniform",
                    "param": [0, 1]
                },
                "success": "1"
            }
        }""")

        self.assertEqual('A', rule.trigger)
        self.assertEqual('B', rule.response)
        self.assertEqual(0, rule.distributionResponse.lower)
        self.assertEqual(1, rule.distributionResponse.upper)
        self.assertEqual(1, rule.successResponse)

    def test_load2(self):
        rule = core.rule.load("""
            {
                "trigger": {
                    "event": "A",
                    "dist": {
                        "name": "Norm",
                        "param": [0, 1]
                    },
                    "success": 1
                },
                "response": {
                    "event": "B",
                    "dist": {
                        "name": "Uniform",
                        "param": [0, 1]
                    },
                    "success": 1
                }
            }
        """)
        self.assertEqual(Rule("A", "B", UniformDistribution(0, 1), NormalDistribution(0, 1), 1, 1), rule)

    def test_asJson(self):
        rule = Rule("a", "b", NormalDistribution(0, 1))
        expected = {"trigger": {
            "event": "a",
            "success": 1.0,
            "dist": ""
            },
            "response": {
                "event": "b",
                "success": 1.0,
                "dist":
                    NormalDistribution(0, 1)
            },
            "likelihood": -1,
            "data": {}
        }
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
