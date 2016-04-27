from core.event import Event


class Sequence:
    def __init__(self, events, length):
        self.events = events
        self.length = length

    def getLength(self):
        return self.length

    def getEvents(self):
        return self.events

    def getEvent(self, index):
        for i in range(0, len(self.events)):
            event = self.events[i]

            if (index < event.getTimestamp()):
                break
            if (event.getTimestamp() == index):
                return event
        return Event("-", index)
