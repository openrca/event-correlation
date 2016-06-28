import os
import unittest

import generation
from core.distribution import NormalDistribution, ExponentialDistribution, UniformDistribution
from core.rule import Rule
from generation.entry import Entry

INPUT_FILE = os.path.join(os.path.dirname(__file__), 'entries.json')


class TestScript(unittest.TestCase):
    def test_constructor(self):
        entry = Entry(Rule("A", "B", NormalDistribution()))
        self.assertEqual(Rule("A", "B", NormalDistribution()), entry.rule)
        self.assertEqual(ExponentialDistribution(), entry.dist)
        self.assertEqual(1, entry.scale)
        self.assertEqual(0, entry.lastTime)

    def test_getOccurrenceProb(self):
        entry = Entry(Rule("A", "B", NormalDistribution()), UniformDistribution(0, 10))
        entry.lastTime = 0
        self.assertEqual(0.5, entry.getOccurrenceProb(5))

    def test___eq__(self):
        entry1 = Entry(Rule("A", "B", UniformDistribution(0, 10)))
        entry2 = Entry(Rule("A", "C", UniformDistribution(0, 10)))
        self.assertEqual(entry1, entry1)
        self.assertNotEqual(entry1, entry2)
        self.assertNotEqual(entry1, "A")

    def test___hash__(self):
        entry = Entry(Rule("A", "B", UniformDistribution(0, 10)))
        self.assertTrue(isinstance(hash(entry), int))

    def test_load(self):
        entry = generation.entry.loadEntry("""
            {"rule": {
                "trigger": "A",
                "response": "B",
                "dist": {
                    "name": "Uniform",
                    "param": [0, 1]
                },
                "successTrigger": 1,
                "successResponse": 1
           },
            "dist": {
                "name": "Norm",
                "param": [0, 1]
            },
            "scale": 0.5}
        """)
        self.assertEqual(Rule("A", "B", UniformDistribution()), entry.rule)
        self.assertEqual(NormalDistribution(), entry.dist)
        self.assertEqual(0.5, entry.scale)

        with self.assertRaises(ValueError):
            generation.entry.loadEntry({"name": "Test"})

    def test_loadFromFile(self):
        entries = generation.entry.loadEntries(INPUT_FILE)
        self.assertEqual(2, len(entries))
        self.assertEqual(Rule("A", "B", UniformDistribution()), entries[0].rule)
        self.assertEqual(NormalDistribution(), entries[0].dist)
        self.assertEqual(0.5, entries[0].scale)

        self.assertEqual(Rule("C", "D", NormalDistribution(), 0.9, 0.5), entries[1].rule)
        self.assertEqual(ExponentialDistribution(), entries[1].dist)
        self.assertEqual(1, entries[1].scale)


if __name__ == '__main__':
    unittest.main()
