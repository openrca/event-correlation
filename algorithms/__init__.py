import abc
import logging

import numpy as np

from core.distribution import NormalDistribution
from core.performance import EnergyDistance, MutualInformationPerformance
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

    def matchAll(self, sequence, alpha=0.05, **kwargs):
        """ Finds all reasonable correlation in a sequence of events.
        Check parseArgs for additional parameters. All detected correlations are return as a list and stored in
        sequence.calculatedRules.
        """
        eventTypes = self.__cleanUpEventTypes(sequence)
        result = []

        for trigger in eventTypes:
            for response in eventTypes:
                # TODO decide A -> B or B -> A
                rule = self.__matchIfReasonable(sequence, trigger, response, alpha, **kwargs)
                if (rule is not None):
                    result.append(rule)
        return self.__cleanUpResult(result)

    def matchTransitive(self, sequence, start, alpha=0.05, **kwargs):
        nodes = [start]
        visited = []

        eventTypes = self.__cleanUpEventTypes(sequence)
        result = []

        while (len(nodes)):
            trigger = nodes.pop()
            if (trigger in visited):
                continue
            visited.append(trigger)
            self._logger.info("Testing '{}'".format(trigger))

            for response in eventTypes:
                rule = self.__matchIfReasonable(sequence, trigger, response, alpha, **kwargs)
                if (rule is not None):
                    result.append(rule)
                    nodes.append(response)
        return self.__cleanUpResult(result)

    @staticmethod
    def __cleanUpResult(result):
        l = []
        processed = set()
        for rule in result:
            pair = (rule.trigger, rule.response)
            if (pair in processed):
                continue
            processed.add(pair)
            l.append(rule)
        return l

    # noinspection PyMethodMayBeStatic
    def __cleanUpEventTypes(self, sequence, limit=5):
        result = []
        for eventType in sequence.eventTypes:
            if (len(sequence.getEvents(eventType)) > limit):
                result.append(eventType)
        return result

    def __matchIfReasonable(self, sequence, trigger, response, alpha, **kwargs):
        if (trigger == response):
            return None
        self._logger.debug("Matching '{}' with '{}'".format(trigger, response))

        seqTrigger = sequence.asVector(trigger)
        seqResponse = sequence.asVector(response)

        performance = EnergyDistance()
        score, pValue = performance.compute(seqTrigger, seqResponse)
        if (pValue <= alpha):
            self._logger.info("Found correlated events '{}' and '{}'".format(trigger, response))
            if (len(seqTrigger) < len(sequence.events) / 200 or len(seqResponse) < len(sequence.events) / 200):
                self._logger.warn("Too few samples. Skipping events")
                return None

            # noinspection PyNoneFunctionAssignment
            rule, data = self.match(sequence, trigger, response, **kwargs)
            return rule
        return None

    def match(self, sequence, trigger, response, enforceNormal=False, **kwargs):
        """ Computes a correlation of two event types. Check parseArgs for additional parameters. """
        self._sequence = sequence
        self._parseArgs(kwargs)
        triggerVector = self._sequence.asVector(trigger)
        responseVector = self._sequence.asVector(response)
        if (len(triggerVector) == 0 or len(responseVector) == 0):
            raise ValueError('No events with id {} and/or {} found.'.format(trigger, response))

        data = self._compute(triggerVector, responseVector)

        samples = data[RESULT_KDE].samples
        if (len(samples[samples < 0]) > len(samples) / 2):
            data[RESULT_KDE] = -data[RESULT_KDE]
            data[RESULT_MU] = -data[RESULT_MU]
            data[RESULT_IDX][:, 0], data[RESULT_IDX][:, 1] = data[RESULT_IDX][:, 1], data[RESULT_IDX][:, 0].copy()
            tmp = trigger
            trigger = response
            response = tmp

        dist = NormalDistribution(data[RESULT_MU], data[RESULT_SIGMA]) if enforceNormal else data[RESULT_KDE]
        rule = Rule(trigger, response, dist, data=data)

        performance = EnergyDistance()
        score, pValue = performance.compute(triggerVector, responseVector)
        rule.likelihood = score

        self.__fillRuleData(self._sequence.asVector(trigger), self._sequence.asVector(response), rule)
        self.__connectEventPairs(trigger, response, data[RESULT_IDX])

        return (rule, data)

    def _parseArgs(self, kwargs):
        pass

    @abc.abstractmethod
    def _compute(self, trigger, response):
        pass

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

    # noinspection PyMethodMayBeStatic
    def __fillRuleData(self, trigger, response, rule):
        distribution = rule.distributionResponse

        rule.successResponse = Matcher.__calculateRuleSuccess(trigger, response, distribution)
        rule.successTrigger = Matcher.__calculateRuleSuccess(response, trigger, -distribution)

        rule.data["Size"] = rule.data[RESULT_IDX].shape[0]
        # rule.data["Performance Range"] = RangePerformance().getValueByDistribution(distribution)
        # rule.data["Performance Variance"] = VariancePerformance().getValueByDistribution(distribution)
        # rule.data["Performance Std"] = StdPerformance().getValueByDistribution(distribution)
        # rule.data["Performance CondProd"] = CondProbPerformance(samples=distribution.samples).getValueByDistribution(
        #     distribution)
        # rule.data["Performance Entropy"] = EntropyPerformance().getValueByDistribution(distribution)
        rule.data["Mutual Information"] = MutualInformationPerformance(trigger, response, len(self._sequence)) \
            .getValueByDistribution(distribution)
        rule.data["Likelihood"] = rule.likelihood
        rule.data["Success Response"] = rule.successResponse
        rule.data["Success Trigger"] = rule.successTrigger

    @staticmethod
    def __calculateRuleSuccess(trigger, response, dist, threshold=0.05):
        count = 0
        for t in trigger:
            for r in response:
                if (dist.getPDFValue(r - t) > threshold):
                    count += 1
                    break
        return count / len(trigger)

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
