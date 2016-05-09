""" Automatically generated documentation for Generator """
import bisect
import collections

import core.distribution
import core.rule
from core.event import Event
from core.sequence import Sequence

PendingEvent = collections.namedtuple("PendingEvent", ["timestamp", "event", "confidence"])


class Generator:
    def __init__(self):
        self.length = -1
        self.numberEvents = -1
        self.entries = []
        self.rndNumber = core.distribution.UniformDistribution()
        self.pendingEvents = []
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
        timeline = []
        while len(timeline) < self.numberEvents:
            for entry in self.entries:
                if (len(timeline) >= self.numberEvents):
                    break
                timeTrigger = entry.dist.getRandom() + entry.lastTime
                entry.lastTime = timeTrigger
                trigger = Event(entry.rule.getTrigger())
                self.__addEvent(timeline, PendingEvent(timeTrigger, trigger, entry.rule.getTriggerConfidence()))

                if (len(timeline) >= self.numberEvents):
                    break
                timeResponse = entry.rule.getDistribution().getRandom() + entry.lastTime
                response = Event(entry.rule.getResponse())
                trigger.setTriggered(response)
                self.__addEvent(timeline, PendingEvent(timeResponse, response, entry.rule.getResponseConfidence()))
        timeline.sort()
        return Sequence(timeline, timeline[-1].getTimestamp() + 1)

    def __createByLength(self):
        timeline = []
        for t in range(0, self.length):
            pendingEvent = self.__getPendingEvent(t)
            if (pendingEvent is not None):
                self.__addEvent(timeline, PendingEvent(t, pendingEvent.event, pendingEvent.confidence))
                continue

            entry = self.__findNextEntry(t)
            if (entry is None):
                continue

            trigger = Event(entry.rule.getTrigger())
            response = Event(entry.rule.getResponse())
            self.__addEvent(timeline, PendingEvent(t, trigger, entry.rule.getTriggerConfidence()))

            entry.lastTime = t
            trigger.setTriggered(response)

            self.__addPendingEvent(entry, t, response)
        return Sequence(timeline, self.length)

    def __findNextEntry(self, t):
        entries = self.entries
        # entries = np.random.permutation(self.entries)
        for entry in entries:
            value = self.rndNumber.getRandom()
            if (value < entry.getOccurrenceProb(t)):
                return entry
        return None

    def __getPendingEvent(self, t):
        if (len(self.pendingEvents) == 0):
            return None
        if (self.pendingEvents[0].event.getTimestamp() <= t):
            return self.pendingEvents.pop(0)
        return None

    def __addPendingEvent(self, entry, t, response):
        response.setTimestamp(round(t + entry.rule.getResponseTimestamp()))
        pendingEvent = PendingEvent(timestamp=response.getTimestamp(), event=response,
                                    confidence=entry.rule.getResponseConfidence())
        bisect.insort(self.pendingEvents, pendingEvent)

    def __addEvent(self, timeline, pendingEvent):
        if (self.rndNumber.getRandom() > pendingEvent.confidence):
            pendingEvent.event.setOccurred(False)
        pendingEvent.event.setTimestamp(pendingEvent.timestamp)
        timeline.append(pendingEvent.event)
