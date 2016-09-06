import fastLagEM
import threading

import numpy as np

from algorithms import Matcher, RESULT_MU, RESULT_SIGMA, RESULT_IDX, RESULT_KDE
from core.distribution import UniformDistribution, KdeDistribution, NormalDistribution


class lagEM(Matcher):
    def __init__(self):
        super().__init__(__name__)
        self.threshold = None

    def parseArgs(self, kwargs):
        """
        Additional parameters:
            threshold: Defines a threshold for parameter convergence
        """
        self.threshold = kwargs["threshold"]

    def compute(self):
        self.logger.info("Matching event {} against {}".format(self.eventA, self.eventB))
        a = self.sequence.asVector(self.eventA)
        b = self.sequence.asVector(self.eventB)

        result = np.zeros([10, 3])
        threads = []
        for i in range(10):
            thread = threading.Thread(target=self.computeParallel, args=(a, b, result, i,))
            thread.start()
            threads.append(thread)

        for i in range(10):
            threads[i].join()
        threads.clear()
        self.logger.info("Results:\n {}".format(result))
        tmp = result.sum(axis=0) / np.count_nonzero(result[:, 0])
        return {RESULT_MU: tmp[0], RESULT_SIGMA: tmp[1], "Likelihood": result[:, 2].max(), RESULT_IDX: None,
                RESULT_KDE: KdeDistribution(NormalDistribution(tmp[0], tmp[1]).getRandom(min(a.size, b.size)))}

    def computeParallel(self, a, b, result, index):
        self.logger.info("Processing batch {}".format(index))
        tmp = np.zeros([20, 3])
        for j in range(20):
            self.logger.debug("Worker[{}]: Processing round {}".format(index, j))
            mu = UniformDistribution(0, 100).getRandom()
            var = UniformDistribution(3, 25).getRandom() ** 2
            tmp[j] = fastLagEM.compute(a, b, mu, var, len(a), len(b))
        result[index] = tmp[np.argmax(tmp[:, 2])]
