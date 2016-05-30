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

    def parseArgs(self, kwargs):
        self.sequence = kwargs["sequence"]
        self.eventA = kwargs["eventA"]
        self.eventB = kwargs["eventB"]
        if (kwargs["algorithm"] == "fmincon"):
            self.algorithm = self.solveFMinCon
        elif (kwargs["algorithm"] == "cpl"):
            self.algorithm = self.solveCPL
        else:
            self.algorithm = self.solveSLSQP

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

        # self.a = np.array([12.6987, 63.2359, 81.4724, 90.5792, 91.3376])
        # self.b = np.array([20.0833, 72.3687, 92.1576, 107.7360, 106.8765])

        na = len(self.a)
        nb = len(self.b)

        z_0 = np.repeat(1 / na * np.ones(na), nb)

        [TA, TB] = np.meshgrid(self.a, self.b)
        delta = (TB - TA)
        self.A = -np.diag(delta.reshape(-1))

        # one to one matching
        # A = np.concatenate((A, np.tile(np.eye(na), nb)))
        # b = np.concatenate((b, np.ones(na)))

        self.Aeq = np.kron(np.eye(nb), np.ones(na))

        Z = self.algorithm(z_0, na, nb)

        idx = Z.argmax(axis=1)
        approxZ = np.zeros(Z.shape)
        approxZ[np.arange(idx.size), idx] = 1

        print("Approximation:")
        print(approxZ)
        mu, var = self.calculateMeanVar(approxZ)
        return {"Mu": mu, "Sigma": math.sqrt(var)}

    def solveFMinCon(self, z, na, nb):
        from pymatbridge import Matlab

        if (shutil.which("matlab") is None):
            raise RuntimeError("Matlab not found. Please ensure that Matlab is in the path.")

        self.logger.debug("Connecting to Matlab")
        matlab = Matlab()
        matlab.start()
        matlab.set_variable("z", z.T)
        matlab.set_variable("ta", self.a)
        matlab.set_variable("tb", self.b)
        matlab.set_variable("A", self.A)
        matlab.set_variable("b", np.zeros(na * nb).T)
        matlab.set_variable("Aeq", self.Aeq)
        matlab.set_variable("beq", np.ones(nb).T)
        matlab.set_variable("lb", np.zeros(na * nb).T)
        matlab.set_variable("ub", np.ones(na * nb).T)
        matlab.run_code("fun = @(z)cost_function(z, ta, tb, 'var');")

        matlab.run_code(
            "[z_opt, val] = fmincon(fun, z, A, b, Aeq, beq, lb, ub, [], optimoptions('fmincon', 'MaxFunEvals', 1e5));")
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
