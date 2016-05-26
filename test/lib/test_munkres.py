import unittest

import numpy as np

from lib.munkres import Munkres


class TestScript(unittest.TestCase):
    def setUp(self):
        self.m = Munkres()

    @staticmethod
    def calcTotalCost(indexes, cost_matrix):
        total_cost = 0
        for r, c in indexes:
            x = cost_matrix[r][c]
            total_cost += x
        return total_cost

    def test_square1(self):
        c = [[400, 150, 400],
             [400, 450, 600],
             [300, 225, 300]]
        res = self.m.compute(c)
        self.assertEqual(850, self.calcTotalCost(res, c))

    def test_square2(self):
        c = np.array([[10, 10, 8],
                      [9, 8, 1],
                      [9, 7, 4]])
        res = self.m.compute(c)
        self.assertEqual(18, self.calcTotalCost(res, c))

    def test_rectangular1(self):
        c = [[400, 150, 400, 1],
             [400, 450, 600, 2],
             [300, 225, 300, 3]]
        res = self.m.compute(c)
        self.assertEqual(452, self.calcTotalCost(res, c))

    def test_rectangular2(self):
        c = np.array([[10, 10, 8, 11],
                      [9, 8, 1, 1],
                      [9, 7, 4, 10]])
        res = self.m.compute(c)
        self.assertEqual(15, self.calcTotalCost(res,c ))


if __name__ == '__main__':
    unittest.main()
