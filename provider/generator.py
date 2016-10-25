""" Automatically generated documentation for Generator """
import copy
import json
import math
import os

import core.distribution
import core.rule
from core import rule
from core.event import Event
from core.sequence import Sequence
from provider import SequenceParser


class Generator(SequenceParser):
    def __init__(self):
        super().__init__()
        self.length = -1
        self.numberEvents = -1
        self.rules = []
        self.lastTime = {}
        self.rndNumber = core.distribution.UniformDistribution()
        self.discrete = False
        self._createFunction = None

    def setRndNumber(self, dist):
        self.rndNumber = dist
        return self

    def setSeqLength(self, length):
        """ Set the total length of the sequence
        The number of occurrences is calculated dynamically such that
        """
        self.length = length
        return self

    def setNumberOfEvents(self, count):
        """ Set the number of events

        The sequence length is calculated dynamically such that enough events occurred
        """
        self.numberEvents = count
        return self

    def setRules(self, rules):
        """ Add rules to this generator """
        self.rules = []
        self.lastTime = {}
        for rule in rules:
            self.rules.append(rule)
            self.lastTime[rule] = 0
        return self

    def setDiscrete(self):
        """ Call this function to create discrete sequences """
        self.discrete = True
        return self

    def _create(self, file, normalization):
        rulesFile = None
        if (file is not None and isinstance(file, str)):
            # noinspection PyUnresolvedReferences
            config = os.path.toAbsolutePath(file)
            with open(config) as f:
                config = json.load(f)

            rulesFile = config["rules"] if "rules" in config else None
            self.numberEvents = int(config["count"]) if "count" in config else -1
            self.length = int(config["length"]) if "length" in config else -1

        if (self.length == -1 and self.numberEvents == -1):
            raise ValueError("Neither sequence length nor event count specified. Please provide at exactly one")
        if (self.length != -1 and self.numberEvents != -1):
            raise ValueError("Sequence length and event count specified. Please provide exactly one")
        if (len(self.rules) == 0 and rulesFile is not None):
            rules = rule.loadFromFile(rulesFile)
            self.setRules(rules)
        if (self.rules is None or len(self.rules) == 0):
            raise RuntimeError("Configuration not valid. Please provide rules")

        if (self.length != -1):
            self._createFunction = self._createByLength
        else:
            self._createFunction = self._createByNumberEvents

        return self._createFunction()

    def _createByNumberEvents(self):
        timeline = {}
        while len(timeline) < self.numberEvents:
            for rule in self.rules:
                if (len(timeline) >= self.numberEvents):
                    break

                timeTrigger = self._getTimeStamp(rule.distributionTrigger, self.lastTime[rule], timeline)
                self.lastTime[rule] = timeTrigger
                trigger = Event(rule.trigger)
                self._addEvent(timeline, timeTrigger, trigger, rule.successTrigger)

                if (len(timeline) >= self.numberEvents):
                    break

                if (rule.response is not None):
                    timeResponse = self._getTimeStamp(rule.distributionResponse, self.lastTime[rule], timeline)
                    response = Event(rule.response)
                    trigger.setTriggered(response)
                    self._addEvent(timeline, timeResponse, response, rule.successResponse)
        for rule in self.rules:
            self.lastTime[rule] = 0
        return self._asSequence(timeline)

    def _createByLength(self):
        timeline = {}

        rules = copy.copy(self.rules)
        while (len(rules) > 0):
            for rule in rules:
                timeTrigger = self._getTimeStamp(rule.distributionTrigger, self.lastTime[rule], timeline)
                if (timeTrigger >= self.length):
                    rules.remove(rule)
                    continue

                self.lastTime[rule] = timeTrigger
                trigger = Event(rule.trigger)
                self._addEvent(timeline, timeTrigger, trigger, rule.successTrigger)

                if (rule.response is not None):
                    timeResponse = self._getTimeStamp(rule.distributionResponse, self.lastTime[rule], timeline)
                    if (timeResponse >= self.length):
                        continue

                    response = Event(rule.response)
                    trigger.setTriggered(response)
                    self._addEvent(timeline, timeResponse, response, rule.successResponse)
        for rule in self.rules:
            self.lastTime[rule] = 0
        return self._asSequence(timeline, self.length)

    def _getTimeStamp(self, dist, lastTime, timeline):
        time = dist.getRandom() + lastTime
        stepSize = 0.01
        if (self.discrete):
            time = round(time)
            stepSize = 1
        while (time in timeline):
            time += stepSize
        return time

    def _addEvent(self, timeline, timestamp, event, success):
        if (self.rndNumber.getRandom() > success):
            event.occurred = False
        event.timestamp = timestamp
        timeline[timestamp] = event

    def _asSequence(self, dictionary, length=-1):
        seq = list(dictionary.values())
        seq.sort()
        return Sequence(seq, length if length != -1 else math.ceil(seq[-1].timestamp) + 1, self.rules)
