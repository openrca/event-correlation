import abc
import numbers

import numpy as np

from core import distribution
from core.distribution import KDE


class Performance(abc.ABC):
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
    from the samples and averages the probability of all samples.
    """

    def __init__(self, dist=KDE, samples=None):
        super().__init__()
        self.dist = dist
        self.samples = samples

    def getValueByDistribution(self, dist):
        if (self.samples is None):
            return 0
        return dist.getPDFValue(self.samples).mean()

    def getValueBySamples(self, samples):
        dist = self.dist
        if (isinstance(self.dist, numbers.Number)):
            dist = distribution.samplesToDistribution(samples, self.dist)
        return dist.getPDFValue(samples).mean()


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

    def getValueByDistribution(self, dist):
        return dist.getDifferentialEntropy()

    def getValueBySamples(self, samples):
        dist = self.dist
        if (isinstance(self.dist, numbers.Number)):
            dist = distribution.samplesToDistribution(samples, self.dist)
        return dist.getDifferentialEntropy()
