import abc
import logging


class Matcher:
    def __init__(self, name):
        self.name = name
        self.logger = None
        self.__initLogging()

    def __initLogging(self):
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)

        formatter = logging.Formatter('%(asctime)s - %(name)s: %(levelname)s - %(message)s')
        handler.setFormatter(formatter)

        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(logging.DEBUG)
        self.logger.propagate = False
        self.logger.addHandler(handler)

    @abc.abstractmethod
    def parseArgs(self, kwargs):
        pass

    @abc.abstractmethod
    def match(self, **kwargs):
        pass
