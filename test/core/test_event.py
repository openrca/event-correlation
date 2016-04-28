import json
import unittest

import core.event


class TestScript(unittest.TestCase):
    def setUp(self):
        self.event = core.event.Event("a", 10)

    def test_constructor(self):
        self.assertEqual("a", self.event.eventType)
        self.assertEqual(10, self.event.timestamp)

    def test_constructor2(self):
        event = core.event.Event("a")

        self.assertEqual("a", event.eventType, "a")
        self.assertIsNotNone(event.timestamp)
        self.assertEqual(-1, event.timestamp)

    def test_getter(self):
        self.assertEqual("a", self.event.getEventType())
        self.assertEqual(10, self.event.getTimestamp())

    def test_hash(self):
        self.assertEqual(hash("a") + hash(10), hash(self.event))

    def test_equals(self):
        event2 = core.event.Event("a", 10)
        self.assertEqual(event2, self.event)

        event3 = core.event.Event("foo")
        self.assertNotEqual(event3, self.event)

        event4 = core.event.Event(5)
        self.assertNotEqual(event4, self.event)

        self.assertNotEqual("a", self.event)

    def test_asJson(self):
        event = core.event.Event("a", 0)
        event2 = core.event.Event("b", 0)
        event2.setOccurred(False)
        event.setTriggered(event2)

        d = {
            "eventType": "a",
            "timestamp": "0",
            "occurred": "True",
            "triggered": {
                "eventType": "b",
                "timestamp": "0",
                "occurred": "False"
            }
        }

        self.assertEqual(d, json.loads(json.dumps(event.asJson())))


if __name__ == '__main__':
    unittest.main()
