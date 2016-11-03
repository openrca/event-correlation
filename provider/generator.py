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
        self.__length = -1
        self.__numberEvents = -1
        self.__rules = []
        self.__lastTime = {}
        self.__rndNumber = core.distribution.UniformDistribution()
        self.__discrete = False
        self.__createFunction = None

    def setRndNumber(self, dist):
        self.__rndNumber = dist
        return self

    def setSeqLength(self, length):
        """ Set the total length of the sequence
        The number of occurrences is calculated dynamically such that
        """
        self.__length = length
        return self

    def setNumberOfEvents(self, count):
        """ Set the number of events

        The sequence length is calculated dynamically such that enough events occurred
        """
        self.__numberEvents = count
        return self

    def setRules(self, rules):
        """ Add rules to this generator """
        self.__rules = []
        self.__lastTime = {}
        for rule in rules:
            self.__rules.append(rule)
            self.__lastTime[rule] = 0
        return self

    def setDiscrete(self):
        """ Call this function to create discrete sequences """
        self.__discrete = True
        return self

    def _create(self, file, normalization):
        rulesFile = None
        if (file is not None and isinstance(file, str)):
            # noinspection PyUnresolvedReferences
            config = os.path.toAbsolutePath(file)
            with open(config) as f:
                config = json.load(f)

            rulesFile = config["rules"] if "rules" in config else None
            self.__numberEvents = int(config["count"]) if "count" in config else -1
            self.__length = int(config["length"]) if "length" in config else -1

        if (self.__length == -1 and self.__numberEvents == -1):
            raise ValueError("Neither sequence length nor event count specified. Please provide at exactly one")
        if (self.__length != -1 and self.__numberEvents != -1):
            raise ValueError("Sequence length and event count specified. Please provide exactly one")
        if (len(self.__rules) == 0 and rulesFile is not None):
            rules = rule.loadFromFile(rulesFile)
            self.setRules(rules)
        if (self.__rules is None or len(self.__rules) == 0):
            raise RuntimeError("Configuration not valid. Please provide rules")

        if (self.__length != -1):
            self.__createFunction = self.__createByLength
        else:
            self.__createFunction = self.__createByNumberEvents

        return self.__createFunction()

    def __createByNumberEvents(self):
        timeline = {}
        while len(timeline) < self.__numberEvents:
            for rule in self.__rules:
                if (len(timeline) >= self.__numberEvents):
                    break

                timeTrigger = self.__getTimeStamp(rule.distributionTrigger, self.__lastTime[rule], timeline)
                self.__lastTime[rule] = timeTrigger
                trigger = Event(rule.trigger)
                self.__addEvent(timeline, timeTrigger, trigger, rule.successTrigger)

                if (len(timeline) >= self.__numberEvents):
                    break

                if (rule.response is not None):
                    timeResponse = self.__getTimeStamp(rule.distributionResponse, self.__lastTime[rule], timeline)
                    response = Event(rule.response)
                    trigger.setTriggered(response)
                    self.__addEvent(timeline, timeResponse, response, rule.successResponse)
        for rule in self.__rules:
            self.__lastTime[rule] = 0
        return self.__asSequence(timeline)

    def __createByLength(self):
        timeline = {}

        rules = copy.copy(self.__rules)
        while (len(rules) > 0):
            for rule in rules:
                timeTrigger = self.__getTimeStamp(rule.distributionTrigger, self.__lastTime[rule], timeline)
                if (timeTrigger >= self.__length):
                    rules.remove(rule)
                    continue

                self.__lastTime[rule] = timeTrigger
                trigger = Event(rule.trigger)
                self.__addEvent(timeline, timeTrigger, trigger, rule.successTrigger)

                if (rule.response is not None):
                    timeResponse = self.__getTimeStamp(rule.distributionResponse, self.__lastTime[rule], timeline)
                    if (timeResponse >= self.__length):
                        continue

                    response = Event(rule.response)
                    trigger.setTriggered(response)
                    self.__addEvent(timeline, timeResponse, response, rule.successResponse)
        for rule in self.__rules:
            self.__lastTime[rule] = 0
        return self.__asSequence(timeline, self.__length)

    def __getTimeStamp(self, dist, lastTime, timeline):
        time = dist.getRandom() + lastTime
        stepSize = 0.01
        if (self.__discrete):
            time = round(time)
            stepSize = 1
        while (time in timeline):
            time += stepSize
        return time

    def __addEvent(self, timeline, timestamp, event, success):
        if (self.__rndNumber.getRandom() > success):
            event.occurred = False
        event.timestamp = timestamp
        timeline[timestamp] = event

    def __asSequence(self, dictionary, length=-1):
        seq = list(dictionary.values())
        seq.sort()
        return Sequence(seq, length if length != -1 else math.ceil(seq[-1].timestamp) + 1, self.__rules)
