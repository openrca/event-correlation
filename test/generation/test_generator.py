import unittest

import generation.entry
import generation.generator
from core.distribution import StaticDistribution
from core.event import Event
from core.rule import Rule
from generation.entry import Entry


class TestScript(unittest.TestCase):
    def test_getTimestamp(self):
        timeline = {}
        gen = generation.generator.Generator()
        dist = StaticDistribution([5], rvs=[5])
        self.assertEqual(5, gen._getTimeStamp(dist, 0, timeline))
        timeline[5] = None
        self.assertEqual(5.01, gen._getTimeStamp(dist, 0, timeline))
        timeline[5.01] = None

        gen.setDiscrete()
        self.assertEqual(6, gen._getTimeStamp(dist, 0, timeline))
        timeline[6] = None
        self.assertEqual(7, gen._getTimeStamp(dist, 0, timeline))
        timeline[7] = None

    def test_createSequenceByLength(self):
        length = 10

        eventA1 = Event("A", 1)
        eventA2 = Event("A", 5)
        eventB1 = Event("B", 4)
        eventB2 = Event("B", 8)
        eventA1.setTriggered(eventB1)
        eventA2.setTriggered(eventB2)

        # @formatter:off
        sequences = generation.generator.Generator() \
            .setSeqLength(length) \
            .setRndNumber(StaticDistribution(rvs=[1, 0, 0, 1, 1, 0, 0, 0, 1, 1, 1, 1])) \
            .setEntries([Entry(
                Rule(Event('A'), Event('B'), StaticDistribution(rvs=[3]), responseConfidence=0.9),
                StaticDistribution(rvs=[2, 4, 5]))
            ]) \
            .createSequence()
        # @formatter:on

        self.assertEqual(1, len(sequences))
        seq = sequences[0]
        self.assertEqual("_A__BA__*_", str(seq))
        self.assertEqual(eventA1, seq.getEvent(1)[0])
        self.assertEqual(eventB1, seq.getEvent(1)[0].triggered)
        self.assertEqual(eventB1, seq.getEvent(4)[0])
        self.assertEqual(eventA1, seq.getEvent(4)[0].triggeredBy)
        self.assertEqual(eventA2, seq.getEvent(5)[0])
        self.assertEqual(eventB2, seq.getEvent(5)[0].triggered)
        self.assertEqual(eventB2, seq.getEvent(8)[0])
        self.assertEqual(eventA2, seq.getEvent(8)[0].triggeredBy)

    def test_createSequenceByNumberOfEvents(self):
        numberEvents = 9
        eventA1 = Event("A", 1)
        eventA2 = Event("A", 5)
        eventA3 = Event("A", 7)
        eventA4 = Event("A", 11)
        eventA5 = Event("A", 13)
        eventB1 = Event("B", 4)
        eventB2 = Event("B", 8)
        eventB3 = Event("B", 10)
        eventB4 = Event("B", 14)

        eventA2.occurred = False
        eventB3.occurred = False
        eventA1.setTriggered(eventB1)
        eventA2.setTriggered(eventB2)
        eventA3.setTriggered(eventB3)
        eventA4.setTriggered(eventB4)

        # @formatter:off
        sequences = generation.generator.Generator() \
            .setNumberOfEvents(numberEvents) \
            .setRndNumber(StaticDistribution(rvs=[0, 0, 1, 0, 0, 1, 0, 0, 0])) \
            .setEntries([Entry(
                Rule(Event('A'), Event('B'), StaticDistribution(rvs=[3]), triggerConfidence=0.9, responseConfidence=0.9),
                StaticDistribution(rvs=[2, 4]))
            ]) \
            .createSequence()
        # @formatter:on

        self.assertEqual(1, len(sequences))
        seq = sequences[0]
        self.assertEqual("_A__B*_AB_*A_AB", str(seq))
        self.assertEqual(eventA1, seq.getEvent(1)[0])
        self.assertEqual(eventB1, seq.getEvent(1)[0].triggered)
        self.assertEqual(eventB1, seq.getEvent(4)[0])
        self.assertEqual(eventA1, seq.getEvent(4)[0].triggeredBy)
        self.assertEqual(eventA2, seq.getEvent(5)[0])
        self.assertFalse(eventA2.occurred)
        self.assertEqual(eventB2, seq.getEvent(5)[0].triggered)
        self.assertEqual(eventB2, seq.getEvent(8)[0])
        self.assertEqual(eventA2, seq.getEvent(8)[0].triggeredBy)
        self.assertEqual(eventA3, seq.getEvent(7)[0])
        self.assertEqual(eventB3, seq.getEvent(7)[0].triggered)
        self.assertEqual(eventB3, seq.getEvent(10)[0])
        self.assertFalse(eventB3.occurred)
        self.assertEqual(eventA3, seq.getEvent(10)[0].triggeredBy)
        self.assertEqual(eventA4, seq.getEvent(11)[0])
        self.assertEqual(eventB4, seq.getEvent(11)[0].triggered)
        self.assertEqual(eventB4, seq.getEvent(14)[0])
        self.assertEqual(eventA4, seq.getEvent(14)[0].triggeredBy)
        self.assertEqual(eventA5, seq.getEvent(13)[0])
        self.assertIsNone(eventA5.triggered)

    def test_invalidConfiguration(self):
        with self.assertRaises(RuntimeError):
            # @formatter:off
            generation.generator.Generator() \
                .setRndNumber(StaticDistribution([0, 0, 1, 0, 0, 1, 0, 0, 0])) \
                .setEntries([Entry(
                    Rule(Event('A'), Event('B'), StaticDistribution(), triggerConfidence=0.9, responseConfidence=0.9),
                    StaticDistribution([2, 4]))
                ]) \
                .createSequence()
            # @formatter:on

        with self.assertRaises(RuntimeError):
            # @formatter:off
            generation.generator.Generator() \
                .setRndNumber(StaticDistribution([0, 0, 1, 0, 0, 1, 0, 0, 0])) \
                .setSeqLength(100) \
                .createSequence()
            # @formatter:on

    def test_createMultipleSequences(self):
        # @formatter:off
        sequences = generation.generator.Generator() \
            .setNumberOfEvents(9) \
            .setRndNumber(StaticDistribution([0, 0, 1, 0, 0, 1, 0, 0, 0])) \
            .setEntries([Entry(
                Rule(Event('A'), Event('B'), StaticDistribution([3]), triggerConfidence=0.9, responseConfidence=0.9),
                StaticDistribution([2, 4]))
            ]) \
            .createSequence(5)
        # @formatter:on
        self.assertEqual(5, len(sequences))


if __name__ == '__main__':
    unittest.main()
