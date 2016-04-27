""" Automatically generated documentation for Event """


class Event:
    def __init__(self, eventType, timestamp=None):
        self.eventType = eventType
        if (timestamp is None):
            timestamp = -1
        self.timestamp = timestamp
        self.occurred = True
        self.triggeredBy = None
        self.triggered = None

    def getEventType(self):
        return self.eventType

    def getTimestamp(self):
        return self.timestamp

    def hasOccurred(self):
        return self.occurred

    def getTriggeredBy(self):
        return self.triggeredBy

    def getTriggered(self):
        return self.triggered

    def setOccurred(self, occurred):
        self.occurred = occurred

    def setTriggeredBy(self, event):
        self.triggeredBy = event

    def setTriggered(self, event):
        self.triggered = event

    def setTimestamp(self, timestamp):
        self.timestamp = timestamp

    def getExternalRepresentation(self):
        if (self.occurred):
            return self.eventType
        else:
            return "*"

    def __eq__(self, other):
        if (not isinstance(other, self.__class__)):
            return False
        return self.eventType == other.eventType and self.timestamp == other.timestamp

    def __hash__(self):
        return hash(self.eventType) + hash(self.timestamp)

    def __str__(self):
        return "Event: {} ({})".format(str(self.eventType), str(self.timestamp))

    def __repr__(self):
        return self.__str__()

    def __copy__(self):
        return Event(self.eventType, self.timestamp)


def load(value):
    """ Load an event from a json string"""

    try:
        e = Event(value["eventType"])

        if ("timestamp" in value):
            e.setTimestamp(int(value["timestamp"]))
        if ("triggered" in value):
            e.setTriggered(load(value["triggered"]))
        if ("triggeredBy" in value):
            e.setTriggeredBy(load(value["triggeredBy"]))
        return e
    except KeyError as ex:
        raise ValueError("Missing parameter 'eventType'")
