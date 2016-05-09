import unittest

import core.event
import generation.entry
import generation.generator
from core import event, rule
from core.distribution import StaticDistribution
from core.event import Event
from generation.entry import Entry


class TestScript(unittest.TestCase):
    def test_addPendingEvents(self):
        r = rule.Rule(core.event.Event('A'), event.Event('B'), StaticDistribution([0], [0]))
        entry = generation.entry.Entry(r, 10)

        response = event.Event("B")

        gen = generation.generator.Generator()
        gen._Generator__addPendingEvent(entry, 0, response)
        gen._Generator__addPendingEvent(entry, 10, response)
        gen._Generator__addPendingEvent(entry, 8, response)
        gen._Generator__addPendingEvent(entry, 12, response)
        gen._Generator__addPendingEvent(entry, 5, response)
        gen._Generator__addPendingEvent(entry, 13, response)

        self.assertEqual(0, gen.pendingEvents[0][0])
        self.assertEqual(5, gen.pendingEvents[1][0])
        self.assertEqual(8, gen.pendingEvents[2][0])
        self.assertEqual(10, gen.pendingEvents[3][0])
        self.assertEqual(12, gen.pendingEvents[4][0])
        self.assertEqual(13, gen.pendingEvents[5][0])

    def test_pendingEventHandling(self):
        r = rule.Rule(event.Event('A'), event.Event('B'), StaticDistribution([0], [0]))

        response1 = event.Event("B")
        response2 = event.Event("B")

        entry = generation.entry.Entry(r, 10)
        gen = generation.generator.Generator()
        gen._Generator__addPendingEvent(entry, 0, response1)
        gen._Generator__addPendingEvent(entry, 10, response2)

        self.assertEqual(generation.generator.PendingEvent(0, event.Event('B', 0), 1),
                         gen._Generator__getPendingEvent(0))
        self.assertIsNone(gen._Generator__getPendingEvent(5))
        self.assertEqual(10, gen.pendingEvents[0][0])
        self.assertEqual(generation.generator.PendingEvent(10, event.Event('B', 10), 1),
                         gen._Generator__getPendingEvent(11))
        self.assertIsNone(gen._Generator__getPendingEvent(1000))

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
            .setRndNumber(StaticDistribution([1, 0, 0, 1, 1, 0, 0, 0, 1, 1, 1, 1])) \
            .setEntries([
                Entry(rule.Rule(event.Event('A'), event.Event('B'),
                                StaticDistribution([3]), responseConfidence=0.9),
                      StaticDistribution([0, 1, 0, 0, 0, 1, 0, 0, 0, 0]))
            ]) \
            .createSequence()
        # @formatter:on

        self.assertEqual(1, len(sequences))
        seq = sequences[0]
        self.assertEqual("_A__BA__*_", str(seq))
        self.assertEqual(eventA1, seq.getEvent(1))
        self.assertEqual(eventB1, seq.getEvent(1).getTriggered())
        self.assertEqual(eventB1, seq.getEvent(4))
        self.assertEqual(eventA1, seq.getEvent(4).getTriggeredBy())
        self.assertEqual(eventA2, seq.getEvent(5))
        self.assertEqual(eventB2, seq.getEvent(5).getTriggered())
        self.assertEqual(eventB2, seq.getEvent(8))
        self.assertEqual(eventA2, seq.getEvent(8).getTriggeredBy())

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

        eventA2.setOccurred(False)
        eventB3.setOccurred(False)
        eventA1.setTriggered(eventB1)
        eventA2.setTriggered(eventB2)
        eventA3.setTriggered(eventB3)
        eventA4.setTriggered(eventB4)

        # @formatter:off
        sequences = generation.generator.Generator() \
            .setNumberOfEvents(numberEvents) \
            .setRndNumber(StaticDistribution([0, 0, 1, 0, 0, 1, 0, 0, 0])) \
            .setEntries([
                Entry(rule.Rule(event.Event('A'), event.Event('B'), StaticDistribution([3]), triggerConfidence=0.9,
                                responseConfidence=0.9),
                        StaticDistribution([2, 4]))
            ]) \
            .createSequence()
        # @formatter:on

        self.assertEqual(1, len(sequences))
        seq = sequences[0]
        self.assertEqual("_A__B*_AB_*A_AB", str(seq))
        self.assertEqual(eventA1, seq.getEvent(1))
        self.assertEqual(eventB1, seq.getEvent(1).getTriggered())
        self.assertEqual(eventB1, seq.getEvent(4))
        self.assertEqual(eventA1, seq.getEvent(4).getTriggeredBy())
        self.assertEqual(eventA2, seq.getEvent(5))
        self.assertFalse(eventA2.hasOccurred())
        self.assertEqual(eventB2, seq.getEvent(5).getTriggered())
        self.assertEqual(eventB2, seq.getEvent(8))
        self.assertEqual(eventA2, seq.getEvent(8).getTriggeredBy())
        self.assertEqual(eventA3, seq.getEvent(7))
        self.assertEqual(eventB3, seq.getEvent(7).getTriggered())
        self.assertEqual(eventB3, seq.getEvent(10))
        self.assertFalse(eventB3.hasOccurred())
        self.assertEqual(eventA3, seq.getEvent(10).getTriggeredBy())
        self.assertEqual(eventA4, seq.getEvent(11))
        self.assertEqual(eventB4, seq.getEvent(11).getTriggered())
        self.assertEqual(eventB4, seq.getEvent(14))
        self.assertEqual(eventA4, seq.getEvent(14).getTriggeredBy())
        self.assertEqual(eventA5, seq.getEvent(13))
        self.assertIsNone(eventA5.getTriggered())

    def test_invalidConfiguration(self):
        with self.assertRaises(RuntimeError):
            # @formatter:off
            generation.generator.Generator() \
                .setRndNumber(StaticDistribution([0, 0, 1, 0, 0, 1, 0, 0, 0])) \
                .setEntries([
                    Entry(rule.Rule(event.Event('A'), event.Event('B'), StaticDistribution([3]), triggerConfidence=0.9,
                                    responseConfidence=0.9),
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
            .setEntries([
                Entry(rule.Rule(event.Event('A'), event.Event('B'), StaticDistribution([3]), triggerConfidence=0.9,
                                responseConfidence=0.9),
                        StaticDistribution([2, 4]))
            ]) \
            .createSequence(5)
        # @formatter:on
        self.assertEqual(5, len(sequences))


if __name__ == '__main__':
    unittest.main()
