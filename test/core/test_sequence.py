import os
import unittest

from core import sequence
from core.event import Event

INPUT_FILE = os.path.join(os.path.dirname(__file__), 'sequences.json')


class TestScript(unittest.TestCase):
    def setUp(self):
        """ Set up before test case """
        pass

    def tearDown(self):
        """ Tear down after test case """
        pass

    def test_load(self):
        sequences = sequence.loadFromFile(INPUT_FILE)
        self.assertEqual(1, len(sequences))
        seq = sequences[0]
        events = seq.getEvents()

        eventA = Event("A", 0)
        eventB = Event("B", 2)
        eventC = Event("C", 1)

        self.assertEqual(10, seq.getLength())
        self.assertEqual(3, len(events))
        self.assertEqual(eventA, events[0])
        self.assertEqual(eventC, events[1])
        self.assertEqual(eventB, events[2])
        self.assertEqual(eventB, events[0].getTriggered())
        self.assertEqual(eventA, events[2].getTriggeredBy())
        self.assertIsNone(events[1].getTriggered())


if __name__ == '__main__':
    unittest.main()
