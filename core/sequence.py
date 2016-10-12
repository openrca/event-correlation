import copy
import json
import logging
import math
import os

import numpy as np

from core import event, rule
from core.event import Event


class Sequence:
    def __init__(self, events, length=0, rules=None, calculatedRules=None):
        if (rules is None):
            rules = []
        if (calculatedRules is None):
            calculatedRules = []
        events.sort(key=lambda e: e.timestamp)

        self.events = events
        self.length = length
        self.rules = rules
        self.calculatedRules = calculatedRules

        self.eventTypes = set()
        self.firstTimestamp = max(self.events[0].timestamp - 1, 0) if (len(self.events) > 0) else 0
        for e in self.events:
            e.timestamp -= self.firstTimestamp
            self.eventTypes.add(e.eventType)

        if (length == 0 and len(self.events) > 0):
            self.length = int(self.events[-1].timestamp) + 1

    def getEvents(self, eventType=None):
        """ Returns all events with the given event type. If no eventType is provided all events are returned. """
        if (eventType is None):
            return self.events
        return [e for e in self.events if e.eventType == eventType]

    # noinspection PyMethodMayBeStatic
    def getPaddedEvent(self, event, prevTime):
        """ Returns the given event with an additional padding. The padding fills the time between the event and
        prevTime. """
        result = []
        if (event.timestamp - prevTime > 10):
            result.append(Event(eventType="...", timestamp=event.timestamp))
        else:
            for j in range(math.ceil(prevTime), int(event.timestamp) - 1):
                result.append(Event(timestamp=event.timestamp))
        result.append(event)

        return result

    def getCalculatedRule(self, trigger, response):
        """ Returns the calculated rule with the given trigger and response. """
        return self._getRule(trigger, response, self.calculatedRules)

    def getRule(self, trigger, response):
        """ Returns the rule used to create the sequence with the given trigger and response. Works only for synthetic
        sequences.
        """
        return self._getRule(trigger, response, self.rules)

    def getBaseDistribution(self, calculatedRule):
        """ For a given calculatedRule the corresponding real distribution is searched.
        Works only for synthetic sequences. """

        rule = self._getRule(calculatedRule.trigger, calculatedRule.response, self.rules)
        if (rule is not None):
            return rule.distributionResponse

        # search for opposite rule
        rule = self._getRule(calculatedRule.response, calculatedRule.trigger, self.rules)
        if (rule is not None):
            return -rule.distributionResponse
        return None

    @staticmethod
    def _getRule(trigger, response, rules):
        for r in rules:
            if (r.matches(trigger, response)):
                return r
        return None

    def asVector(self, eventType):
        """ Returns all timestamps of the events with the given eventType"""
        l = [e.timestamp for e in self.getEvents(eventType) if e.occurred]
        return np.array(l)

    def getMissingIdx(self, eventType):
        """ Returns the indices of events that did not occure. Works only for synthetic sequences. """
        l = np.array([e.occurred for e in self.getEvents(eventType)])
        return np.where(np.arange(len(l)) * np.invert(l))[0]

    def __len__(self):
        return len(self.events)

    def __str__(self):
        tokens = []

        # truncate to 500 events due to performance
        seq = copy.copy(self.getEvents()[:500])
        prevTime = -1
        for i in range(len(seq)):
            for e in self.getPaddedEvent(seq[i], prevTime):
                tokens.append(e.getExternalRepresentation())
            prevTime = seq[i].timestamp
        return "".join(tokens)

    def asJson(self):
        return {
            "length": self.length,
            "events": self.events,
            "rules": self.rules,
            "firstTimestamp": self.firstTimestamp,
            "calculatedRules": self.calculatedRules
        }

    def store(self, filename):
        import core
        with open(filename, "w+") as file:
            file.write(json.dumps(self.asJson(), default=core.defaultJsonEncoding))


def load(value):
    if (isinstance(value, str)):
        value = json.loads(value)

    try:
        length = int(value["length"])

        events = []
        for item in value["events"]:
            e = event.load(item)
            if (e not in events):
                events.append(e)
            while (e.triggered is not None):
                e = e.triggered
                if (e not in events):
                    events.append(e)
        events.sort(key=lambda x: x.timestamp)

        rules = []
        if ("rules" in value):
            for item in value["rules"]:
                r = rule.load(item)
                rules.append(r)

        calculatedRules = []
        if ("rules" in value):
            for item in value["calculatedRules"]:
                r = rule.load(item)
                calculatedRules.append(r)

        seq = Sequence(events, length, rules)
        seq.firstTimestamp = int(value["firstTimestamp"])
        seq.calculatedRules = calculatedRules
        logging.debug("Loaded sequence: " + str(seq))
        return seq
    except KeyError:
        raise ValueError("Missing parameter 'length' and/or 'events'")


def loadFromFile(filename):
    # noinspection PyUnresolvedReferences
    filename = os.path.toAbsolutePath(filename)
    with open(filename, "r") as file:
        content = json.loads("".join(file.readlines()))
        return load(content)
