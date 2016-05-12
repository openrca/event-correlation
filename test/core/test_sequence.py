import os
import unittest

from core import sequence
from core.distribution import NormalDistribution
from core.event import Event
from core.rule import Rule
from core.sequence import Sequence

INPUT_FILE = os.path.join(os.path.dirname(__file__), 'sequences.json')
TMP_FILE_NAME = "/tmp/sequences.json"


class TestScript(unittest.TestCase):
    def setUp(self):
        """ Set up before test case """
        pass

    def tearDown(self):
        """ Tear down after test case """
        pass

    def test_load(self):
        seq = sequence.loadFromFile(INPUT_FILE)
        events = seq.getEvents()

        eventA = Event("A", 0)
        eventB = Event("B", 2)
        eventC = Event("C", 1)

        self.assertEqual(10, seq.length)
        self.assertEqual(3, len(events))
        self.assertEqual(eventA, events[0])
        self.assertEqual(eventC, events[1])
        self.assertEqual(eventB, events[2])
        self.assertEqual(eventB, events[0].triggered)
        self.assertEqual(eventA, events[2].triggeredBy)
        self.assertIsNone(events[1].triggered)

        with self.assertRaises(ValueError):
            sequence.load("{\"length\": 10}")

    def test_rules(self):
        seq = sequence.loadFromFile(INPUT_FILE)
        rule = Rule("A", "B", NormalDistribution())
        seq.rules = [rule]
        self.assertEqual(rule, seq.getRule(Event("A"), Event("B")))
        self.assertIsNone(seq.getRule(Event("A"), Event("C")))

    def test_getEvent(self):
        seq = sequence.loadFromFile(INPUT_FILE)
        self.assertIsNotNone(seq.getEvent(-1))
        self.assertEqual(Event("A", 0), seq.getEvent(0)[0])
        self.assertEqual(Event(timestamp=3), seq.getEvent(3)[0])

    def test_asVector(self):
        seq = sequence.loadFromFile(INPUT_FILE)
        vec = seq.asVector("A")
        self.assertEqual(1, len(vec))
        self.assertEqual(0, vec[0])

    def test_storeAndLoad(self):
        eventA = Event("A", 0)
        eventB = Event("B", 2)
        eventC = Event("C", 1)
        eventA.setTriggered(eventB)
        rule = Rule("A", "B", NormalDistribution())

        seq = Sequence([eventA, eventC, eventB], 5, [rule])

        try:
            seq.store(TMP_FILE_NAME)
            seq2 = sequence.loadFromFile(TMP_FILE_NAME)

            self.assertEqual(seq.length, seq2.length)
            self.assertEqual(len(seq.getEvents()), len(seq2.getEvents()))
            for i in range(len(seq.getEvents())):
                event1 = seq.getEvents()[i]
                event2 = seq2.getEvents()[i]

                self.assertEqual(event1, event2)
                self.assertEqual(event1.triggered, event2.triggered)
                self.assertEqual(event1.triggeredBy, event2.triggeredBy)
            self.assertEqual(len(seq.rules), len(seq2.rules))
            for i in range(len(seq.rules)):
                self.assertEqual(seq.rules[i], seq2.rules[i])

        except (OSError, IOError) as ex:
            print("Unable to open tmp file. Maybe you have to change TMP_FILE_NAME: {}".format(ex))
        os.remove(TMP_FILE_NAME)

if __name__ == '__main__':
    unittest.main()
