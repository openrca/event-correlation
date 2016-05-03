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

    def maximization(self, a, b, r):
        delta = self.getDelta(a, b)
        mu = np.sum(np.sum(r * delta, axis=1), axis=0) / len(b)

        delta = np.power(delta - mu, 2)
        sigma = np.sum(np.sum(r * delta, axis=1), axis=0) / len(b)
        return (mu, sigma)

    def expectation(self, a, b, r, mu, sigma):
        dist = self.getDist(a, b, mu, sigma)

        tmp = np.multiply(r, dist)
        denominator = np.sum(tmp, axis=0)
        return tmp / denominator

    def match(self, **kwargs):
        self.parseArgs(kwargs)
        self.logger.info("Matching event {} against {}".format(self.eventA, self.eventB))
        a = self.sequence.asVector(self.eventA)
        b = self.sequence.asVector(self.eventB)

        result = np.zeros([10, 2])
        for i in range(0, 10):
            self.logger.info("Processing batch {}".format(i))
            likelihood = np.zeros(20)
            tmp = np.zeros([20, 2])
            for j in range(0, 20):
                tmp[j][0], tmp[j][1], likelihood[j] = self.calculate(a, b)

            idx = np.argmax(likelihood)
            result[i][0] = tmp[idx][0]
            result[i][1] = tmp[idx][1]
        print(result)
        return (result[0][0], result[0][1])

    def calculate(self, a, b):
        r = np.ones([len(b), len(a)]) * 1 / len(a)
        mu = np.random.uniform()
        sigma = np.random.uniform()

        while True:
            self.logger.debug("Current parameters: Mu: {}\t Sigma:{}".format(mu, sigma))
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

        dist = self.getDist(a, b, mu, sigma)
        likelihood = np.sum(np.reshape(r, [1, r.size]) * np.reshape(dist, [1, dist.size]))
        return (mu, sigma, likelihood)

    @staticmethod
    def getDelta(a, b):
        A, B = np.meshgrid(a, b)
        return B - A

    def getDist(self, a, b, mu, sigma):
        delta = self.getDelta(a, b)
        scalar = np.math.log(1 / np.math.sqrt(2 * np.math.pi * sigma))

        dist = -1 * np.power(delta - mu, 2) / (2 * sigma) + scalar
        return np.power(np.math.e, dist)
