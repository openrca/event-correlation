import math
import shutil

import numpy as np

from algorithms import Matcher


class MarcoMatcher(Matcher):
    def __init__(self):
        super().__init__(__name__)
        self.sequence = None
        self.eventA = None
        self.eventB = None
        self.algorithm = None

        self.a = None
        self.b = None
        self.A = None
        self.Aeq = None
        self.delta = None

    def parseArgs(self, kwargs):
        self.sequence = kwargs["sequence"]
        self.eventA = kwargs["eventA"]
        self.eventB = kwargs["eventB"]
        if (kwargs["algorithm"] == "quadprog"):
            self.algorithm = self.solveQuadProg
        elif (kwargs["algorithm"] == "cpl"):
            self.algorithm = self.solveCPL
        elif (kwargs["algorithm"] == "slsqp"):
            self.algorithm = self.solveSLSQP
        else:
            raise ValueError("No algorithm specified.")

    def calculateMeanVar(self, z):
        Z = np.reshape(z, (len(self.a), len(self.b)))
        [A, B] = np.meshgrid(self.a, self.b)
        delta = B - A

        mean = 1 / len(self.b) * np.sum(np.multiply(Z, delta))

        var = 1 / (len(self.b) - 1) * np.sum(np.multiply(Z, (delta.T - mean) ** 2))
        return (mean, var)

    def match(self, **kwargs):
        self.parseArgs(kwargs)

        self.a = self.sequence.asVector(self.eventA)
        self.b = self.sequence.asVector(self.eventB)

        na = len(self.a)
        nb = len(self.b)

        z_0 = np.repeat(1 / na * np.ones(na), nb)

        [TA, TB] = np.meshgrid(self.a, self.b)
        self.delta = TB - TA
        self.A = -np.diag(self.delta.reshape(-1))

        self.Aeq = np.kron(np.eye(nb), np.ones(na))

        Z = self.algorithm(z_0, na, nb)

        idx = Z.argmax(axis=1)
        approxZ = np.zeros(Z.shape)
        approxZ[np.arange(idx.size), idx] = 1

        print("Approximation:")
        print(approxZ)
        mu, var = self.calculateMeanVar(approxZ)
        return {"Mu": mu, "Sigma": math.sqrt(var)}

    def solveQuadProg(self, z, na, nb):
        from pymatbridge import Matlab

        if (shutil.which("matlab") is None):
            raise RuntimeError("Matlab not found. Please ensure that Matlab is in the path.")

        self.logger.debug("Connecting to Matlab")
        matlab = Matlab()
        matlab.start()

        A = self.A
        b = np.zeros(na * nb)

        # one to one matching
        A = np.concatenate((A, np.tile(np.eye(na), nb)))
        b = np.concatenate((b, np.ones(na)))

        matlab.set_variable("z", z.T)
        matlab.set_variable("A", A)
        matlab.set_variable("b", b.T)

        matlab.set_variable("Aeq", self.Aeq)
        matlab.set_variable("beq", np.ones(nb).T)
        matlab.set_variable("lb", np.zeros(na * nb).T)
        matlab.set_variable("ub", np.ones(na * nb).T)
        matlab.set_variable("f", self.delta.flatten() ** 2 / (na - 1))

        matlab.run_code("[z_opt, val] = quadprog([], f, A, b, Aeq, beq, lb, ub, z);")
        z_opt = matlab.get_variable("z_opt")
        matlab.stop()
        self.logger.debug("Closing connection to Matlab")
        return np.reshape(z_opt, (na, nb))

    def solveSLSQP(self, z, na, nb):
        """ Solve the optimization problem using scipy.optimize.minimize().

        Does not converge for sequences with more than ~30 events.
        """
        import scipy.optimize

        res = scipy.optimize.minimize(self._costFunctionSLSQP, z, method='SLSQP', constraints=(
            # Constraints can be formulated as equality ('eq') to 0 or inequality ('ineq') >= 0
            {'type': 'ineq', 'fun': lambda x: -self.A.dot(x)},
            {'type': 'eq', 'fun': lambda x: self.Aeq.dot(x) - 1}
        ), bounds=((0, 1),) * z.size, options={"disp": True})
        print(res)
        return np.reshape(res.x, (na, nb))

    def _costFunctionSLSQP(self, z):
        return self.calculateMeanVar(z)[0]

    def solveCPL(self, z, na, nb):
        """ Solve the optimization problem using cvxpot.solvers.cpl().

        Not working yet!
        """
        raise RuntimeError("Not working yet")

        # noinspection PyUnreachableCode
        from cvxopt import matrix
        import cvxopt.solvers

        [A, B] = np.meshgrid(self.a, self.b)
        delta = B - A
        var, mean = self.calculateMeanVar(z)

        c = (delta - mean) ** 2 / (na - 1)
        c = matrix(c.reshape(na * nb, 1))

        h = np.zeros(na * nb)
        b = np.ones(na * nb)

        res = cvxopt.solvers.cpl(c=c, F=self.F, options={"debug": True})  # , G=self.A, h=h, A=self.Aeq, b=b)
        print(res)
        return res

    def F(self, x=None, z=None):
        from cvxopt import matrix

        na = len(self.a)
        nb = len(self.b)

        if x is None:
            return 0, matrix(np.repeat(1 / na * np.ones(na), nb))
