import abc
import logging

import aniso8601

logging.getLogger().setLevel(logging.DEBUG)


class SequenceParser(abc.ABC):
    @abc.abstractmethod
    def create(self, file, filter=None, whitelist=None, normalization=1):
        pass

    # noinspection PyMethodMayBeStatic
    def _parseISO8601(self, timeString):
        return aniso8601.parse_datetime(timeString).timestamp()
