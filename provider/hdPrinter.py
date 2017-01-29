import csv
import re

from core.sequence import Sequence
from provider import SequenceParser


class HDPrinterParser(SequenceParser):
    def __init__(self):
        super().__init__()
        self.__COLUMN_TIMESTAMP = 2
        self.__COLUMN_EVENT_ID = 3
        self.__COLUMN_STATUS = 5

    def _create(self, file, normalization):
        with open(file) as csvFile:
            reader = csv.reader(csvFile, delimiter=';')
            next(reader, None)  # skip the header

            for row in reader:
                timestamp = self._parseISO8601(row[self.__COLUMN_TIMESTAMP]) / normalization
                eventId = row[self.__COLUMN_EVENT_ID]
                status = row[self.__COLUMN_STATUS]

                if (status == 'RESET'):
                    continue

                self._createEvent(eventId, timestamp)

        self.__printStatistic()
        return Sequence(self._events)

    def chunkSequence(self, file, output, offset=1800):
        self.create(file)

        subSequences = []
        current = None
        start = None
        for event in reversed(self._events):
            if (re.match('^0X5001[\dA-F]$', event.eventType) is not None):
                if (current is None):
                    current = [event]
                start = event
            elif (current is not None):
                if (start.timestamp - event.timestamp < offset):
                    current.append(event)
                else:
                    subSequences.append(Sequence(list(reversed(current))))
                    current = None
        if (current is not None):
            subSequences.append(Sequence(list(reversed(current))))

        for idx, seq in enumerate(subSequences):
            seq.store('{}-{}.seq'.format(output, idx))

    def trimSequence(self, file, output, offset=1800):
        self.create(file)

        events = []
        start = None
        for event in reversed(self._events):
            if (re.match('^0X5001[\dA-F]$', event.eventType) is not None):
                start = event
            if (start is not None and start.timestamp - event.timestamp < offset):
                events.append(event)
        Sequence(list(reversed(events))).store(output)

    def __printStatistic(self):
        print("# Events: {}".format(len(self._events)))
        l = list(self._count.keys())
        l.sort()
        for i in l:
            print("EventID {}: \t#{}".format(i, self._count[i]))
