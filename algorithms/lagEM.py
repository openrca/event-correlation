import fastLagEM
import threading

import numpy as np

from algorithms import Matcher, RESULT_MU, RESULT_SIGMA, RESULT_IDX, RESULT_KDE
from core.distribution import UniformDistribution, KdeDistribution


class lagEM(Matcher):
    def __init__(self):
        super().__init__(__name__)
        self.threshold = None

    def _parseArgs(self, kwargs):
        """
        Additional parameters:
            threshold: Defines a threshold for parameter convergence
        """
        self.threshold = kwargs["threshold"]

    def _compute(self):
        self.logger.info("Matching event {} against {}".format(self.trigger, self.response))
        trigger = self.sequence.asVector(self.trigger)
        response = self.sequence.asVector(self.response)

        assignments = [[]] * 10
        result = np.zeros([10, 3])
        threads = []
        for i in range(10):
            thread = threading.Thread(target=self.__computeParallel, args=(trigger, response, result, assignments, i,))
            thread.start()
            threads.append(thread)

        for i in range(10):
            threads[i].join()
        threads.clear()
        self.logger.info("Results:\n {}".format(result))

        mu, std, likelihood = result.sum(axis=0) / np.count_nonzero(result[:, 0])
        idx = np.array(assignments[np.argmax(result[:, 2])])

        [TTrigger, TResponse] = np.meshgrid(trigger, response)
        delta = TResponse - TTrigger
        samples = delta[idx[:, 1], idx[:, 0]]

        return {RESULT_MU: mu, RESULT_SIGMA: std, "Likelihood": result[:, 2].max(), RESULT_IDX: idx,
                RESULT_KDE: KdeDistribution(samples)}

    def __computeParallel(self, a, b, result, assignments, index):
        self.logger.info("Processing batch {}".format(index))
        tmp = np.zeros([20, 3])
        tmp2 = []
        for j in range(20):
            self.logger.debug("Worker[{}]: Processing round {}".format(index, j))
            mu = UniformDistribution(0, 100).getRandom()
            var = UniformDistribution(3, 25).getRandom() ** 2
            mu, std, likelihood, r = fastLagEM.compute(a, b, mu, var, len(a), len(b))
            tmp[j] = np.array([mu, std, likelihood])
            tmp2.append(r)

        idx = np.argmax(tmp[:, 2])
        result[index] = tmp[idx]
        assignments[index] = tmp2[idx]
