import numpy as np
import math

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
            print(result)
        return (result[0][0], result[0][1])

    def calculate(self, a, b):
        r = np.ones([a.size, b.size]) / b.size
        mu = np.random.uniform(5, 7)
        sigma = np.random.uniform(5, 7)

        while True:
            self.logger.debug("Current parameters: Mu: {}\t Sigma:{}".format(mu, sigma))
            print(np.sum(r, axis=1))

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

        return (mu, sigma, np.random.uniform())

    @staticmethod
    def expectation(a, b, r, mu, sigma):
        tmp = np.zeros(r.shape)
        for i in range(0, a.size):
            for j in range(0, b.size):
                tmp[i][j] = r[i][j] * (1 / math.sqrt(2 * math.pi * sigma)) \
                            * math.exp(-(b[j] - a[i] - mu) ** 2 / (2 * sigma))

        c = tmp / tmp.sum(axis=1)[:, None]
        for i in range(0, a.size):
            for j in range(0, b.size):
                if (math.isnan(c[i][j])):
                    asdf = 0

        return c

    @staticmethod
    def maximization(a, b, r):
        A, B = np.meshgrid(a, b)
        delta = (B - A).T

        mu = (delta * r).sum() / b.size
        sigma = ((delta - mu) ** 2 * r).sum() / b.size

        return (mu, sigma)
