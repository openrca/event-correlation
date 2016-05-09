import copy
import json

import numpy as np

from core import event
from core.event import Event


class Sequence:
    def __init__(self, events, length, rules=None):
        self.events = events
        self.length = length
        self.rules = rules

    def getLength(self):
        return self.length

    def getEvents(self, eventType=None):
        res = []
        for e in self.events:
            if (eventType is None or e.getEventType() == eventType):
                res.append(e)
        return res

    def getEvent(self, index):
        for e in self.events:
            if (index < e.getTimestamp()):
                break
            if (e.getTimestamp() == index):
                return e
        return Event(timestamp=index)

    def setRules(self, rules):
        self.rules = rules

    def getRule(self, trigger, response):
        for rule in self.rules:
            if (rule.getTrigger() == trigger.getEventType() and rule.getResponse() == response.getEventType()):
                return rule
        return None

    def asVector(self, eventType):
        l = [e for e in self.getEvents(eventType) if e.hasOccurred()]
        v = np.zeros(len(l))
        i = 0
        for e in l:
            v[i] = e.getTimestamp()
            i += 1
        return v

    def __str__(self):
        tokens = []

        seq = copy.copy(self.getEvents())
        for i in range(0, self.getLength()):
            if (len(seq) > 0 and seq[0].timestamp == i):
                e = seq.pop(0)
                tokens.append(e.getExternalRepresentation())
            else:
                tokens.append("_")
        return "".join(tokens)

    def asJson(self):
        events = []
        for e in self.getEvents():
            events.append(e.asJson())
        return {
            "length": self.getLength(),
            "events": events
        }

    def store(self, filename):
        with open(filename, "w+") as file:
            file.write(json.dumps(self.asJson()))


def load(value):
    events = []
    if (isinstance(value, str)):
        value = json.loads(value)

    try:
        length = int(value["length"])

        for item in value["events"]:
            e = event.load(item)

            events.append(e)
            while (e.getTriggered() is not None):
                e = e.getTriggered()
                events.append(e)

        events.sort(key=lambda x: x.timestamp)
        seq = Sequence(events, length)
        print("Loaded sequence: " + str(seq))
        return seq
    except KeyError:
        raise ValueError("Missing parameter 'length' and/or 'events'")


def loadFromFile(filename):
    with open(filename, "r") as file:
        content = json.loads("".join(file.readlines()))

        entry = load(content)
        return entry
