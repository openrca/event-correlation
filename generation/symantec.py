import json
import os
from xml.etree.ElementTree import ElementTree

import aniso8601

from core import sequence
from core.event import Event
from core.sequence import Sequence


class SymantecParser():
    def __init__(self):
        self.cacheDir = "/tmp/ec/cache"
        self.nameSpace = {"ev": "http://schemas.microsoft.com/win/2004/08/events/event"}

        # noinspection PyUnresolvedReferences
        with open(os.path.toAbsolutePath("../contrib/symantecKnowledgeBase.json")) as f:
            self.knowledgeBase = json.load(f)["events"]

    def clearCache(self):
        """ Clear all cached results """
        for file in os.scandir(self.cacheDir):
            if file.is_file:
                os.unlink(file.path)

    def parse(self, file):
        """
        This method parses a Symantec xml log file into a Sequence. For multiple consecutive calls, the parsed sequence
        is cached in 'cacheDir'.
        :param file:
        :return:
        """
        # noinspection PyUnresolvedReferences
        file = os.path.toAbsolutePath(file)
        fileName = self._getFileName(file)

        seq = self._loadFromCache(fileName)
        if (seq is not None):
            return seq

        count = {}
        events = []
        root = ElementTree().parse(file)
        for event in root:
            system = event.find("ev:System", namespaces=self.nameSpace)
            eventId = int(system.find("ev:EventID", namespaces=self.nameSpace).text)
            time = self._parseISO8601(system.find("ev:TimeCreated", namespaces=self.nameSpace).attrib["SystemTime"])

            events.append(Event(eventId, time))
            if eventId in count:
                count[eventId] += 1
            else:
                count[eventId] = 1
        self._printStatistic(root, count)
        return Sequence(events)

    # noinspection PyMethodMayBeStatic
    def _getFileName(self, file):
        return os.path.splitext(os.path.basename(file))[0]

    def _loadFromCache(self, file):
        cacheFile = os.path.join(self.cacheDir, file)
        if (os.path.isfile(cacheFile)):
            try:
                return sequence.loadFromFile(cacheFile)
            except ValueError:
                pass
        return None

    def _storeInCache(self, file, seq):
        cacheFile = os.path.join(self.cacheDir, file)
        seq.store(cacheFile)

    # noinspection PyMethodMayBeStatic
    def _parseISO8601(self, timeString):
        return aniso8601.parse_datetime(timeString).timestamp()

    def _printStatistic(self, root, count):
        print("# Events: {}".format(len(root)))
        l = list(count.keys())
        l.sort()
        for i in l:
            print("EventID {}:\t{},\t#{}".format(i, self.knowledgeBase[str(i)]["desc"], count[i]))
