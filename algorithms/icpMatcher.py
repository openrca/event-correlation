from time import sleep

import matplotlib.pyplot as plt
import numpy as np
from scipy import optimize

from algorithms import Matcher, RESULT_MU, RESULT_SIGMA, RESULT_KDE
from core.distribution import KdeDistribution


class IcpMatcher(Matcher):
    def __init__(self):
        super().__init__(__name__)
        self.initPose = None
        self.maxiter = 50
        self.threshold = 1e-4
        self.showVisualization = False
        self.switched = False

    def parseArgs(self, kwargs):
        """
        Additional parameters:
            maxiter: Maximum number of iterations. Default is 50.
            threshold: Threshold for offset length. If the change of the offset is smaller than threshold,
                the calculation is considered as converged. Default if 1e-4.
            initPose: Initial guess of the offset. If not provided, initial guess is calculated from input.
            showVisualization: Show a visualization of the current assignment after each iteration. Default is False.
        """
        if ("maxiter" in kwargs):
            self.maxiter = kwargs["maxiter"]
        if ("threshold" in kwargs):
            self.threshold = kwargs["threshold"]
        if ("initPos" in kwargs):
            self.initPose = kwargs["initPos"]
        if ("showVisualization" in kwargs):
            self.showVisualization = kwargs["showVisualization"]

    def compute(self, src=None, dst=None):
        if (src is None):
            src = np.array(self.sequence.asVector(self.eventA))
        if (dst is None):
            dst = np.array(self.sequence.asVector(self.eventB))

        self.switched = len(src) > len(dst)
        if (self.switched):
            self.logger.info("Switching src and dst")
            tmp = src
            src = dst
            dst = tmp

        a = np.array(src, copy=True).astype(float)
        b = np.array(dst, copy=True).astype(float)

        if (self.initPose is None):
            self.initPose = self.findInitialGuess(a, b)

        opt = np.array(self.initPose).astype(np.float32)
        a += opt

        p = None
        for i in range(self.maxiter):
            if (p is not None and abs(p) < self.threshold):
                break

            idx = IcpMatcher.findMinimalDistance(a, b)
            p = IcpMatcher.findOptimalTransformation(opt, a, b[idx])
            a += p
            opt += p

            self.logger.debug("Offset {}\t Distance {}".format(opt, IcpMatcher.totalDistance(0, a, b[idx])))
            if (self.showVisualization):
                IcpMatcher.visualizeCurrentStep(src, dst, a, b[idx])

        idx = IcpMatcher.findMinimalDistance(a, b)
        tmp = b[idx]
        self.logger.info("Final distance " + str(IcpMatcher.totalDistance(0, a, tmp)))
        self.logger.info("Final offset " + str(opt))
        print(idx)

        cost = tmp - src
        cost = cost[abs(cost - cost.mean()) < 2.58 * cost.std()]
        if (self.switched):
            cost *= -1

        return {RESULT_MU: cost.mean(), RESULT_SIGMA: cost.std(), RESULT_KDE: KdeDistribution(cost), "Offset": opt}

    def findInitialGuess(self, a, b):
        [A, B] = np.meshgrid(a, b)
        guess = (B - A).mean()
        self.logger.info("Estimated initial guess as {}".format(guess))
        return guess

    @staticmethod
    def visualizeCurrentStep(src, dst, a, b):
        plt.clf()
        plt.scatter(dst, [0] * len(dst), marker='x', c='b', label="Reference")
        plt.scatter(src, [-1] * len(src), marker='x', c='r', label="Input")

        plt.scatter(a, [-0.5] * len(a), marker='x', c='g', label="Shifted Result")
        plt.legend(loc="upper left")
        plt.ylim([-1.2, 0.4])

        for i in range(a.shape[0]):
            plt.plot([src[i], b[i]], [-1, 0], color='k', linestyle='-', linewidth=0.5)
            plt.plot([a[i], b[i]], [-0.5, 0], color='k', linestyle=':', linewidth=0.5)

        plt.show()
        sleep(1)

    @staticmethod
    def findMinimalDistance(a, b):
        [A, B] = np.meshgrid(a, b)
        delta = abs(B - A)
        return delta.argmin(axis=0)

    @staticmethod
    def findOptimalTransformation(p, a, b):
        # Compute minimum of cost function
        #   sum( (a + p - b)^2 )
        # with p the variable.
        result = optimize.minimize(IcpMatcher.totalDistance, p, args=(a, b), method='Newton-CG',
                                   jac=IcpMatcher.jacobiMatrix, hess=IcpMatcher.hesseMatrix)
        return result.x[0]

    @staticmethod
    def totalDistance(p, a, b):
        return np.sum(np.square((a + p) - b))

    # noinspection PyTypeChecker
    @staticmethod
    def jacobiMatrix(p, a, b):
        d = (a + p) - b
        return np.array([np.sum(2 * d)])

    # noinspection PyUnusedLocal
    @staticmethod
    def hesseMatrix(p, a, b):
        # This function has to have the same arguments as IcpMatcher.jacobiMatrix and IcpMatcher.totalDistance.
        # See http://docs.scipy.org/doc/scipy-0.17.1/reference/generated/scipy.optimize.minimize.html
        return 2 * np.size(a, 0)
