import unittest

from core import bayesianNetwork
from core.bayesianNetwork import BayesianNetwork, Evidence
from core.distribution import NormalDistribution
from core.event import Event
from core.rule import Rule
from core.sequence import Sequence


class TestScript(unittest.TestCase):
    def test(self):
        seq = Sequence([Event('A'), Event('B'), Event('C')])
        seq.calculatedRules = [
            Rule('A', 'C', NormalDistribution(), successResponse=0.8, successTrigger=0.2),
            Rule('B', 'C', NormalDistribution(), successResponse=0.5, successTrigger=0.5),
        ]

        bn = BayesianNetwork(seq)
        bn.createCompleteGraph()
        bn.learnStructure()

        res = bn.query('C', [Evidence('A', True), Evidence('B', True)])
        print(res)
