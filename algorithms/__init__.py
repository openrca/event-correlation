import abc
import logging

import numpy as np

from core.performance import EnergyStatistic
from core.rule import Rule

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
        self.logger = logging.getLogger(self.name)
        self.zScore = CONFIDENCE_90
        np.set_printoptions(precision=4, linewidth=150, threshold=10000)

        self.sequence = None
        self.eventA = None
        self.eventB = None

    def trimVector(self, data):
        """ Remove potential outliers.
        This leads to worse results for simple associations but improves performance for complex associations with
        success < 1
        """
        data.sort()
        result = data[abs(data - data.mean()) < self.zScore * data.std()]
        self.logger.debug("Kept {} / {} samples".format(result.size, data.size))
        return result

    @staticmethod
    def idxToSamples(idx, samples):
        """
        Takes the vector of occurrence timestamps and transforms them to samples of an underlying distribution.
        The idx vector indicates which samples are really relevant. The inter-arrival distance is considered.
        """

        tmp = np.concatenate(([0], samples))
        tmp = np.diff(tmp)
        return tmp[idx]

    def matchAll(self, sequence, **kwargs):
        """ Finds all reasonable correlation in a sequence of events.
        Check parseArgs for additional parameters. All detected correlations are return as a list and stored in
        sequence.calculatedCorrelations.
        Additional parameters:
            alpha: Significance level alpha for correlation hypothesis test. Default is 0.05.
        """
        alpha = 0.05
        if ("alpha" in kwargs):
            alpha = kwargs["alpha"]

        performance = EnergyStatistic()

        for eventA in sequence.eventTypes:
            for eventB in sequence.eventTypes:
                # TODO decide A -> B or B -> A

                if (eventA == eventB):
                    continue
                self.logger.debug("Matching '{}' with '{}'".format(eventA, eventB))

                seqA = sequence.asVector(eventA)
                seqB = sequence.asVector(eventB)

                score, pValue = performance.compute(seqA, seqB)
                if (pValue <= alpha):
                    self.logger.info("Found correlated events '{}' and '{}'".format(eventA, eventB))
                    # noinspection PyNoneFunctionAssignment
                    param = self.match(sequence, eventA, eventB, **kwargs)
                    sequence.calculatedRules.append(Rule(eventA, eventB, param[RESULT_KDE], param=param))
        return sequence.calculatedRules

    def match(self, sequence, eventA, eventB, **kwargs):
        """ Computes a correlation of two event types. Check parseArgs for additional parameters. """
        self.sequence = sequence
        self.eventA = eventA
        self.eventB = eventB
        self.parseArgs(kwargs)
        return self.compute()

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
