""" Collection of distributions

This module contains a collection of distributions for creation of random sequences.
"""

import abc
import datetime
import json
import math
import time

import numpy as np

STATIC = 1
NORMAL = 2
UNIFORM = 3
POWER = 4
EXP = 5

distributions = {
    STATIC: 'Static',
    NORMAL: 'Normal',
    UNIFORM: 'Uniform',
    POWER: 'Power',
    EXP: 'Exp',
}


class Distribution:
    """ Base class for all distributions """

    def __init__(self):
        d = datetime.datetime.now()
        self.seed(int(time.mktime(d.timetuple())))

    @staticmethod
    def seed(seed):
        np.random.seed(seed)

    @abc.abstractmethod
    def getPDFValue(self):
        """ Fetch the next random value """
        return

    @abc.abstractmethod
    def getCDFValue(self, x):
        """ Calculate CDF with offset x """
        return


class StaticDistribution(Distribution):
    """ Mock distribution used for testing

    This distribution will allways return the values provided by the setters
    """

    def __init__(self, pdf=[0.5], cdf=[0.5]):
        self.pdfIdx = 0
        self.cdfIdx = 0
        self.pdf = pdf
        self.cdf = cdf

    def getPDFValue(self):
        t = self.__get(self.pdfIdx, self.pdf)
        self.pdfIdx = t[0]
        return t[1]

    def getCDFValue(self, x):
        t = self.__get(self.cdfIdx, self.cdf)
        self.cdfIdx = t[0]
        return t[1]

    def __get(self, idx, lst):
        if (idx >= len(lst)):
            idx = 0;
        return (idx + 1, lst[idx])


class NormalDistribution(Distribution):
    """ Creates random samples based on a normal distribution """

    def __init__(self, mu=1, sigma=1):
        super().__init__()
        self.mu = mu
        self.sigma = sigma
        self.__checkParam()

    def __checkParam(self):
        if (self.sigma <= 0):
            raise ValueError("Variance is not positive. Sigma: {}".format(self.sigma))

    def getPDFValue(self):
        return np.random.normal(self.mu, self.sigma)

    def getCDFValue(self, x):
        raise NotImplementedError("Not implemented yet")


class UniformDistribution(Distribution):
    """ Creates random samples based on a uniform distribution """

    def __init__(self, lower=0, upper=1):
        super().__init__()
        self.lower = lower
        self.upper = upper
        self.__checkParam()

    def __checkParam(self):
        if (self.lower >= self.upper):
            raise ValueError("Lower border is greater or equal to upper border. Lower: {}, Upper: {}"
                             .format(self.lower, self.upper))

    def getPDFValue(self):
        return np.random.uniform(self.lower, self.upper)

    def getCDFValue(self, x):
        raise NotImplementedError("Not implemented yet")


class PowerLawDistribution(Distribution):
    """ Creates random samples based on a Power Law distribution

    Distribution:
        P(x; a) = ax^(a - 1), 0 <= x <= 1, a > 0
    """

    def __init__(self, exponent):
        super().__init__()
        self.exponent = exponent
        self.__checkParam()

    def __checkParam(self):
        if (self.exponent <= 0):
            raise ValueError("Exponent is not positive. Exponent: {}".format(self.exponent))

    def getPDFValue(self):
        return np.random.power(self.exponent)

    def getCDFValue(self, x):
        raise NotImplementedError("Not implemented yet")


class ExponentialDistribution(Distribution):
    """ Creates random samples based on an Exponential distribution

    Distribution
        P(x) = le^(-lx), x >= 0, l > 0
    """

    def __init__(self, lam=1):
        super().__init__()
        self.lam = lam
        self.__checkParam()

    def __checkParam(self):
        if (self.lam <= 0):
            raise ValueError("Exponent is not positive. Exponent: {}".format(self.lam))

    def getPDFValue(self):
        return np.random.exponential(self.lam)

    def getCDFValue(self, x):
        if (x < 0):
            return 0
        return 1 - math.exp(-self.lam * x)


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
    except KeyError as ex:
        raise ValueError("Missing attributes 'name' and/or 'param' in '{}'".format(str(value)))

    try:
        if (dist == distributions[NORMAL]):
            return NormalDistribution(float(param[0]), float(param[1]))
        elif (dist == distributions[UNIFORM]):
            return UniformDistribution(float(param[0]), float(param[1]))
        elif (dist == distributions[POWER]):
            return PowerLawDistribution(float(param[0]))
        elif (dist == distributions[EXP]):
            return ExponentialDistribution(float(param[0]))
        else:
            raise ValueError("Unknown distribution '{}'".format(dist))
    except (IndexError, ValueError) as ex:
        raise ValueError("Unknown parameters '{}' for distribution '{}'".format(param, dist))
