import copy
import json
import logging

from core import event
from core.event import Event


class Sequence:
    def __init__(self, events, length):
        self.events = events
        self.length = length

    def getLength(self):
        return self.length

    def getEvents(self):
        return self.events

    def getEvent(self, index):
        for e in self.events:
            if (index < e.getTimestamp()):
                break
            if (e.getTimestamp() == index):
                return e
        return Event("-", index)

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


def load(value):
    events = []
    try:
        length = int(value["length"])

        for item in value["events"]:
            e = event.load(item)

            events.append(e)
            while (e.getTriggered() is not None):
                e = e.getTriggered()
                events.append(e)

        events.sort(key=lambda x: x.timestamp)
        return Sequence(events, length)
    except KeyError:
        raise ValueError("Missing parameter 'length' and/or 'events'")


def loadFromFile(filename):
    sequences = []
    with open(filename, "r") as file:
        content = json.loads("".join(file.readlines()))

    for line in content:
        logging.debug("Processing line '{}'".format(line))
        try:
            entry = load(line)
            sequences.append(entry)
        except ValueError as ex:
            logging.warning(ex)

    return sequences


def store(sequence):
    return json.dumps(sequence)
