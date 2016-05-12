""" Automatically generated documentation for Generator """
import copy
import math

import core.distribution
import core.rule
from core.event import Event
from core.sequence import Sequence


class Generator:
    def __init__(self):
        self.length = -1
        self.numberEvents = -1
        self.entries = []
        self.rndNumber = core.distribution.UniformDistribution()
        self.discrete = False
        self._create = None

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

    def setEntries(self, entries):
        """ Add entries to this generator """
        for entry in entries:
            self.entries.append(entry)
        return self

    def setDiscrete(self):
        """ Call this function to create discrete sequences """
        self.discrete = True
        return self

    def createSequence(self, count=1):
        if (self.length != -1):
            self._create = self._createByLength
        elif (self.numberEvents != -1):
            self._create = self._createByNumberEvents
        else:
            raise RuntimeError("Configuration not valid. Please set either numberEvents or sequence length")

        if (len(self.entries) == 0):
            raise RuntimeError("Configuration not valid. Please provide entries")

        if (count == 1):
            return [self._create()]

        sequences = []
        for i in range(count):
            sequences.append(self._create())
        return sequences

    def _createByNumberEvents(self):
        timeline = {}
        while len(timeline) < self.numberEvents:
            for entry in self.entries:
                if (len(timeline) >= self.numberEvents):
                    break

                timeTrigger = self._getTimeStamp(entry.dist, entry.lastTime, timeline)
                entry.lastTime = timeTrigger
                trigger = Event(entry.rule.trigger)
                self._addEvent(timeline, timeTrigger, trigger, entry.rule.triggerConfidence)

                if (len(timeline) >= self.numberEvents):
                    break

                timeResponse = self._getTimeStamp(entry.rule.distribution, entry.lastTime, timeline)
                response = Event(entry.rule.response)
                trigger.setTriggered(response)
                self._addEvent(timeline, timeResponse, response, entry.rule.responseConfidence)
        return self._asSequence(timeline)

    def _createByLength(self):
        timeline = {}

        entries = copy.copy(self.entries)
        while (len(entries) > 0):
            for entry in self.entries:
                timeTrigger = self._getTimeStamp(entry.dist, entry.lastTime, timeline)
                if (timeTrigger >= self.length):
                    entries.remove(entry)
                    continue

                entry.lastTime = timeTrigger
                trigger = Event(entry.rule.trigger)
                self._addEvent(timeline, timeTrigger, trigger, entry.rule.triggerConfidence)

                timeResponse = self._getTimeStamp(entry.rule.distribution, entry.lastTime, timeline)
                if (timeResponse >= self.length):
                    continue

                response = Event(entry.rule.response)
                trigger.setTriggered(response)
                self._addEvent(timeline, timeResponse, response, entry.rule.responseConfidence)
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

    def _addEvent(self, timeline, timestamp, event, confidence):
        if (self.rndNumber.getRandom() > confidence):
            event.occurred = False
        event.timestamp = timestamp
        timeline[timestamp] = event

    @staticmethod
    def _asSequence(dictionary, length=-1):
        seq = list(dictionary.values())
        seq.sort()
        return Sequence(seq, length if length != -1 else math.ceil(seq[-1].timestamp) + 1)
