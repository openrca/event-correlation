from time import sleep

import matplotlib.pyplot as plt
import numpy as np
from scipy import optimize
from sklearn.neighbors import NearestNeighbors

from algorithms import Matcher, RESULT_MU, RESULT_SIGMA, RESULT_KDE
from core.distribution import KdeDistribution


class IcpMatcher(Matcher):
    def __init__(self):
        super().__init__(__name__)
        self.initPose = None
        self.maxiter = 50
        self.threshold = 1e-4
        self.showVisualization = False

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
            self.initPose = np.array(kwargs["initPos"]).astype(np.float32)
        if ("showVisualization" in kwargs):
            self.showVisualization = kwargs["showVisualization"]

    def compute(self, src=None, dst=None):
        if (src is None):
            src = np.array(self.sequence.asVector(self.eventA), copy=True).astype(np.float32)
            # artificially shift data for better visualization
            src = np.column_stack((src, np.ones(src.size) * -0.5))

        if (dst is None):
            dst = np.array(self.sequence.asVector(self.eventB), copy=True).astype(np.float32)
            dst = np.column_stack((dst, np.zeros(dst.size)))

        a = np.array(src, copy=True).astype(np.float32)
        b = np.array(dst, copy=True).astype(np.float32)

        if (self.initPose is None):
            self.initPose = self.findInitialGuess(a, b)

        opt = np.array(self.initPose).astype(np.float32)
        a = IcpMatcher.transform(opt, a)

        p = None
        for i in range(self.maxiter):
            if (p is not None and np.linalg.norm(p) < self.threshold):
                break

            idx = IcpMatcher.findMinimalDistance(a, b)
            p = IcpMatcher.findOptimalTransformation(opt, a, b[idx])
            a = IcpMatcher.transform(p, a)
            opt += p

            self.logger.debug("Offset {}\t Distance {}".format(opt, IcpMatcher.totalDistance(np.array([0, 0]),
                                                                                             a, b[idx])))
            if (self.showVisualization):
                IcpMatcher.visualizeCurrentStep(src, dst, a, b[idx])

        idx = IcpMatcher.findMinimalDistance(a, b)
        self.logger.info("Final distance " + str(IcpMatcher.totalDistance(np.array([0, 0]), a, b[idx])))
        self.logger.info("Final offset " + str(opt))

        idx = IcpMatcher.findMinimalDistance(a, b)
        print(idx)
        tmp = b[idx]

        cost = np.zeros(np.shape(a))
        cost[:, 0] = tmp[:, 0] - src[:, 0]
        # cost[:, 1] = tmp[:, 1] - src[:, 1]
        cost = np.linalg.norm(cost, axis=1)

        cost = cost[abs(cost - cost.mean()) < 2.58 * cost.std()]
        print(cost)

        return {RESULT_MU: cost.mean(), RESULT_SIGMA: cost.std(), RESULT_KDE: KdeDistribution(cost), "Offset": opt}

    def findInitialGuess(self, a, b):
        [Ax, Bx] = np.meshgrid(a[:, 0], b[:, 0])
        guessX = (Bx - Ax).mean()

        [Ay, By] = np.meshgrid(a[:, 1], b[:, 1])
        guessY = (By - Ay).mean()

        guess = np.array([guessX, guessY]).astype(np.float32)
        self.logger.info("Estimated initial guess as {}".format(guess))
        return guess

    @staticmethod
    def visualizeCurrentStep(src, dst, a, b):
        plt.clf()
        plt.scatter(dst[:, 0], dst[:, 1], marker='x', c='b', label="Reference")
        plt.scatter(src[:, 0], src[:, 1], marker='x', c='r', label="Input")

        plt.scatter(a[:, 0], a[:, 1], marker='x', c='g', label="Shifted Result")
        plt.legend(loc="upper left")
        # plt.xlim([0, 200])
        # plt.ylim([-2, 2])

        for i in range(a.shape[0]):
            plt.plot([src[i, 0], b[i, 0]], [src[i, 1], b[i, 1]], color='k', linestyle='-', linewidth=0.5)

        plt.show()
        sleep(1)

    @staticmethod
    def findMinimalDistance(a, b):
        neighbours = NearestNeighbors(n_neighbors=1, algorithm='auto').fit(b)
        distances, idx = neighbours.kneighbors(a)
        return idx.flatten()

    @staticmethod
    def findOptimalTransformation(p, a, b):
        # Compute minimum of cost function
        #   sum( (T * a - b) * (T * a - b)' )
        # with
        #   T = [[ 1 0 p_x],
        #        [ 0 1 p_y]]
        # and p the variable.
        result = optimize.minimize(IcpMatcher.totalDistance, p, args=(a, b), method='Newton-CG',
                                   jac=IcpMatcher.jacobiMatrix, hess=IcpMatcher.hesseMatrix)
        return result.x

    @staticmethod
    def totalDistance(p, a, b):
        xt = IcpMatcher.transform(p, a)

        d = np.zeros(np.shape(a))
        d[0, :] = xt[0, :] - b[0, :]
        d[1, :] = xt[1, :] - b[1, :]

        return np.sum(np.square(d[:, 0]) + np.square(d[:, 1]))

    @staticmethod
    def transform(p, points):
        T = p
        if (p.ndim == 1):
            T = np.array([[1, 0, p[0]],
                          [0, 1, p[1]]])

        tmp = np.column_stack((points, np.ones(len(points))))
        dst = np.zeros(points.shape)

        for i in range(len(points)):
            dst[i] = T.dot(tmp[i])
        return dst

    # noinspection PyTypeChecker
    @staticmethod
    def jacobiMatrix(p, a, b):
        xt = IcpMatcher.transform(p, a)

        d = np.zeros(np.shape(a))
        d[:, 0] = xt[:, 0] - b[:, 0]
        d[:, 1] = xt[:, 1] - b[:, 1]

        return np.array([np.sum(2 * d[:, 0]),
                         np.sum(2 * d[:, 1])])

    # noinspection PyUnusedLocal
    @staticmethod
    def hesseMatrix(p, a, b):
        # This function has to have the same arguments as IcpMatcher.jacobiMatrix and IcpMatcher.totalDistance.
        # See http://docs.scipy.org/doc/scipy-0.17.1/reference/generated/scipy.optimize.minimize.html
        return np.eye(2) * 2 * np.size(a, 0)
