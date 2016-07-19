import abc
import logging

import numpy as np

logging.TRACE = 5
logging.addLevelName(logging.TRACE, "TRACE")


def trace(self, message, *args, **kws):
    if self.isEnabledFor(logging.TRACE):
        self._log(logging.TRACE, message, args, **kws)


logging.Logger.trace = trace

RESULT_MU = "Mu"
RESULT_SIGMA = "Sigma"
RESULT_KDE = "Kde"
RESULT_IDX = "Index"

CONFIDENCE_50 = 0.674
CONFIDENCE_80 = 1.282
CONFIDENCE_90 = 1.645
CONFIDENCE_95 = 1.960
CONFIDENCE_99 = 2.576


class Matcher(abc.ABC):
    def __init__(self, name):
        if (name is None):
            name = __name__
        self.name = name
        self.logger = None
        self.zScore = CONFIDENCE_90
        self._initLogging()
        np.set_printoptions(precision=4, linewidth=150, threshold=10000)

        self.sequence = None
        self.eventA = None
        self.eventB = None

    def _initLogging(self):
        self.logger = logging.getLogger(self.name)
        if (len(self.logger.handlers) == 0):
            handler = logging.StreamHandler()
            handler.setLevel(logging.TRACE)

            formatter = logging.Formatter('%(asctime)s - %(name)s: %(levelname)s - %(message)s')
            handler.setFormatter(formatter)

            self.logger.setLevel(logging.TRACE)
            self.logger.propagate = False
            self.logger.addHandler(handler)

    def match(self, sequence, eventA, eventB, **kwargs):
        """ Computes a correlation of two event types. Check parseArgs for additional parameters. """
        self.sequence = sequence
        self.eventA = eventA
        self.eventB = eventB
        self.parseArgs(kwargs)
        return self.compute()

    def trimVector(self, data):
        """ Remove potential outliers.
        This leads to worse results for simple associations but improves performance for complex associations with
        success < 1
        """
        data.sort()
        result = data[abs(data - data.mean()) < self.zScore * data.std()]
        self.logger.debug("Kept {} / {} samples".format(result.size, data.size))
        return result

    @abc.abstractmethod
    def parseArgs(self, kwargs):
        pass

    @abc.abstractmethod
    def compute(self):
        pass


class InitialGuess(abc.ABC):
    @abc.abstractmethod
    def computeOffset(self, data, model):
        pass
