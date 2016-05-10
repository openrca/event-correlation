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
        self.__create = None

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
            self.__create = self.__createByLength
        elif (self.numberEvents != -1):
            self.__create = self.__createByNumberEvents
        else:
            raise RuntimeError("Configuration not valid. Please set either numberEvents or sequence length")

        if (len(self.entries) == 0):
            raise RuntimeError("Configuration not valid. Please provide entries")

        if (count == 1):
            return [self.__create()]

        sequences = []
        for i in range(0, count):
            sequences.append(self.__create())
        return sequences

    def __createByNumberEvents(self):
        timeline = {}
        while len(timeline) < self.numberEvents:
            for entry in self.entries:
                if (len(timeline) >= self.numberEvents):
                    break

                timeTrigger = self.__getTimeStamp(entry.dist, entry.lastTime, timeline)
                entry.lastTime = timeTrigger
                trigger = Event(entry.rule.getTrigger())
                self.__addEvent(timeline, timeTrigger, trigger, entry.rule.getTriggerConfidence())

                if (len(timeline) >= self.numberEvents):
                    break

                timeResponse = self.__getTimeStamp(entry.rule.getDistribution(), entry.lastTime, timeline)
                response = Event(entry.rule.getResponse())
                trigger.setTriggered(response)
                self.__addEvent(timeline, timeResponse, response, entry.rule.getResponseConfidence())
        return self.__asSequence(timeline)

    def __createByLength(self):
        timeline = {}

        entries = copy.copy(self.entries)
        while (len(entries) > 0):
            for entry in self.entries:
                timeTrigger = self.__getTimeStamp(entry.dist, entry.lastTime, timeline)
                if (timeTrigger >= self.length):
                    entries.remove(entry)
                    continue

                entry.lastTime = timeTrigger
                trigger = Event(entry.rule.getTrigger())
                self.__addEvent(timeline, timeTrigger, trigger, entry.rule.getTriggerConfidence())

                timeResponse = self.__getTimeStamp(entry.rule.getDistribution(), entry.lastTime, timeline)
                if (timeResponse >= self.length):
                    continue

                response = Event(entry.rule.getResponse())
                trigger.setTriggered(response)
                self.__addEvent(timeline, timeResponse, response, entry.rule.getResponseConfidence())
        return self.__asSequence(timeline, self.length)

    def __getTimeStamp(self, dist, lastTime, timeline):
        time = dist.getRandom() + lastTime
        stepSize = 0.01
        if (self.discrete):
            time = round(time)
            stepSize = 1
        while (time in timeline):
            time += stepSize
        return time

    def __addEvent(self, timeline, timestamp, event, confidence):
        if (self.rndNumber.getRandom() > confidence):
            event.setOccurred(False)
        event.setTimestamp(timestamp)
        timeline[timestamp] = event

    @staticmethod
    def __asSequence(dictionary, length=-1):
        seq = list(dictionary.values())
        seq.sort()
        return Sequence(seq, length if length != -1 else math.ceil(seq[-1].getTimestamp()) + 1)
