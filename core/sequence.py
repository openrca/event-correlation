import copy
import json
import logging
import math
import os

import numpy as np

from core import event, rule
from core.event import Event


class Sequence:
    def __init__(self, events, length=None, rules=None, calculatedRules=None):
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
        for e in self.events:
            self.eventTypes.add(e.eventType)

    def getEvents(self, eventType=None):
        """ Returns all events with the given event type. If no eventType is provided all events are returned. """
        if (eventType is None):
            return self.events
        return [e for e in self.events if e.eventType == eventType]

    def getEvent(self, timestamp):
        """ Returns the all events that happened at the given timestamp (same integer part). If no events happened, a
        default event is returned. """
        result = []
        for e in self.events:
            if (timestamp < math.floor(e.timestamp)):
                break
            if (math.floor(e.timestamp) == timestamp):
                result.append(e)
        if (len(result) == 0):
            result.append(Event(timestamp=timestamp))
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

        seq = copy.copy(self.getEvents())
        for i in range(self.length):
            if (len(seq) > 0 and seq[0].timestamp <= i):
                while (len(seq) > 0 and seq[0].timestamp <= i):
                    e = seq.pop(0)
                    tokens.append(e.getExternalRepresentation())
            else:
                tokens.append("_")
        return "".join(tokens)

    def asJson(self):
        return {
            "length": self.length,
            "events": self.events,
            "rules": self.rules,
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
