import math
import numbers
import sys
from time import sleep

import matplotlib.pyplot as plt
import numpy as np
from scipy import optimize

from algorithms import Matcher, RESULT_MU, RESULT_SIGMA, RESULT_KDE, RESULT_IDX, InitialGuess, CONFIDENCE_80
from core.distribution import KdeDistribution


class IcpMatcher(Matcher):
    def __init__(self):
        super().__init__(__name__)
        self.__initPose = None
        self.__f = None
        self.__maxiter = 50
        self.__threshold = 1e-6
        self.__showVisualization = False

    def _parseArgs(self, kwargs):
        """
        Additional parameters:
            maxiter: Maximum number of iterations. Default is 50.
            threshold: Threshold for offset length. If the change of the offset is smaller than threshold,
                the calculation is considered as converged. Default if 1e-4.
            initPose: Initial guess of the offset. If not provided, initial guess is calculated from input.
            f: Fraction of src to be used during transformation calculation. This parameter is used to eliminate
                outliers. Allowed values are:
                    None: No outlier reduction
                    [0, 1]: Remove (1 - f) * 100 % of the data points
                    "confidence": Remove values that are not in the 80% confidence interval
            showVisualization: Show a visualization of the current assignment after each iteration. Default is False.
        """
        if ("maxiter" in kwargs):
            self.__maxiter = kwargs["maxiter"]
        if ("threshold" in kwargs):
            self.__threshold = kwargs["threshold"]
        if ("initPos" in kwargs):
            self.__initPose = kwargs["initPos"]
        if ("f" in kwargs):
            self.__f = kwargs["f"]
        if ("showVisualization" in kwargs):
            self.__showVisualization = kwargs["showVisualization"]

    def _compute(self, trigger, response):
        data = np.array(trigger, copy=True).astype(float)
        model = np.array(response, copy=True).astype(float)

        if (len(trigger) > len(response)):
            self._logger.debug('Switching trigger and response for calculation')
            tmp = data
            data = model
            model = tmp

        if (self.__initPose is None):
            # TODO find better method for initial guess
            mean = MeanDistanceInitialGuess().computeOffset(data, model)
            sac = SampleConsensusInitialGuess().computeOffset(data, model)
            binAlignment = BinAlignmentInitialGuess().computeOffset(data, model)
            self._logger.trace("Mean initial guess: {}".format(mean))
            self._logger.trace("SAC initial guess: {}".format(sac))
            self._logger.trace("Bin alignment initial guess: {}".format(binAlignment))
            self.__initPose = (mean + sac + binAlignment) / 3
            self.__initPose = sac
            self._logger.info("Estimated initial guess as {}".format(self.__initPose))

        opt = np.array(self.__initPose).astype(np.float32)
        data += opt

        t = None
        for i in range(self.__maxiter):
            if (t is not None and abs(t) < self.__threshold):
                break

            subData, selectedIdx = self.__getSubset(data, model)
            idx = IcpMatcher._findMinimalDistance(subData, model)
            t = IcpMatcher._findOptimalTransformation(subData, model[idx])
            data += t
            opt += t

            self._logger.debug("Offset {}\t Distance {}".format(opt, IcpMatcher.__costFunction(0, subData, model[idx])))
            if (self.__showVisualization):
                IcpMatcher.__visualizeCurrentStep(trigger, subData, selectedIdx, model, idx)

        idx = IcpMatcher._findMinimalDistance(data, model)
        idx = np.column_stack((np.arange(idx.size), idx))
        tmp = model[idx[:, 1]]
        self._logger.info("Final offset {} ({} distance)".format(opt, IcpMatcher.__costFunction(0, data, tmp)))

        if (len(trigger) > len(response)):
            cost = (tmp - response) * -1
            idx[:, 0], idx[:, 1] = idx[:, 1], idx[:, 0].copy()
        else:
            cost = tmp - trigger
        cost = self._trimVector(cost)
        return {RESULT_MU: cost.mean(), RESULT_SIGMA: cost.std(), RESULT_KDE: KdeDistribution(cost), RESULT_IDX: idx,
                "Offset": opt}

    @staticmethod
    def __visualizeCurrentStep(src, data, dataIdx, model, modelIdx):
        plt.clf()
        plt.scatter(model, [0] * len(model), marker='x', c='b', label="Model")
        plt.scatter(src, [-1] * len(src), marker='x', c='r', label="Data")

        plt.scatter(data, [-0.5] * len(data), marker='x', c='g', label="Shifted data")
        plt.legend(loc="upper left")
        plt.ylim([-1.2, 0.4])

        for i in range(modelIdx.shape[0]):
            plt.plot([data[i], src[dataIdx[i]]], [-0.5, -1], color='k', linestyle='-', linewidth=0.5)
            plt.plot([data[i], model[modelIdx[i]]], [-0.5, 0], color='k', linestyle=':', linewidth=0.5)

        plt.show()
        sleep(1)

    @staticmethod
    def _findMinimalDistance(data, model, k=1):
        [A, B] = np.meshgrid(data, model)
        delta = abs(B - A)
        if (k == 1):
            return delta.argmin(axis=0)
        return np.argsort(delta, axis=0)[0:k, :].flatten()

    @staticmethod
    def _findOptimalTransformation(data, model):
        # Compute minimum of cost function
        #   sum( (data + t - model)^2 )
        # with t the variable.
        result = optimize.minimize(IcpMatcher.__costFunction, np.zeros(1), args=(data, model), method='Newton-CG',
                                   jac=IcpMatcher.__jacobiMatrix, hess=IcpMatcher.__hesseMatrix)
        return result.x[0]

    @staticmethod
    def __costFunction(t, data, model):
        return np.sum(abs((data + t) - model))

    def __getSubset(self, data, model):
        if (self.__f == 1 or self.__f is None):
            return data, np.arange(data.size)

        [A, B] = np.meshgrid(data, model)
        delta = abs(B - A)

        minIdx = np.column_stack((delta.argmin(axis=0), np.arange(data.size)))
        values = delta[minIdx[:, 0], minIdx[:, 1]]

        selectedIdx = values
        if (isinstance(self.__f, numbers.Number)):
            # based on The Trimmed Iterative Closest Point algorithm, Chetverikov, Svirko and Stepanov
            selectedIdx = values.argsort()[:math.floor(self.__f * data.size)]
        if (self.__f == "confidence"):
            # based on The Dual-Bootstrap Iterative Closest Point Algorithm With Application to Retinal Image
            # Registration, Stewart, Tsai and Roysam
            selectedIdx = np.arange(values.size)[abs(values - values.mean()) < CONFIDENCE_80 * values.std()]

        # select at most one data point per model point
        if (selectedIdx.size > model.size):
            selectedIdx = values[selectedIdx].argsort()[:model.size]

        self._logger.trace("Selected {} from {} values".format(selectedIdx.size, data.size))
        return data[minIdx[:, 1][selectedIdx]], selectedIdx

    # noinspection PyTypeChecker
    @staticmethod
    def __jacobiMatrix(t, data, model):
        d = (data + t) - model
        return np.sum(np.where(d > 0)) - np.sum(np.where(d < 0))

    # noinspection PyUnusedLocal
    @staticmethod
    def __hesseMatrix(t, data, model):
        # This function has to have the same arguments as IcpMatcher.jacobiMatrix and IcpMatcher.totalDistance.
        # See http://docs.scipy.org/doc/scipy-0.17.1/reference/generated/scipy.optimize.minimize.html
        return 0


class SampleConsensusInitialGuess(InitialGuess):
    """
    Compute (mostly) robust initial transformation for IcpMatcher.

    Calculation is based on [1] Fast Point Feature Histograms (FPFH) for 3D registration, Rusu, Blodow and Beetz,
    Section IV Sample Consensus Initial Alignment: SAC-IA and [2] PointCloudLibrary(PCL) implementation on
    http://docs.pointclouds.org/trunk/ia__ransac_8hpp_source.html
    """

    def __init__(self):
        self.__nrSamples = 3
        self.__maxIterations = 500
        self.__minSampleDistance = 0
        self.__distanceThreshold = 50
        self.__kCorrespondence = 2

    def computeOffset(self, data, model):
        guess = 0
        minError = sys.maxsize
        for i in range(self.__maxIterations):
            dataSamples = self.__selectSamples(data)
            modelSamples = self.__findSimilarFeatures(dataSamples, model)

            # noinspection PyProtectedMember
            t = IcpMatcher._findOptimalTransformation(dataSamples, modelSamples)
            d = dataSamples + t
            error = self.__computeErrorMetric(d, model)
            if (error < minError):
                guess = t
                minError = error
        return guess

    def __selectSamples(self, data):
        result = []
        iterationsWithoutSample = 0
        while (len(result) < self.__nrSamples):
            if (iterationsWithoutSample > 3 * data.size):
                self.__minSampleDistance /= 2
                iterationsWithoutSample = 0

            d = np.random.choice(data, 1)
            for i in result:
                if (abs(d - i) < self.__minSampleDistance):
                    iterationsWithoutSample += 1
                    continue
            iterationsWithoutSample = 0
            result.append(d)

        return np.array(result).flatten()

    def __findSimilarFeatures(self, data, model):
        result = []
        for d in data:
            # noinspection PyProtectedMember
            idx = IcpMatcher._findMinimalDistance(d, model, self.__kCorrespondence)
            result.append(np.random.choice(idx, 1)[0])

        return model[result]

    def __computeErrorMetric(self, data, model):
        error = 0
        # noinspection PyProtectedMember
        idx = IcpMatcher._findMinimalDistance(data, model)
        dist = data - model[idx]
        for d in dist:
            error += min(abs(d) / self.__distanceThreshold, 1)
        return error


class BinAlignmentInitialGuess(InitialGuess):
    def __init__(self):
        self.__nrBins = None
        self.__binLength = None
        self.__interval = None
        self.__modelBins = None

        self.__data = None
        self.__model = None

    def computeOffset(self, data, model):
        self.__model = model
        self.__data = data

        self.__setNumberOfBins(data, model)
        self.__interval = (min(data.min(), model.min()), max(data.max(), model.max()))
        self.__binLength = (self.__interval[1] - self.__interval[0]) / self.__nrBins
        self.__modelBins = self.__countBinAssignments(model, 0)

        result = optimize.minimize(self.__costFunction, np.zeros(1), method="TNC", jac=self.__jacobiFunction,
                                   bounds=[(-self.__interval[1], self.__interval[1])])
        return result.x

    def __setNumberOfBins(self, data, model):
        # Based on Sturges rules
        dataBins = math.log2(data.size) + 1
        modelBins = math.log2(model.size) + 1
        self.__nrBins = math.floor(max(dataBins, modelBins))

    def __countBinAssignments(self, points, offset):
        borders = np.arange(self.__nrBins + 1) * self.__binLength + self.__interval[0]
        return np.histogram(points - offset, borders)[0]

    def __costFunction(self, offset):
        dataBins = self.__countBinAssignments(self.__data, offset)
        return abs(dataBins - self.__modelBins).sum() ** 2

    def __jacobiFunction(self, offset):
        modelMean = self.__model.mean() - offset
        dataMean = self.__data.mean()
        return dataMean - modelMean


class MeanDistanceInitialGuess(InitialGuess):
    def computeOffset(self, data, model):
        return model.mean() - data.mean()
