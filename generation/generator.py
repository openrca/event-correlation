""" Automatically generated documentation for Generator """

import bisect
import collections

import core.distribution
import core.event
import core.rule
from core.sequence import Sequence

PendingEvent = collections.namedtuple("PendingEvent", ["timestamp", "event", "confidence"])


class Entry:
    def __init__(self, rule: core.rule.Rule, dist=core.distribution.ExponentialDistribution(), scale=1):
        self.rule = rule
        self.lastTime = -1
        self.dist = dist
        self.scale = scale

    def getOccurrenceProb(self, t):
        return self.dist.getCDFValue(t - self.lastTime) * self.scale


class Generator:
    def __init__(self):
        self.length = 100
        self.entries = []
        self.rndNumber = core.distribution.UniformDistribution()
        self.pendingEvents = []

    def setRndNumber(self, dist):
        self.rndNumber = dist
        return self

    def setSeqLength(self, length):
        self.length = length
        return self

    def setRules(self, rules):
        """ Add rules to this generator

        Rules have to be a list of tuples with the following entries
            rule: A core.rule.Rule
            dist: A subclass of generation.distribution.Distribution. This distribution is used to determine the next
                occurrence of rule.trigger
            scale: An optional scale to influence the occurrence probability. Scale > 1 increases the probability and
                scale < 1 vice versa
        """

        for rule, dist, scale in rules:
            self.entries.append(Entry(rule, dist, scale))
        return self

    def createSequence(self, count=1):
        # TODO validate configuration

        if (count == 1):
            return [self.__create()]

        sequences = []
        for i in range(0, count):
            sequences.append(self.__create())
        return sequences

    def __create(self):
        timeline = []
        for t in range(0, self.length):
            pendingEvent = self.__getPendingEvent(t)
            if (pendingEvent is not None):
                self.__addEvent(timeline, PendingEvent(t, pendingEvent.event, pendingEvent.confidence))
                continue

            entry = self.__findNextEntry(t)
            if (entry is None):
                continue

            trigger = entry.rule.getTrigger()
            response = entry.rule.getResponse()
            self.__addEvent(timeline, PendingEvent(t, trigger, entry.rule.getTriggerConfidence()))

            entry.lastTime = t
            trigger.setTriggered(response)

            self.__addPendingEvent(entry, t, response)
        return Sequence(timeline, self.length)

    def __findNextEntry(self, t):
        entries = self.entries
        # entries = np.random.permutation(self.entries)
        for entry in entries:
            value = self.rndNumber.getPDFValue()
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
        response.setTimestamp(int(t + entry.rule.getResponseTimestamp()))
        pendingEvent = PendingEvent(timestamp=response.getTimestamp(), event=response,
                                    confidence=entry.rule.getResponseConfidence())
        bisect.insort(self.pendingEvents, pendingEvent)

    def __addEvent(self, timeline, pendingEvent):
        if (self.rndNumber.getPDFValue() > pendingEvent.confidence):
            pendingEvent.event.setOccurred(False)
        pendingEvent.event.setTimestamp(pendingEvent.timestamp)
        timeline.append(pendingEvent.event)
