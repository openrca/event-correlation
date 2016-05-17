import abc
import logging

logging.TRACE = 5
logging.addLevelName(logging.TRACE, "TRACE")


def trace(self, message, *args, **kws):
    if self.isEnabledFor(logging.TRACE):
        self._log(logging.TRACE, message, args, **kws)


logging.Logger.trace = trace


class Matcher:
    def __init__(self, name):
        self.name = name
        self.logger = None
        self._initLogging()

    def _initLogging(self):
        self.logger = logging.getLogger(self.name)
        if (len(self.logger.handlers) == 0):
            handler = logging.StreamHandler()
            handler.setLevel(logging.INFO)

            formatter = logging.Formatter('%(asctime)s - %(name)s: %(levelname)s - %(message)s')
            handler.setFormatter(formatter)

            self.logger.setLevel(logging.TRACE)
            self.logger.propagate = False
            self.logger.addHandler(handler)

    @abc.abstractmethod
    def parseArgs(self, kwargs):
        pass

    @abc.abstractmethod
    def match(self, **kwargs):
        pass
