""" Collection of distributions

This module contains a collection of distributions for creation of random sequences.
"""

import abc
import datetime
import json
import time

import numpy as np
from scipy import stats

STATIC = 1
NORMAL = 2
UNIFORM = 3
POWER = 4
EXP = 5

distributions = {
    STATIC: 'Static',
    NORMAL: 'Norm',
    UNIFORM: 'Uniform',
    POWER: 'Powerlaw',
    EXP: 'Expon',
}


class Distribution:
    """ Base class for all distributions """

    def __init__(self, distType, param):
        self.distType = distType
        self.param = param
        self.dist = None

        d = datetime.datetime.now()
        self.seed(int(time.mktime(d.timetuple())))

    def asJson(self):
        return {"name": distributions[self.distType], "param": self.param}

    def getMaximumPDF(self):
        """ Calculate the maximum PDF for normalization """
        return self.dist.pdf(self.dist.mean())

    def __eq__(self, other):
        if (not isinstance(other, Distribution)):
            return False
        return self.param == other.param

    def __hash__(self):
        return hash(self.param)

    @staticmethod
    def seed(seed):
        np.random.seed(seed)

    @abc.abstractmethod
    def getRandom(self, n=None):
        """ Return random value """
        return

    @abc.abstractmethod
    def getPDFValue(self, x):
        """ Calculate PDF for value x """
        return

    @abc.abstractmethod
    def getCDFValue(self, x):
        """ Calculate CDF with offset x """
        return


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
        super().__init__(distType=STATIC, param=(pdf, cdf, rvs))
        self.pdfIdx = 0
        self.cdfIdx = 0
        self.rvsIdx = 0
        self.pdf = pdf
        self.cdf = cdf
        self.rvs = rvs

    def getRandom(self, n=None):
        if (n is None):
            n = 1
        result = []
        for i in range(n):
            self.rvsIdx, value = self._get(self.rvsIdx, self.rvs)
            result.append(value)

        if (n == 1):
            return result[0]
        return result

    def getPDFValue(self, x):
        self.pdfIdx, value = self._get(self.pdfIdx, self.pdf)
        return value

    def getCDFValue(self, x):
        self.cdfIdx, value = self._get(self.cdfIdx, self.cdf)
        return value

    @staticmethod
    def _get(idx, lst):
        if (idx >= len(lst)):
            idx = 0
        return (idx + 1, lst[idx])

    def __str__(self):
        return "{}: pdf: {}\t cdf: {}\t rvs: {}".format(distributions[STATIC], self.pdf, self.cdf, self.rvs)


class NormalDistribution(Distribution):
    """ Creates random samples based on a normal distribution """

    def __init__(self, mu=0.0, sigma=1.0):
        """
        :param mu: Expectation value
        :param sigma: Standard deviation
        """
        super().__init__(distType=NORMAL, param=(mu, sigma))
        self.mu = mu
        self.sigma = sigma
        self._checkParam()
        self.dist = stats.norm(mu, sigma)

    def _checkParam(self):
        if (self.sigma <= 0):
            raise ValueError("Variance is not positive. Sigma: {}".format(self.sigma))

    def getRandom(self, n=None):
        return self.dist.rvs(n)

    def getPDFValue(self, x):
        return self.dist.pdf(x)

    def getCDFValue(self, x):
        return self.dist.cdf(x)

    def __str__(self):
        return "{}: Mu: {}\t Sigma: {}".format(distributions[NORMAL], self.mu, self.sigma)


class UniformDistribution(Distribution):
    """ Creates random samples based on a uniform distribution """

    def __init__(self, lower=0.0, upper=1.0):
        """
        :param lower: Lower bound
        :param upper: Upper bound
        """
        super().__init__(distType=UNIFORM, param=(lower, upper))
        self.lower = lower
        self.upper = upper
        self._checkParam()
        # scipy expects size of interval as second parameter
        self.dist = stats.uniform(lower, upper - lower)

    def _checkParam(self):
        if (self.lower >= self.upper):
            raise ValueError("Lower border is greater or equal to upper border. Lower: {}, Upper: {}"
                             .format(self.lower, self.upper))

    def getRandom(self, n=None):
        return self.dist.rvs(n)

    def getPDFValue(self, x):
        return self.dist.pdf(x)

    def getCDFValue(self, x):
        return self.dist.cdf(x)

    def __str__(self):
        return "{}: Lower: {}\t Upper: {}".format(distributions[UNIFORM], self.lower, self.upper)


class PowerLawDistribution(Distribution):
    #  TODO check how Powerlaw exactly is implemented
    """ Creates random samples based on a Power Law distribution

    Distribution:
        P(x; a, b) = ax^(a - 1) + b, 0 <= x <= 1, a > 0
    """

    def __init__(self, a, b=0.0):
        """
        :param a: Shape of function
        :param b: Offset for values
        """
        super().__init__(distType=POWER, param=(a, b))
        self.a = a
        self.b = b
        self._checkParam()
        self.dist = stats.powerlaw(a, b)

    def _checkParam(self):
        if (self.a <= 0):
            raise ValueError("A is not positive. A: {}".format(self.a))

    def getRandom(self, n=None):
        return self.dist.rvs(n)

    def getPDFValue(self, x):
        return self.dist.pdf(x)

    def getCDFValue(self, x):
        return self.dist.cdf(x)

    def __str__(self):
        return "{}: Exponent: {}".format(distributions[POWER], self.a)


class ExponentialDistribution(Distribution):
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
        self.lam = beta
        self.offset = offset
        self._checkParam()
        self.dist = stats.expon(offset, beta)

    def _checkParam(self):
        if (self.lam <= 0):
            raise ValueError("Exponent is not positive. Exponent: {}".format(self.lam))

    def getRandom(self, n=None):
        return self.dist.rvs(n)

    def getPDFValue(self, x):
        return self.dist.pdf(x)

    def getCDFValue(self, x):
        return self.dist.cdf(x)

    def __str__(self):
        return "{}: Offset: {}\t Lambda: {}".format(distributions[EXP], self.offset, self.lam)


def load(value):
    """ Load a distribution from a json string
        Parameter:
            name, param
        Throws:
            ValueError
        """

    if (isinstance(value, str)):
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
        elif (dist == distributions[POWER]):
            return PowerLawDistribution(float(param[0]), float(param[1]))
        elif (dist == distributions[EXP]):
            return ExponentialDistribution(float(param[0]), float(param[1]))
        else:
            raise ValueError("Unknown distribution '{}'".format(dist))
    except (IndexError, ValueError):
        raise ValueError("Unknown parameters '{}' for distribution '{}'".format(param, dist))


def kstest(dist1, dist2, n=20):
    if (not isinstance(dist1, Distribution)):
        raise TypeError("dist1 is not an instance of core.distribution.Distribution")
    if (not isinstance(dist2, Distribution)):
        raise TypeError("dist2 is not an instance of core.distribution.Distribution")

    return stats.kstest(dist1.dist.rvs(n), dist2.dist.cdf).statistic


def approximateIntervalBorders(dist, alpha, lower=-10):
    prevArea = dist.getCDFValue(lower)
    i = lower
    while True:
        area = dist.getCDFValue(i)
        if area - prevArea >= alpha or area == 1:
            return (lower, i)
        i += 0.01


def chi2test(dist1, dist2, n=2000):
    nrBins = int(n / 5)
    if (n >= 35):
        nrBins = int(1.88 * n ** 0.4)

    a = np.sort(dist1.getRandom(n))
    bins = np.zeros(nrBins)

    lower = -10
    percent = 1 / nrBins
    for i in range(nrBins):
        lower, bins[i] = approximateIntervalBorders(dist2, percent, lower)

    counts = np.bincount(np.digitize(a, bins))
    return stats.chisquare(counts).statistic


def getEmpiricalDist(a, b):
    d = b - a
    return NormalDistribution(d.mean(), np.sqrt(d.var()))
