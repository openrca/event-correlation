import fastLagEM
import multiprocessing

import numpy as np

from algorithms import Matcher, RESULT_MU, RESULT_SIGMA, RESULT_IDX, RESULT_KDE
from core.distribution import UniformDistribution, KdeDistribution


class lagEM(Matcher):
    def __init__(self):
        super().__init__(__name__)
        self.__threshold = None

    def _parseArgs(self, kwargs):
        """
        Additional parameters:
            threshold: Defines a threshold for parameter convergence
        """
        self.__threshold = kwargs["threshold"]

    def _compute(self, trigger, response):
        processes = []
        queue = multiprocessing.Queue()

        for i in range(10):
            process = multiprocessing.Process(target=self.__computeParallel, args=(trigger, response, queue, i,))
            process.start()
            processes.append(process)

        result = np.zeros([10, 3])
        assignments = [[]] * 10
        for i in range(10):
            processes[i].join()
            res = queue.get()
            result[i] = res[0]
            assignments[i] = res[1]
        processes.clear()
        self._logger.info("Results:\n {}".format(result))

        mu, std, likelihood = result.sum(axis=0) / np.count_nonzero(result[:, 0])
        idx = np.array(assignments[np.argmax(result[:, 2])])

        [TTrigger, TResponse] = np.meshgrid(trigger, response)
        delta = TResponse - TTrigger
        samples = delta[idx[:, 1], idx[:, 0]]

        return {RESULT_MU: mu, RESULT_SIGMA: std, "Likelihood": result[:, 2].max(), RESULT_IDX: idx,
                RESULT_KDE: KdeDistribution(samples)}

    def __computeParallel(self, a, b, queue, index):
        self._logger.info("Processing batch {}".format(index))
        tmp = np.zeros([20, 3])
        tmp2 = []
        for j in range(20):
            self._logger.debug("Worker[{}]: Processing round {}".format(index, j))
            mu = UniformDistribution(0, 100).getRandom()
            var = UniformDistribution(3, 25).getRandom() ** 2
            mu, std, likelihood, r = fastLagEM.compute(a, b, mu, var, len(a), len(b))
            tmp[j] = np.array([mu, std, likelihood])
            tmp2.append(r)

        idx = np.argmax(tmp[:, 2])
        queue.put([tmp[idx], tmp2[idx]])
