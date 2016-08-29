import abc
import math
import numbers

import numpy as np
import scipy.stats

from core import distribution
from core.distribution import KDE


class Performance(abc.ABC):
    """
    Scores a single distribution for its 'sharpness'. A distribution is sharp if the interval of likely values is small.
    """

    @abc.abstractmethod
    def getValueBySamples(self, samples):
        pass

    @abc.abstractmethod
    def getValueByDistribution(self, dist):
        pass


class RangePerformance(Performance):
    """
    Calculate performance based on maximum distance between points.

    Performance is |max(samples) - min(samples)|
    """

    def getValueByDistribution(self, dist):
        borders = dist.getCompleteInterval()
        return (abs(borders[0] - borders[1]))

    def getValueBySamples(self, samples):
        return abs(samples.max() - samples.min())


class VariancePerformance(Performance):
    """ Calculate performance based on sample variance. """

    def getValueByDistribution(self, dist):
        return dist.getVar()

    def getValueBySamples(self, samples):
        return np.array(samples).var()


class StdPerformance(Performance):
    """ Calculate performance based on sample standard deviation. """

    def getValueByDistribution(self, dist):
        return dist.getStd()

    def getValueBySamples(self, samples):
        return np.array(samples).std()


class CondProbPerformance(Performance):
    """
    Calculate performance based on average conditional probability.

    The samples represent conditional values drawn from an underlying distribution. This class creates a distribution
    from the samples and averages the probability of all samples. To eliminate effects of numerical underflows, the
    logarithmic value is calculated. Furthermore, as all probabilities are smaller than 1, the absolute value is
    returned.
    """

    def __init__(self, dist=KDE, samples=None):
        super().__init__()
        self.dist = dist
        self.samples = samples

    def getValueByDistribution(self, dist):
        if (self.samples is None):
            return 0
        return self._calculate(self.samples, dist)

    def getValueBySamples(self, samples):
        dist = self.dist
        if (isinstance(self.dist, numbers.Number)):
            dist = distribution.samplesToDistribution(samples, self.dist)
        return self._calculate(samples, dist)

    @staticmethod
    def _calculate(samples, dist):
        return np.log(dist.getPDFValue(samples)).mean()


class EntropyPerformance(Performance):
    """
    Calculate performance based on entropy.

    The samples represent conditional values drawn from an underlying distribution. This class creates a distribution
    from the samples and draws the according probabilities. From this probabilities the normalized entropy is
    calculated.
    """

    def __init__(self, dist=KDE):
        super().__init__()
        self.dist = dist

    def getValueByDistribution(self, dist, n=10000):
        borders = dist.getCompleteInterval()
        h = dist.getDifferentialEntropy()
        return (h - (borders[1] - borders[0]) / n) / math.log2(n)

    def getValueBySamples(self, samples):
        dist = self.dist
        if (isinstance(self.dist, numbers.Number)):
            dist = distribution.samplesToDistribution(samples, self.dist)
        return self.getValueByDistribution(dist)


class Metric(abc.ABC):
    @abc.abstractmethod
    def compute(self, eventA, eventB):
        """
        Computes a score between two sample sets to determine if both sample sets are correlated. Additionally a p-value
        is computed to score the returned value.

        To obtain the p-value, a hypothesis test is done. The null hypothesis H0 is that event types 'a' and 'b' are
        independent:
            H0 : P(a, b) = P(a) * P(b)

            H1 : P(a, b) != P(a) * P(b)
        A small p-value (significance level should be 0.05) indicates rejection of H0, meaning 'a' and 'b' are
        correlated.
        """
        pass


class PearsonCoefficient(Metric):
    """
    Computes the pearson correlation coefficient between two sample sets.

    [1] Pearson Correlation Coefficient; Benesty, J. et al.; Noise Reduction in Speech Processing; Springer Berlin
        Heidelberg; 2009
    """

    def compute(self, eventA, eventB):
        res = scipy.stats.pearsonr(eventA, eventB)

        # values are in [0, 1]. Use anti-proportional value to obtain metric
        return (1 - abs(res[0]), res[1])


class DistanceCorrelation(Metric):
    """
    This class computes the sample distance between two sample sets. The distance is calculated based on Brownian
    distance correlation [1].

    [1] Brownian distance covariance; Székely, G. and Rizzo, M.; The Annals of Applied Statistics; 3:4; 2009
    """

    def compute(self, eventA, eventB):
        """ Compute sample distance correlation """
        value = self.computeCov(eventA, eventB) / np.sqrt(self.computeVar(eventA) * self.computeVar(eventB))
        p = self._computePValue(eventA, eventB)

        # values are in [0, 1]. Use anti-proportional value to obtain metric
        return (1 - value, p)

    # noinspection PyMethodMayBeStatic
    def computeCov(self, eventA, eventB):
        if (eventA.size != eventB.size):
            raise ValueError("Input vectors do not have the same length")

        a = DistanceCorrelation._createPairwiseDist(eventA)
        b = DistanceCorrelation._createPairwiseDist(eventB)

        A = (a - a.mean(axis=1)).T - a.mean(axis=0) + a.mean()
        B = (b - b.mean(axis=1)).T - b.mean(axis=0) + b.mean()

        tmp = np.dot(A.flatten(), B.flatten())
        return math.sqrt(tmp / (eventA.size * eventB.size))

    def computeVar(self, event):
        return self.computeCov(event, event)

    @staticmethod
    def _createPairwiseDist(event):
        [A, B] = np.meshgrid(event, event)
        return np.abs(A - B)

    def _computePValue(self, eventA, eventB, n=999):
        """
        The hypothesis test is done by random permutation of eventB. This definitely breaks the possible dependency
        between A and B. Next, the distance correlation V* is computed. This procedure is repeated n times. The fraction
        of V* > V is used as a p-value.
        """

        ref = self.computeCov(eventA, eventB)
        p = 0.0
        for i in range(n):
            cov = self.computeCov(eventA, np.random.permutation(eventB))
            if (ref < cov):
                p += 1
        return p / n


class EnergyStatistic(Metric):
    """
    This class computes the energy statistic described in [1]. The energy statistic is a measure for the distance
    between two distributions represented by two vectors with random samples.
    As the energy statistic is not normalized, the normalized version should be used.

    [1] Energy distance; Rizzo, M. and Szekely, G.; Wiley Interdisciplinary Reviews: Computational Statistics, 8:1; 2016
    """

    def compute(self, eventA, eventB):
        value = self._computeUnNormalized(eventA, eventB) / (2 * self._computeSum(eventA, eventB))
        p = self._computePValue(eventA, eventB)

        return (value, p)

    def _computeUnNormalized(self, eventA, eventB):
        A = self._computeSum(eventA, eventB)
        B = self._computeSum(eventA, eventA)
        C = self._computeSum(eventB, eventB)
        return 2 * A - B - C

    # noinspection PyMethodMayBeStatic
    def _computeSum(self, eventA, eventB):
        [TA, TB] = np.meshgrid(eventA, eventB)
        delta = np.abs(TB - TA)
        return np.sum(delta) / (eventA.size * eventB.size)

    def _computePValue(self, eventA, eventB, n=999):
        p = 0
        ref = self._computeMultivariateTest(eventA, eventB)

        for i in range(n):
            tmp = np.random.permutation(np.concatenate((eventA, eventB)))
            permA = tmp[0:eventA.size]
            permB = tmp[eventA.size:eventA.size + eventB.size]

            v = self._computeMultivariateTest(permA, permB)
            if (ref > v):
                p += 1

        return float(p + 1) / float(n + 1)

    def _computeMultivariateTest(self, eventA, eventB):
        value = 0
        value += self._computeTestStatistic(eventA, eventA)
        value += self._computeTestStatistic(eventA, eventB)
        value += self._computeTestStatistic(eventB, eventA)
        value += self._computeTestStatistic(eventB, eventB)
        return value

    def _computeTestStatistic(self, eventA, eventB):
        return (eventA.size * eventB.size) / (eventA.size + eventB.size) * self._computeUnNormalized(eventA, eventB)
