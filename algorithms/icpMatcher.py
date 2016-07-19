import math
import numbers
from time import sleep
import sys

import matplotlib.pyplot as plt
import numpy as np
from scipy import optimize

from algorithms import Matcher, RESULT_MU, RESULT_SIGMA, RESULT_KDE, RESULT_IDX, InitialGuess
from core.distribution import KdeDistribution


class IcpMatcher(Matcher):
    def __init__(self):
        super().__init__(__name__)
        self.initPose = None
        self.f = None
        self.maxiter = 50
        self.threshold = 1e-6
        self.showVisualization = False

    def parseArgs(self, kwargs):
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

        data = np.array(src, copy=True).astype(float)

        if (self.initPose is None):
            # TODO find better method for initial guess
            mean = MeanDistanceInitialGuess().computeOffset(data, model)
            sac = SampleConsensusInitialGuess().computeOffset(data, model)
            binAlignment = BinAlignmentInitialGuess().computeOffset(data, model)
            self.logger.trace("Mean initial guess: {}".format(mean))
            self.logger.trace("SAC initial guess: {}".format(sac))
            self.logger.trace("Bin alignment initial guess: {}".format(binAlignment))
            self.initPose = (mean + sac + binAlignment) / 3
            self.logger.info("Estimated initial guess as {}".format(self.initPose))

        opt = np.array(self.initPose).astype(np.float32)
        data += opt

        p = None
        for i in range(self.maxiter):
            if (p is not None and abs(p) < self.threshold):
                break

            subData, selectedIdx = self.getSubset(data, model)
            idx = IcpMatcher.findMinimalDistance(subData, model)
            p = IcpMatcher.findOptimalTransformation(opt, subData, model[idx])
            data += p
            opt += p

            self.logger.debug("Offset {}\t Distance {}".format(opt, IcpMatcher.costFunction(0, subData, model[idx])))
            if (self.showVisualization):
                IcpMatcher.visualizeCurrentStep(src, subData, selectedIdx, model, idx)

        idx = IcpMatcher.findMinimalDistance(data, model)
        idx = np.column_stack((np.arange(idx.size), idx))
        tmp = model[idx[:, 1]]
        self.logger.info("Final distance " + str(IcpMatcher.costFunction(0, data, tmp)))
        self.logger.info("Final offset " + str(opt))

        cost = tmp - src
        cost = self.trimVector(cost)
        return {RESULT_MU: cost.mean(), RESULT_SIGMA: cost.std(), RESULT_KDE: KdeDistribution(cost), RESULT_IDX: idx,
                "Offset": opt}

    @staticmethod
    def visualizeCurrentStep(src, data, dataIdx, model, modelIdx):
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
    def findMinimalDistance(data, model, k=1):
        [A, B] = np.meshgrid(data, model)
        delta = abs(B - A)
        if (k == 1):
            return delta.argmin(axis=0)
        return np.argsort(delta, axis=0)[0:k, :].flatten()

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

    def getSubset(self, data, model):
        if (self.f == 1 or self.f is None):
            return data, np.arange(data.size)

        [A, B] = np.meshgrid(data, model)
        delta = abs(B - A)

        minIdx = np.column_stack((delta.argmin(axis=0), np.arange(data.size)))
        values = delta[minIdx[:, 0], minIdx[:, 1]]

        selectedIdx = values
        if (isinstance(self.f, numbers.Number)):
            # based on The Trimmed Iterative Closest Point algorithm, Chetverikov, Svirko and Stepanov
            selectedIdx = values.argsort()[:math.floor(self.f * data.size)]
        if (self.f == "confidence"):
            # based on The Dual-Bootstrap Iterative Closest Point Algorithm With Application to Retinal Image
            # Registration, Stewart, Tsai and Roysam
            selectedIdx = np.arange(values.size)[abs(values - values.mean()) < 1.282 * values.std()]

        # select at most one data point per model point
        if (selectedIdx.size > model.size):
            selectedIdx = values[selectedIdx].argsort()[:model.size]

        self.logger.trace("Selected {} from {} values".format(selectedIdx.size, data.size))
        return data[minIdx[:, 1][selectedIdx]], selectedIdx

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


class SampleConsensusInitialGuess(InitialGuess):
    """
    Compute (mostly) robust initial transformation for IcpMatcher.

    Calculation is based on [1] Fast Point Feature Histograms (FPFH) for 3D registration, Rusu, Blodow and Beetz,
    Section IV Sample Consensus Initial Alignment: SAC-IA and [2] PointCloudLibrary(PCL) implementation on
    http://docs.pointclouds.org/trunk/ia__ransac_8hpp_source.html
    """

    def __init__(self):
        self.nrSamples = 3
        self.maxIterations = 500
        self.minSampleDistance = 0
        self.distanceThreshold = 50
        self.kCorrespondence = 2

    def selectSamples(self, data):
        result = []
        iterationsWithoutSample = 0
        while (len(result) < self.nrSamples):
            d = np.random.choice(data, 1)
            valid = True

            for i in result:
                if (abs(d - i) < self.minSampleDistance):
                    valid = False

            if (valid):
                iterationsWithoutSample = 0
                result.append(d)
            else:
                iterationsWithoutSample += 1
            if (iterationsWithoutSample > 3 * data.size):
                self.minSampleDistance /= 2
                iterationsWithoutSample = 0

        return np.array(result).flatten()

    def findSimilarFeatures(self, data, model):
        result = []
        for d in data:
            idx = IcpMatcher.findMinimalDistance(d, model, self.kCorrespondence)
            result.append(np.random.choice(idx, 1)[0])

        return model[result]

    def computeErrorMetric(self, data, model):
        error = 0
        idx = IcpMatcher.findMinimalDistance(data, model)
        dist = data - model[idx]
        for d in dist:
            error += min(abs(d) / self.distanceThreshold, 1)
        return error

    def computeOffset(self, data, model):
        guess = 0
        minError = sys.maxsize
        for i in range(self.maxIterations):
            dataSamples = self.selectSamples(data)
            modelSamples = self.findSimilarFeatures(dataSamples, model)

            p = IcpMatcher.findOptimalTransformation(0, dataSamples, modelSamples)
            d = dataSamples + p
            error = self.computeErrorMetric(d, model)
            if (error < minError):
                guess = p
                minError = error
        return guess


class BinAlignmentInitialGuess(InitialGuess):
    def __init__(self):
        self.nrBins = None
        self.binLength = None
        self.interval = None
        self.modelBins = None

        self.data = None
        self.model = None

    def computeOffset(self, data, model):
        self.model = model
        self.data = data

        self.setNumberOfBins(data, model)
        self.interval = (min(data.min(), model.min()), max(data.max(), model.max()))
        self.binLength = (self.interval[1] - self.interval[0]) / self.nrBins
        self.modelBins = self.countBinAssignments(model, 0)

        result = optimize.minimize(self.costFunction, 0, method="TNC", jac=self.jacobiFunction,
                                   bounds=[(-self.interval[1], self.interval[1])])
        return result.x

    def setNumberOfBins(self, data, model):
        # Based on Sturges rules
        dataBins = math.log2(data.size) + 1
        modelBins = math.log2(model.size) + 1
        self.nrBins = math.floor(max(dataBins, modelBins))

    def countBinAssignments(self, points, offset):
        borders = np.arange(self.nrBins + 1) * self.binLength + self.interval[0]
        return np.histogram(points - offset, borders)[0]

    def costFunction(self, offset):
        dataBins = self.countBinAssignments(self.data, offset)
        return abs(dataBins - self.modelBins).sum() ** 2

    def jacobiFunction(self, offset):
        modelMean = self.model.mean() - offset
        dataMean = self.data.mean()
        return dataMean - modelMean


class MeanDistanceInitialGuess(InitialGuess):
    def computeOffset(self, data, model):
        return model.mean() - data.mean()
