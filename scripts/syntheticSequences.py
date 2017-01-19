import json
import logging
import os

import matplotlib.pyplot as plt
import numpy as np

import algorithms
import core
from algorithms.icpMatcher import IcpMatcher
from algorithms.lagEM import lagEM
from algorithms.lpMatcher import LpMatcher, Method
from core import distribution
from core.timer import Timer
from provider.generator import Generator
from visualization import CORRECT, ICP, LP, LAGEM, plotDistributions

inputFile = '../contrib/scenarios/3.json'
sequenceCount = 1
create = True
plot = False

outputFile = os.path.toAbsolutePath(os.path.splitext(inputFile)[0] + '-out.json')


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


timer = Timer()
timer.start()
logger = logging.getLogger()
if (create):
    logger.info('Processing ' + inputFile)
    resultIcp = {}
    resultLp = {}
    resultLagEm = {}
    keys = set()

    sequence = None
    for i in range(sequenceCount):
        logger.debug('\tRound ' + str(i))
        sequence = Generator().create(inputFile)

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
        for rule in listLagEM:
            key = (rule.trigger, rule.response)
            keys.add(key)
            resultLagEm.setdefault(key, Result(key[0], key[1])).addData(rule.data)

    data = []
    gen = Generator()
    gen.create(inputFile)
    for key in keys:
        entry = {
            'trigger': key[0],
            'response': key[1],
            'count': gen.getNumberOfEvents()
        }
        data.append(entry)

        correct = sequence.getBaseDistribution(key[0], key[1])
        if (correct is not None):
            entry[CORRECT] = correct

        icp = resultIcp.get(key)
        if (icp is not None):
            entry[ICP] = {
                'mean': icp.getMean(),
                'sigma': icp.getSigma(),
                'samples': icp.getSamples()
            }

        lp = resultLp.get(key)
        if (lp is not None):
            entry[LP] = {
                'mean': lp.getMean(),
                'sigma': lp.getSigma(),
                'samples': lp.getSamples()
            }

        lagEM = resultLagEm.get(key)
        if (lagEM is not None):
            entry[LAGEM] = {
                'mean': lagEM.getMean(),
                'sigma': lagEM.getSigma(),
                'samples': lagEM.getSamples()
            }
    with open(outputFile, 'w') as out:
        json.dump(data, out, default=core.defaultJsonEncoding)
timer.stop()
logger.info("Calculation finished after {}".format(timer))

if (plot):
    with open(outputFile, 'r') as input:
        content = input.readlines()
        data = json.loads("".join(content))
        for entry in data:
            plotDistributions({
                CORRECT: distribution.load(entry[CORRECT]) if CORRECT in entry else None,
                ICP: entry[ICP]['samples'] if ICP in entry else None,
                LP: entry[LP]['samples'] if LP in entry else None,
                LAGEM: [entry[LAGEM]['mean'], entry[LAGEM]['sigma']] if LAGEM in entry else None
            }, '{}-{}'.format(entry['trigger'], entry['response']))
        plt.show()
