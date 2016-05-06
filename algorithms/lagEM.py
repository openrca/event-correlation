import math

import numpy as np

from algorithms import Matcher


class lagEM(Matcher):
    def __init__(self):
        super().__init__(__name__)
        self.sequence = None
        self.eventA = None
        self.eventB = None
        self.threshold = None

    def parseArgs(self, kwargs):
        self.sequence = kwargs["sequence"]
        self.eventA = kwargs["eventA"]
        self.eventB = kwargs["eventB"]
        self.threshold = kwargs["threshold"]

    def match(self, **kwargs):
        self.parseArgs(kwargs)
        self.logger.info("Matching event {} against {}".format(self.eventA, self.eventB))
        a = self.sequence.asVector(self.eventA)
        b = self.sequence.asVector(self.eventB)

        result = np.zeros([10, 2])
        for i in range(0, 10):
            self.logger.info("Processing batch {}".format(i))
            tmp = np.zeros([20, 3])
            for j in range(0, 20):
                tmp[j] = self.calculate(a, b)

            result[i] = tmp[np.argmax(tmp[:, 2]), [0, 1]]
            self.logger.debug("Current result:\n {}".format(result))
        return result.sum(axis=0) / result.shape[0]

    def calculate(self, a, b):
        r = np.ones([a.size, b.size]) / b.size
        mu = np.random.uniform(5, 7)
        sigma = np.random.uniform(5, 7)

        while True:
            self.logger.trace("Current parameters: Mu: {}\t Sigma:{}".format(mu, sigma))

            r = self.expectation(a, b, r, mu, sigma)
            newMu, newSigma = self.maximization(a, b, r)

            deltaMu = abs(mu - newMu)
            deltaSigma = abs(sigma - newSigma)

            mu = newMu
            sigma = newSigma

            if (math.isnan(mu) or math.isnan(sigma)):
                self.logger.warn("Mu or sigma is NaN")
                break

            if (deltaMu < self.threshold and deltaSigma < self.threshold):
                break

        likelihood = 1
        tmp = self.calculateNormalMatrix(a, b, r, mu, sigma).sum(axis=0)
        for j in range(b.size):
            likelihood *= tmp[j]
        return (mu, sigma, likelihood)

    @staticmethod
    def expectation(a, b, r, mu, sigma):
        tmp = lagEM.calculateNormalMatrix(a, b, r, mu, sigma)
        return tmp / tmp.sum(axis=1)[:, None]

    @staticmethod
    def maximization(a, b, r):
        A, B = np.meshgrid(a, b)
        delta = (B - A).T

        mu = (delta * r).sum() / b.size
        sigma = ((delta - mu) ** 2 * r).sum() / b.size

        return (mu, sigma)

    @staticmethod
    def calculateNormalMatrix(a, b, r, mu, sigma):
        tmp = np.zeros(r.shape)
        scalar = 1 / math.sqrt(2 * math.pi * sigma)
        for i in range(0, a.size):
            for j in range(0, b.size):
                tmp[i][j] = r[i][j] * scalar * math.exp(-(b[j] - a[i] - mu) ** 2 / (2 * sigma))
        return tmp
