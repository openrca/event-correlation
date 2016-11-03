import abc
import logging

import numpy as np

from core.performance import EnergyStatistic, RangePerformance, VariancePerformance, StdPerformance, \
    CondProbPerformance, EntropyPerformance
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
        self._logger = logging.getLogger(name)
        self._logger.setLevel(logging.TRACE)
        self.trimCost = True
        self.zScore = CONFIDENCE_50
        np.set_printoptions(precision=4, linewidth=150, threshold=10000)

        self._sequence = None

    def _trimVector(self, data):
        """ Remove potential outliers.
        This leads to worse results for simple associations but improves performance for complex associations with
        success < 1
        """
        if (not self.trimCost):
            return data

        data.sort()
        result = data[abs(data - np.median(data)) <= self.zScore * data.std()]
        self._logger.debug("Kept {} / {} samples".format(result.size, data.size))
        return result

    def matchAll(self, sequence, **kwargs):
        """ Finds all reasonable correlation in a sequence of events.
        Check parseArgs for additional parameters. All detected correlations are return as a list and stored in
        sequence.calculatedRules.
        Additional parameters:
            alpha: Significance level alpha for correlation hypothesis test. Default is 0.05.
        """
        alpha = 0.05
        if ("alpha" in kwargs):
            alpha = kwargs["alpha"]

        performance = EnergyStatistic()
        eventTypes = self.__cleanUpEventTypes(sequence)
        result = []

        for trigger in eventTypes:
            for response in eventTypes:
                # TODO decide A -> B or B -> A

                if (trigger == response):
                    continue
                self._logger.debug("Matching '{}' with '{}'".format(trigger, response))

                seqTrigger = sequence.asVector(trigger)
                seqResponse = sequence.asVector(response)

                score, pValue = performance.compute(seqTrigger, seqResponse)
                if (pValue <= alpha):
                    self._logger.info("Found correlated events '{}' and '{}'".format(trigger, response))
                    if (len(seqTrigger) < len(sequence.events) / 200 or len(seqResponse) < len(sequence.events) / 200):
                        self._logger.warn("Too few samples. Skipping events")
                        continue

                    # noinspection PyNoneFunctionAssignment
                    rule, data = self.match(sequence, trigger, response, **kwargs)
                    result.append(rule)
        return result

    # noinspection PyMethodMayBeStatic
    def __cleanUpEventTypes(self, sequence):
        result = []
        for eventType in sequence.eventTypes:
            if (len(sequence.getEvents(eventType)) > 5):
                result.append(eventType)
        return result

    def match(self, sequence, trigger, response, **kwargs):
        """ Computes a correlation of two event types. Check parseArgs for additional parameters. """
        self._sequence = sequence
        self._parseArgs(kwargs)
        triggerVector = self._sequence.asVector(trigger)
        responseVector = self._sequence.asVector(response)
        if (len(triggerVector) == 0 or len(responseVector) == 0):
            raise ValueError('No events with id {} and/or {} found.'.format(trigger, response))

        data = self._compute(triggerVector, responseVector)
        rule = Rule(trigger, response, data[RESULT_KDE], data=data)
        self.__fillRuleData(rule, rule.distributionResponse)
        self.__connectEventPairs(trigger, response, data[RESULT_IDX])
        return (rule, data)

    def _parseArgs(self, kwargs):
        pass

    @abc.abstractmethod
    def _compute(self, trigger, response):
        pass

    # noinspection PyMethodMayBeStatic
    def __fillRuleData(self, rule, distribution):
        rule.data["Performance Range"] = RangePerformance().getValueByDistribution(distribution)
        rule.data["Performance Variance"] = VariancePerformance().getValueByDistribution(distribution)
        rule.data["Performance Std"] = StdPerformance().getValueByDistribution(distribution)
        rule.data["Performance CondProd"] = CondProbPerformance(samples=distribution.samples).getValueByDistribution(
            distribution)
        rule.data["Performance Entropy"] = EntropyPerformance().getValueByDistribution(distribution)
        rule.data["Metric Pearson"] = 0
        rule.data["Metric Distance"] = 0
        rule.data["Metric Energy"] = 0

    def __connectEventPairs(self, trigger, response, idx):
        # TODO what happens if one event is connected several times?
        if (idx is None):
            return
        t = self._sequence.getEvents(trigger)
        r = self._sequence.getEvents(response)
        for idxTrigger, idxResponse in idx:
            t[idxTrigger].setTriggered(r[idxResponse])


class InitialGuess(abc.ABC):
    @abc.abstractmethod
    def computeOffset(self, data, model):
        pass
