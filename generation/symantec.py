import json
import os
from xml.etree.ElementTree import ElementTree

import aniso8601

from core.event import Event
from core.sequence import Sequence


class SymantecParser():
    def __init__(self):
        self.nameSpace = {"ev": "http://schemas.microsoft.com/win/2004/08/events/event"}

        # noinspection PyUnresolvedReferences
        with open(os.path.toAbsolutePath("../contrib/symantecKnowledgeBase.json")) as f:
            self.knowledgeBase = json.load(f)["events"]

    def parse(self, file, filter=None, whitelist=None, normalization=1):
        """
        This method parses a Symantec xml log file into a Sequence. For multiple consecutive calls, the parsed sequence
        is cached in 'cacheDir'.
        :param normalization:
        :param whitelist:
        :param file:
        :return:
        """
        # noinspection PyUnresolvedReferences
        if filter is None:
            filter = []
        if whitelist is None:
            whitelist = []
        file = os.path.toAbsolutePath(file)

        count = {}
        events = []
        root = ElementTree().parse(file)
        for event in root:
            system = event.find("ev:System", namespaces=self.nameSpace)
            eventId = str(system.find("ev:EventID", namespaces=self.nameSpace).text)
            time = self._parseISO8601(
                system.find("ev:TimeCreated", namespaces=self.nameSpace).attrib["SystemTime"]) / normalization

            if (eventId in filter):
                continue

            if (len(whitelist) == 0 or eventId in whitelist):
                events.append(Event(eventId, time))
                if eventId in count:
                    count[eventId] += 1
                else:
                    count[eventId] = 1
        self._printStatistic(root, count)
        return Sequence(events)

    # noinspection PyMethodMayBeStatic
    def _parseISO8601(self, timeString):
        return aniso8601.parse_datetime(timeString).timestamp()

    def _printStatistic(self, root, count):
        print("# Events: {}".format(len(root)))
        l = list(count.keys())
        l.sort()
        for i in l:
            print("EventID {}:\t{},\t#{}".format(i, self.knowledgeBase[str(i)]["desc"], count[i]))
