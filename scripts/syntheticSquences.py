import logging
import os

import matplotlib.pyplot as plt
import numpy as np

import algorithms
from algorithms.icpMatcher import IcpMatcher
from algorithms.lagEM import lagEM
from algorithms.lpMatcher import LpMatcher, Method
from provider.generator import Generator
from visualization import CORRECT, ICP, LP, LAGEM, plotDistributions

inputFiles = ['../contrib/generation.json']
sequenceCount = 1


class Result:
    def __init__(self, trigger, response):
        self.trigger = trigger
        self.response = response
        self.__samples = []
        self.__mean = 0
        self.__sigma = 0
        self.__count = 0

    def addData(self, data):
        self.__samples.append(data[algorithms.RESULT_KDE].samples)
        self.__mean += data[algorithms.RESULT_MU]
        self.__sigma += data[algorithms.RESULT_SIGMA]
        self.__count += 1

    def getSamples(self):
        return np.concatenate(self.__samples)

    def getMean(self):
        return self.__mean / self.__count if self.__count > 0 else 0

    def getSigma(self):
        return self.__sigma / self.__count if self.__count > 0 else 0

    def __hash__(self):
        return hash(self.trigger) + hash(self.response)

    def __eq__(self, other):
        return self.trigger == other.trigger and self.response == other.response


logger = logging.getLogger()
for file in inputFiles:
    logger.info('Processing ' + file)
    resultIcp = {}
    resultLp = {}
    resultLagEm = {}
    keys = set()

    sequence = None
    for i in range(sequenceCount):
        logger.debug('\tRound ' + str(i))
        sequence = Generator().create(file)

        listIcp = IcpMatcher().matchAll(sequence, f="confidence")
        for rule in listIcp:
            key = (rule.trigger, rule.response)
            keys.add(key)
            resultIcp.setdefault(key, Result(key[0], key[1])).addData(rule.data)

        listLp = LpMatcher().matchAll(sequence, algorithm=Method.PULP)
        for rule in listLp:
            key = (rule.trigger, rule.response)
            keys.add(key)
            resultLp.setdefault(key, Result(key[0], key[1])).addData(rule.data)

        listLagEM = lagEM().matchAll(sequence, threshold=0.01, enforceNormal=True)
        for rule in listLp:
            key = (rule.trigger, rule.response)
            keys.add(key)
            resultLagEm.setdefault(key, Result(key[0], key[1])).addData(rule.data)

    with open(os.path.splitext(file)[0] + '.out', 'w') as out:
        for key in keys:
            out.write('{} -> {}\n'.format(key[0], key[1]))
            data = {}
            correct = sequence.getBaseDistribution(key[0], key[1])
            if (correct is not None):
                data[CORRECT] = correct

            icp = resultIcp.get(key)
            out.write('\tIcp\n')
            if (icp is not None):
                out.write('\t\tMean: {}\n'.format(icp.getMean()))
                out.write('\t\tSigma: {}\n'.format(icp.getSigma()))
                out.write('\t\tSamples: {}\n'.format(icp.getSamples()))
                data[ICP] = icp.getSamples()

            lp = resultLp.get(key)
            out.write('\tLp\n')
            if (lp is not None):
                out.write('\t\tMean: {}\n'.format(lp.getMean()))
                out.write('\t\tSigma: {}\n'.format(lp.getSigma()))
                out.write('\t\tSamples: {}\n'.format(lp.getSamples()))
                data[LP] = lp.getSamples()

            lagEM = resultLagEm.get(key)
            out.write('\tlagEM\n')
            if (lagEM is not None):
                out.write('\t\tMean: {}\n'.format(lagEM.getMean()))
                out.write('\t\tSigma: {}\n'.format(lagEM.getSigma()))
                out.write('\t\tSamples: {}\n'.format(lagEM.getSamples()))
                data[LAGEM] = lagEM.getSamples()

            plotDistributions(data, '{}-{}'.format(key[0], key[1]))
    plt.show()
