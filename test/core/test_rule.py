import os
import unittest

import core
from core.event import Event

INPUT_FILE = os.path.join(os.path.dirname(__file__), 'rules.json')


class TestScript(unittest.TestCase):
    def test_load(self):
        rules = core.rule.loadFromFile(INPUT_FILE)

        self.assertEqual(2, len(rules))
        self.assertEqual(Event('A'), rules[0].getTrigger())
        self.assertEqual(Event('B'), rules[0].getResponse())
        self.assertEqual(0, rules[0].distribution.lower)
        self.assertEqual(1, rules[0].distribution.upper)
        self.assertEqual(1, rules[0].getConfidence())

        self.assertEqual(Event('A'), rules[1].getTrigger())
        self.assertEqual(Event('0'), rules[1].getResponse())
        self.assertEqual(0.5, rules[1].distribution.lam)
        self.assertEqual(0.9, rules[1].getConfidence())


if __name__ == '__main__':
    unittest.main()
