""" Collection of distributions

This module contains a collection of distributions for creation of random sequences.
"""

import abc
import collections
import datetime
import json
import math
import numbers
import sys
import time

import numpy as np
from scipy import stats, integrate

STATIC = 1
NORMAL = 2
UNIFORM = 3
EXP = 5
KDE = 6

distributions = {
    STATIC: 'Static',
    NORMAL: 'Norm',
    UNIFORM: 'Uniform',
    EXP: 'Expon',
    KDE: 'Kde'
}


class Distribution(abc.ABC):
    """ Base class for all distributions """

    def __init__(self, distType, param):
        self.distType = distType
        self.param = param
        self.dist = None

        d = datetime.datetime.now()
        np.random.seed(int(time.mktime(d.timetuple())))

    def asJson(self):
        return {"name": distributions[self.distType], "param": self.param}

    def getMaximumPDF(self):
        """ Compute the maximum PDF for normalization """
        return self.dist.pdf(self.dist.mean())

    def getCompleteInterval(self):
        return self.dist.interval(0.99)

    def getRelativePdf(self, x):
        """ Compute the ratio between x and the maximal pdf value """
        return min(1, self.getPDFValue(x) / self.getMaximumPDF())

    def __eq__(self, other):
        if (not isinstance(other, Distribution)):
            return False
        return self.param == other.param

    def __hash__(self):
        return hash(self.param)

    def __neg__(self):
        return self

    @abc.abstractmethod
    def getRandom(self, n=None):
        """ Return random value """
        pass

    @abc.abstractmethod
    def getPDFValue(self, x):
        """ Compute PDF for value x """
        pass

    @abc.abstractmethod
    def getCDFValue(self, x):
        """ Compute CDF with offset x """
        pass

    @abc.abstractmethod
    def getDifferentialEntropy(self):
        pass

    @abc.abstractmethod
    def getVar(self):
        pass

    @abc.abstractmethod
    def getStd(self):
        pass


class AbstractDistribution(Distribution, abc.ABC):
    @abc.abstractmethod
    def getDifferentialEntropy(self):
        pass

    def getCDFValue(self, x):
        return self.dist.cdf(x)

    def getRandom(self, n=None):
        return self.dist.rvs(n)

    def getPDFValue(self, x):
        return self.dist.pdf(x)

    def getVar(self):
        return self.dist.var()

    def getStd(self):
        return self.dist.std()


class StaticDistribution(Distribution):
    """ Mock distribution used for testing

    This distribution will always return the values provided by the setters
    """

    def __init__(self, pdf=None, cdf=None, rvs=None):
        """
        :param pdf: Values to be returned by 'getPDFValue()'
        :param cdf: Values to be returned by 'getPDFValue()'
        :param rvs: Values to be returned by 'getPDFValue()'
        """
        if (pdf is None):
            pdf = [0.5]
        if (cdf is None):
            cdf = [0.5]
        if (rvs is None):
            rvs = [0.5]
        super().__init__(distType=STATIC, param=())
        self.pdfIdx = 0
        self.cdfIdx = 0
        self.rvsIdx = 0
        self.pdf = np.array(pdf)
        self.cdf = np.array(cdf)
        self.rvs = np.array(rvs)

    def getRandom(self, n=None):
        if (n is None):
            n = 1
        result = []
        for i in range(n):
            self.rvsIdx, value = self.__get(self.rvsIdx, self.rvs)
            result.append(value)

        if (n == 1):
            return result[0]
        return result

    def getPDFValue(self, x):
        self.pdfIdx, value = self.__get(self.pdfIdx, self.pdf)
        return value

    def getCDFValue(self, x):
        self.cdfIdx, value = self.__get(self.cdfIdx, self.cdf)
        return value

    # noinspection PyArgumentList
    def getDifferentialEntropy(self):
        """ Static distribution has no continuous entropy. Compute normal entropy instead. """
        count = np.array(list(collections.Counter(self.pdf).values()))
        return stats.entropy(np.divide(count, count.sum()))

    def getStd(self):
        return self.pdf.std()

    def getVar(self):
        return self.pdf.var()

    @staticmethod
    def __get(idx, lst):
        if (idx >= len(lst)):
            idx = 0
        return (idx + 1, lst[idx])

    def __str__(self):
        return "{}: pdf: {} cdf: {} rvs: {}".format(distributions[STATIC], self.pdf, self.cdf, self.rvs)


class NormalDistribution(AbstractDistribution):
    """ Creates random samples based on a normal distribution """

    def __init__(self, mu=0.0, sigma=1.0):
        """
        :param mu: Expectation value
        :param sigma: Standard deviation
        """
        super().__init__(distType=NORMAL, param=(mu, sigma))
        self.mu = mu
        self.sigma = sigma
        self.__checkParam()
        self.dist = stats.norm(mu, sigma)

    def getDifferentialEntropy(self):
        return math.log(self.sigma * math.sqrt(2 * math.pi * math.e))

    def __checkParam(self):
        if (self.sigma == 0):
            self.sigma = 0.0000001

        if (self.sigma < 0):
            raise ValueError("Variance is not positive. Sigma: {}".format(self.sigma))

    def __str__(self):
        return "{}: Mu: {} Sigma: {}".format(distributions[NORMAL], self.mu, self.sigma)

    def __neg__(self):
        return NormalDistribution(-self.mu, self.sigma)


class UniformDistribution(AbstractDistribution):
    """ Creates random samples based on a uniform distribution """

    def __init__(self, lower=0.0, upper=1.0):
        """
        :param lower: Lower bound
        :param upper: Upper bound
        """
        super().__init__(distType=UNIFORM, param=(lower, upper))
        self.lower = lower
        self.upper = upper
        self.__checkParam()
        # scipy expects size of interval as second parameter
        self.dist = stats.uniform(lower, upper - lower)

    def __checkParam(self):
        if (self.lower >= self.upper):
            raise ValueError("Lower border is greater or equal to upper border. Lower: {}, Upper: {}"
                             .format(self.lower, self.upper))

    def getDifferentialEntropy(self):
        return math.log(self.upper - self.lower)

    def __str__(self):
        return "{}: Lower: {} Upper: {}".format(distributions[UNIFORM], self.lower, self.upper)

    def __neg__(self):
        return UniformDistribution(-self.upper, -self.lower)


class ExponentialDistribution(AbstractDistribution):
    """ Creates random samples based on an Exponential distribution

    Distribution
        P(x) = le^(-lx), x >= 0, l > 0
    """

    def __init__(self, offset=0.0, beta=1.0):
        """
        :param offset: Offset of start
        :param beta: Scaling of slope 1 / lambda
        """
        super().__init__(distType=EXP, param=(offset, beta))
        self.beta = beta
        self.offset = offset
        self.__checkParam()
        self.dist = stats.expon(offset, beta)

    def __checkParam(self):
        if (self.beta <= 0):
            raise ValueError("Exponent is not positive. Exponent: {}".format(self.beta))

    def getDifferentialEntropy(self):
        return 1 - math.log(1 / self.beta)

    def __str__(self):
        return "{}: Offset: {} Beta: {}".format(distributions[EXP], self.offset, self.beta)

    def __neg__(self):
        return ExponentialDistribution(-self.offset, self.beta)


class KdeDistribution(Distribution):
    """ Creates random samples based on a Kernel density estimation.

    Kernel density estimation is a method for parameter-less distributions. The distributions is created from a set of
    samples.
    """

    def __init__(self, samples):
        """
        :param samples: 1D-Samples to create distribution from
        """
        super().__init__(distType=KDE, param=([samples]))
        self.samples = np.array(sorted(samples))
        if (len(samples) == 0):
            raise ValueError("Unable to perform Kernel density estimation without samples.")

        self.minValue = np.min(self.samples) - 2
        self.maxValue = np.max(self.samples) + 2
        if (np.min(self.samples) != np.max(self.samples)):
            self.kernel = stats.gaussian_kde(self.samples, 0.1)
        else:
            self.kernel = SingularKernel(np.min(self.samples))
        self.cachedMaxPdf = None

    def getPDFValue(self, x):
        pdf = self.kernel.evaluate(x)
        if (self.cachedMaxPdf is not None and len(pdf) == 1 and pdf > self.cachedMaxPdf):
            self.cachedMaxPdf = pdf
        return pdf

    def getRandom(self, n=None):
        if (n is None):
            n = 1
        return self.kernel.resample(n)[0]

    def getCDFValue(self, x):
        if (isinstance(x, numbers.Number)):
            upper = min(x, self.maxValue)
            if (upper <= self.minValue):
                return 0
            return self.kernel.integrate_box_1d(self.minValue, upper)

        res = np.zeros(len(x))
        for i in range(len(x)):
            upper = min(x[i], self.maxValue)
            if (upper > self.minValue):
                res[i] = self.kernel.integrate_box_1d(self.minValue, upper)
        return res

    def getCompleteInterval(self):
        return (self.minValue, self.maxValue)

    def getDifferentialEntropy(self):
        """
        It is not possible to integrate this function analytically. Therefore the continuous function is approximated by
        sampling and discrete entropy. To compare differential entropy with "normal" entropy you have to add the
        logarithm of the step size to the result [1], [2].

        [1] http://thirdorderscientist.org/homoclinic-orbit/2013/5/8/bridging-discrete-and-differential-entropy
        [2] Elements of information theory, Cover, Thomas, page 247-248
        """
        x = np.linspace(self.minValue, self.maxValue, 10000)
        pdf = self.getPDFValue(x)
        return stats.entropy(pdf) + math.log2((self.maxValue - self.minValue) / 10000)

    def getMaximumPDF(self):
        if (self.cachedMaxPdf is None):
            x = np.linspace(self.minValue, self.maxValue, 10000)
            self.cachedMaxPdf = self.getPDFValue(x).max()
        return self.cachedMaxPdf

    def getStd(self):
        return self.samples.std()

    def getVar(self):
        return self.samples.var()

    def __str__(self):
        return "{}: Samples: {}".format(distributions[KDE], self.samples)

    def __repr__(self):
        return str(self.samples)

    def __neg__(self):
        return KdeDistribution(-self.samples)


class SingularKernel():
    def __init__(self, value, threshold=0.005):
        self.value = value
        self.maxValue = sys.maxsize
        # threshold is a workaround to increase the probability that distribution is visible in plot
        self.threshold = threshold

    def evaluate(self, x):
        if (isinstance(x, (list, np.ndarray))):
            result = np.zeros(len(x))
            for i in range(len(x)):
                if (abs(x[i] - self.value) < self.threshold):
                    result[i] = self.maxValue
            return result
        else:
            return np.array([self.maxValue if (abs(x - self.value) < self.threshold) else 0])

    def resample(self, n):
        return [np.array([self.value] * n)]

    def integrate_box_1d(self, lower, upper):
        if (lower <= self.value <= upper):
            return 1
        return 0


def load(value):
    """ Load a distribution from a json string
        Parameter:
            name, param
        Throws:
            ValueError
        """

    if (isinstance(value, str)):
        if (value == ""):
            return None
        value = json.loads(value)

    try:
        dist = value["name"]
        param = value["param"]
    except KeyError:
        raise ValueError("Missing attributes 'name' and/or 'param' in '{}'".format(str(value)))

    try:
        if (dist == distributions[NORMAL]):
            return NormalDistribution(float(param[0]), float(param[1]))
        elif (dist == distributions[UNIFORM]):
            return UniformDistribution(float(param[0]), float(param[1]))
        elif (dist == distributions[EXP]):
            return ExponentialDistribution(float(param[0]), float(param[1]))
        elif (dist == distributions[KDE]):
            return KdeDistribution(param[0])
        else:
            raise ValueError("Unknown distribution '{}'".format(dist))
    except (IndexError, ValueError):
        raise ValueError("Unknown parameters '{}' for distribution '{}'".format(param, dist))


def samplesToDistribution(samples, distribution):
    samples = np.array(samples)
    if (len(samples) == 0):
        raise ValueError("No samples provided")

    if (distribution == NORMAL):
        return NormalDistribution(samples.mean(), samples.std())
    elif (distribution == UniformDistribution):
        return UniformDistribution(samples.min(), samples.max())
    elif (distribution == EXP):
        return ExponentialDistribution(samples.min(), samples.mean() - samples.min())
    elif (distribution == KDE):
        return KdeDistribution(samples)
    else:
        raise ValueError("Unknown distribution '{}'".format(distribution))


def approximateIntervalBorders(dist, alpha, lower=-10):
    prevArea = dist.getCDFValue(lower)
    i = lower
    while True:
        area = dist.getCDFValue(i)
        if area - prevArea >= alpha or area == 1:
            return (lower, i)
        i += 0.01


def getEmpiricalDist(seq, trigger, response):
    events = seq.getEvents(trigger)

    values = []
    for event in events:
        if (event.triggered is not None and event.triggered.eventType == response):
            values.append(event.triggered.timestamp - event.timestamp)
    if (len(values) == 0):
        return None

    values = np.array(values)
    return NormalDistribution(values.mean(), values.std())


def getAreaBetweenDistributions(dist1, dist2):
    if (dist1 is None or dist2 is None):
        return 0

    borders1 = dist1.getCompleteInterval()
    borders2 = dist2.getCompleteInterval()
    x = np.linspace(min(borders1[0], borders2[0]), max(borders1[1], borders2[1]), 2000)
    y = np.amin(np.array([dist1.getPDFValue(x), dist2.getPDFValue(x)]), axis=0)
    return integrate.simps(y, x)


def getRelativeEntropy(dist1, dist2):
    borders1 = dist1.getCompleteInterval()
    borders2 = dist2.getCompleteInterval()
    x = np.linspace(min(borders1[0], borders2[0]), max(borders1[1], borders2[1]), 10000)
    return stats.entropy(dist1.getPDFValue(x), dist2.getPDFValue(x))
