import unittest

import numpy as np

from algorithms import lpMatcher, RESULT_IDX
from algorithms.lpMatcher import LpMatcher
from core.event import Event
from core.sequence import Sequence


class TestScript(unittest.TestCase):

    def test_equal(self):
        algorithm = LpMatcher()
        algorithm.trimCost = False

        seq = Sequence([Event('A', 34), Event('A', 73), Event('A', 82),
                        Event('B', 109), Event('B', 149), Event('B', 169)], 6)

        result = algorithm.match(sequence=seq, eventA="A", eventB="B", algorithm=lpMatcher.Method.PULP)[1]
        self.assertTrue((np.array([[0, 0], [1, 1], [2, 2]]) == result[RESULT_IDX]).all())

    def test_moreB(self):
        algorithm = LpMatcher()
        algorithm.trimCost = False

        seq = Sequence([Event('A', 73), Event('A', 82),
                        Event('B', 109), Event('B', 149), Event('B', 169)], 5)

        result = algorithm.match(sequence=seq, eventA="A", eventB="B", algorithm=lpMatcher.Method.PULP)[1]
        self.assertTrue((np.array([[0, 0], [1, 2]]) == result[RESULT_IDX]).all())

    def test_moreA(self):
        algorithm = LpMatcher()
        algorithm.trimCost = False

        seq = Sequence([Event('A', 34), Event('A', 73), Event('A', 82),
                        Event('B', 109), Event('B', 149)], 5)

        result = algorithm.match(sequence=seq, eventA="A", eventB="B", algorithm=lpMatcher.Method.PULP)[1]
        self.assertTrue((np.array([[1, 0], [2, 1]]) == result[RESULT_IDX]).all())

if __name__ == '__main__':
    unittest.main()
