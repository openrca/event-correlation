import math
import threading

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

        result = np.zeros([10, 3])
        threads = []
        for i in range(10):
            thread = threading.Thread(target=self.calculateParallel, args=(a, b, result, i,))
            thread.start()
            threads.append(thread)

        for i in range(10):
            threads[i].join()
        threads.clear()
        self.logger.info("Results:\n {}".format(result))
        tmp = result.sum(axis=0) / np.count_nonzero(result[:, 0])
        return {"Mu": tmp[0], "Sigma": tmp[1], "Likelihood": result[:, 2].max()}

    def calculateParallel(self, a, b, result, index):
        self.logger.info("Processing batch {}".format(index))
        tmp = np.zeros([20, 3])
        for j in range(20):
            self.logger.debug("Worker[{}]: Processing round {}".format(index, j))
            tmp[j] = self.calculate(a, b)
        result[index] = tmp[np.argmax(tmp[:, 2])]

    def calculate(self, a, b):
        r = np.ones([a.size, b.size]) / b.size
        mu = np.random.uniform(76, 78)
        variance = np.random.uniform(3, 25) ** 2

        while True:
            self.logger.trace("Current parameters: Mu: {}\t Sigma:{}".format(mu, math.sqrt(variance)))

            r = self.expectation(a, b, r, mu, variance)
            newMu, newVariance = self.maximization(a, b, r)

            deltaMu = abs(mu - newMu)
            deltaVariance = abs(variance - newVariance)

            mu = newMu
            variance = newVariance

            if (math.isnan(mu) or math.isnan(variance)):
                self.logger.warn("Mu or Variance is NaN")
                break

            if (deltaMu < self.threshold and deltaVariance < self.threshold):
                break

        likelihood = 1
        tmp = self.calculateNormalMatrix(a, b, r, mu, variance).sum(axis=0)
        for j in range(b.size):
            likelihood *= tmp[j]

        if (math.isnan(mu) or math.isnan(math.sqrt(variance)) or math.isnan(likelihood)):
            return (0, 0, 0)
        return (mu, math.sqrt(variance), likelihood)

    @staticmethod
    def expectation(a, b, r, mu, variance):
        tmp = lagEM.calculateNormalMatrix(a, b, r, mu, variance)
        return tmp / tmp.sum(axis=1)[:, None]

    @staticmethod
    def maximization(a, b, r):
        A, B = np.meshgrid(a, b)
        delta = (B - A).T

        mu = (delta * r).sum() / b.size
        variance = ((delta - mu) ** 2 * r).sum() / b.size

        return (mu, variance)

    @staticmethod
    def calculateNormalMatrix(a, b, r, mu, variance):
        tmp = np.zeros(r.shape)
        scalar = 1 / math.sqrt(2 * math.pi * variance)
        for i in range(a.size):
            for j in range(b.size):
                tmp[i][j] = r[i][j] * scalar * math.exp(-(b[j] - a[i] - mu) ** 2 / (2 * variance))
        return tmp
