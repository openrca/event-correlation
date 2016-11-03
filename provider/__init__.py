import abc
import logging
import os

import aniso8601

from core.event import Event

logging.getLogger().setLevel(logging.DEBUG)

GENERATE = 'gen'
LOAD = 'load'
SYMANTEC = 'symantec'
PRINTER = 'printer'

CHOICES = [GENERATE, LOAD, SYMANTEC, PRINTER]


class SequenceParser(abc.ABC):
    def __init__(self):
        self._count = {}
        self._events = []
        self._filter = []
        self._whitelist = []

    # noinspection PyShadowingBuiltins
    def create(self, file, filter=None, whitelist=None, normalization=1):
        """
        This method creates a new sequence based on the given file. The actual creation is implemented by subclasses.
        :param filter:
        :param normalization:
        :param whitelist:
        :param file:
        :return:
        """
        # noinspection PyUnresolvedReferences
        if filter is not None:
            self._filter = filter
        if whitelist is not None:
            self._whitelist = whitelist
        if (file is not None):
            # noinspection PyUnresolvedReferences
            file = os.path.toAbsolutePath(file)

        return self._create(file, normalization)

    @abc.abstractmethod
    def _create(self, file, normalization):
        pass

    # noinspection PyMethodMayBeStatic
    def _parseISO8601(self, timeString):
        return aniso8601.parse_datetime(timeString).timestamp()

    def _createEvent(self, eventId, timestamp):
        if (eventId not in self._filter and (len(self._whitelist) == 0 or eventId in self._whitelist)):
            self._events.append(Event(eventId, timestamp))
            if eventId in self._count:
                self._count[eventId] += 1
            else:
                self._count[eventId] = 1
