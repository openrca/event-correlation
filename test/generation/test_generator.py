import unittest

import core.distribution as distri
import core.event
import generation.generator
from core import event, rule
from core.event import Event


class TestScript(unittest.TestCase):
    def test_addPendingEvents(self):
        r = rule.Rule(core.event.Event('A'), event.Event('B'), distri.StaticDistribution([0], [0]))
        entry = generation.generator.Entry(r, 10)

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
        r = rule.Rule(event.Event('A'), event.Event('B'), distri.StaticDistribution([0], [0]))

        response1 = event.Event("B")
        response2 = event.Event("B")

        entry = generation.generator.Entry(r, 10)
        gen = generation.generator.Generator()
        gen._Generator__addPendingEvent(entry, 0, response1)
        gen._Generator__addPendingEvent(entry, 10, response2)

        self.assertEqual(generation.generator.PendingEvent(0, event.Event('B', 0), 1), gen._Generator__getPendingEvent(0))
        self.assertIsNone(gen._Generator__getPendingEvent(5))
        self.assertEqual(10, gen.pendingEvents[0][0])
        self.assertEqual(generation.generator.PendingEvent(10, event.Event('B', 10), 1), gen._Generator__getPendingEvent(11))
        self.assertIsNone(gen._Generator__getPendingEvent(1000))

    def test_createSequence(self):
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
            .setRndNumber(distri.StaticDistribution([1, 0, 0, 1, 1, 0, 0, 0, 1, 1, 0, 1])) \
            .setRules([
                (rule.Rule(event.Event('A', distri.StaticDistribution()), event.Event('B'),
                           distri.StaticDistribution([3],)),
                 distri.StaticDistribution([0, 1, 0, 0, 0, 1, 0, 0, 0, 0]), 1)
            ]) \
            .createSequence()
        # @formatter:on

        self.assertEqual(1, len(sequences))
        seq = sequences[0]
        self.assertEqual("_A__BA__B_", str(seq))
        self.assertEqual(eventA1, seq.getEvent(1))
        self.assertEqual(eventB1, seq.getEvent(1).getTriggered())
        self.assertEqual(eventB1, seq.getEvent(4))
        self.assertEqual(eventA1, seq.getEvent(4).getTriggeredBy())
        self.assertEqual(eventA2, seq.getEvent(5))
        self.assertEqual(eventB2, seq.getEvent(5).getTriggered())
        self.assertEqual(eventB2, seq.getEvent(8))
        self.assertEqual(eventA2, seq.getEvent(8).getTriggeredBy())


if __name__ == '__main__':
    unittest.main()
