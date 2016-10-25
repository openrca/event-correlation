import json
import os
from xml.etree.ElementTree import ElementTree

from core.sequence import Sequence
from provider import SequenceParser


class SymantecParser(SequenceParser):
    def __init__(self):
        super().__init__()
        self.nameSpace = {"ev": "http://schemas.microsoft.com/win/2004/08/events/event"}

        # noinspection PyUnresolvedReferences
        with open(os.path.toAbsolutePath("../contrib/symantecKnowledgeBase.json")) as f:
            self.knowledgeBase = json.load(f)["events"]

    def _create(self, file, normalization):
        root = ElementTree().parse(file)
        for event in root:
            system = event.find("ev:System", namespaces=self.nameSpace)
            eventId = str(system.find("ev:EventID", namespaces=self.nameSpace).text)
            time = self._parseISO8601(
                system.find("ev:TimeCreated", namespaces=self.nameSpace).attrib["SystemTime"]) / normalization
            self._createEvent(eventId, time)

        self._printStatistic()
        return Sequence(self.events)

    def _printStatistic(self):
        print("# Events: {}".format(len(self.events)))
        l = list(self.count.keys())
        l.sort()
        for i in l:
            print("EventID {}:\t{},\t#{}".format(i, self.knowledgeBase[str(i)]["desc"], self.count[i]))
