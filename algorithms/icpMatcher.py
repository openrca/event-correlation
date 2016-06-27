import math
from time import sleep

import matplotlib.pyplot as plt
import numpy as np
from scipy import optimize

from algorithms import Matcher, RESULT_MU, RESULT_SIGMA, RESULT_KDE, RESULT_IDX
from core.distribution import KdeDistribution


class IcpMatcher(Matcher):
    def __init__(self):
        super().__init__(__name__)
        self.initPose = None
        self.f = 1
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
            f: Fraction of a to be used during transformation calculation. If f < 1, some points of a are ignored and
                treated as outliers.
            showVisualization: Show a visualization of the current assignment after each iteration. Default is False.
        """
        if ("maxiter" in kwargs):
            self.maxiter = kwargs["maxiter"]
        if ("threshold" in kwargs):
            self.threshold = kwargs["threshold"]
        if ("initPos" in kwargs):
            self.initPose = kwargs["initPos"]
        if ("f" in kwargs):
            self.f = kwargs["f"]
        if ("showVisualization" in kwargs):
            self.showVisualization = kwargs["showVisualization"]

    def compute(self, src=None, model=None):
        if (src is None):
            src = np.array(self.sequence.asVector(self.eventA))
        if (model is None):
            model = np.array(self.sequence.asVector(self.eventB))

        self.switched = len(src) > len(model)
        if (self.switched):
            self.logger.info("Switching input and model")
            tmp = src
            src = model
            model = tmp

        data = np.array(src, copy=True).astype(float)

        if (self.initPose is None):
            self.initPose = self.findInitialGuess(data, model)

        opt = np.array(self.initPose).astype(np.float32)
        data += opt

        p = None
        for i in range(self.maxiter):
            if (p is not None and abs(p) < self.threshold):
                break

            subData = self.getSubset(data, model, 0.5)
            idx = IcpMatcher.findMinimalDistance(subData, model)
            p = IcpMatcher.findOptimalTransformation(opt, subData, model[idx])
            data += p
            opt += p

            self.logger.debug("Offset {}\t Distance {}".format(opt, IcpMatcher.costFunction(0, subData, model[idx])))
            if (self.showVisualization):
                IcpMatcher.visualizeCurrentStep(src, data, model, idx)

        idx = IcpMatcher.findMinimalDistance(data, model)
        idx = np.column_stack((np.arange(idx.size), idx))
        tmp = model[idx[:, 1]]
        self.logger.info("Final distance " + str(IcpMatcher.costFunction(0, data, tmp)))
        self.logger.info("Final offset " + str(opt))
        print(idx)

        cost = tmp - src
        cost = cost[abs(cost - cost.mean()) < 2.58 * cost.std()]
        if (self.switched):
            cost *= -1

        return {RESULT_MU: cost.mean(), RESULT_SIGMA: cost.std(), RESULT_KDE: KdeDistribution(cost), RESULT_IDX: idx,
                "Offset": opt}

    def findInitialGuess(self, data, model):
        [A, B] = np.meshgrid(data, model)
        guess = (B - A).mean()
        guess /= len(model) / len(data)
        self.logger.info("Estimated initial guess as {}".format(guess))
        return guess

    @staticmethod
    def visualizeCurrentStep(src, data, model, idx):
        plt.clf()
        plt.scatter(model, [0] * len(model), marker='x', c='b', label="Model")
        plt.scatter(src, [-1] * len(src), marker='x', c='r', label="Data")

        plt.scatter(data, [-0.5] * len(data), marker='x', c='g', label="Shifted data")
        plt.legend(loc="upper left")
        plt.ylim([-1.2, 0.4])

        for i in range(data.shape[0]):
            plt.plot([src[i], model[idx[i]]], [-1, 0], color='k', linestyle='-', linewidth=0.5)
            plt.plot([data[i], model[idx[i]]], [-0.5, 0], color='k', linestyle=':', linewidth=0.5)

        plt.show()
        sleep(1)

    @staticmethod
    def findMinimalDistance(data, model):
        [A, B] = np.meshgrid(data, model)
        delta = abs(B - A)
        return delta.argmin(axis=0)

    @staticmethod
    def findOptimalTransformation(p, data, model):
        # Compute minimum of cost function
        #   sum( (data + p - model)^2 )
        # with p the variable.
        result = optimize.minimize(IcpMatcher.costFunction, p, args=(data, model), method='Newton-CG',
                                   jac=IcpMatcher.jacobiMatrix, hess=IcpMatcher.hesseMatrix)
        return result.x[0]

    @staticmethod
    def costFunction(p, data, model):
        return math.sqrt(np.sum(np.square((data + p) - model)))

    @staticmethod
    def getSubset(data, model, f):
        if (f == 1):
            return data

        [A, B] = np.meshgrid(data, model)
        delta = abs(B - A)

        minIdx = np.column_stack((delta.argmin(axis=0), np.arange(data.size)))
        values = delta[minIdx[:, 0], minIdx[:, 1]]
        return data[minIdx[:, 1][values.argsort()[:math.floor(f * data.size)]]]

    # noinspection PyTypeChecker
    @staticmethod
    def jacobiMatrix(p, data, model):
        d = (data + p) - model
        return np.array([np.sum(2 * d)])

    # noinspection PyUnusedLocal
    @staticmethod
    def hesseMatrix(p, data, model):
        # This function has to have the same arguments as IcpMatcher.jacobiMatrix and IcpMatcher.totalDistance.
        # See http://docs.scipy.org/doc/scipy-0.17.1/reference/generated/scipy.optimize.minimize.html
        return 2 * np.size(data, 0)
