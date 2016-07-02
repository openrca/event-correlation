import shutil

import numpy as np

from algorithms import Matcher, RESULT_MU, RESULT_SIGMA, RESULT_KDE, RESULT_IDX
from core.distribution import KdeDistribution


class MarcoMatcher(Matcher):
    def __init__(self):
        super().__init__(__name__)
        self.algorithm = None

    def parseArgs(self, kwargs):
        """
        Additional parameters:
            algorithm: Defines the algorithm to solve the optimization problem. Allowed values are
                matlab (requires Matlab and pymatbridge)
                cvxopt (requires cvxopt with glpk support)
                scipy
        """
        if (kwargs["algorithm"] == "matlab"):
            self.algorithm = self.solveMatlab
        elif (kwargs["algorithm"] == "scipy"):
            self.algorithm = self.solveScipy
        elif (kwargs["algorithm"] == "cvxopt"):
            self.algorithm = self.solveCvxopt
        else:
            raise ValueError("No algorithm specified.")

    def compute(self):
        eventA = self.sequence.asVector(self.eventA)
        eventB = self.sequence.asVector(self.eventB)

        na = len(eventA)
        nb = len(eventB)

        [TA, TB] = np.meshgrid(eventA, eventB)
        delta = TB - TA
        A = -np.diag(delta.reshape(-1))
        b = np.zeros(na * nb)

        # one to one matching
        if (na >= nb):
            A = np.concatenate((A, np.tile(np.eye(na), (1, nb))))
            b = np.concatenate((b, np.ones(na)))
        # TODO what happens if na < nb?

        Aeq = np.kron(np.eye(nb), np.ones(na))
        beq = np.ones(nb)

        f = delta.flatten() ** 2 / (na - 1)

        Z = self.algorithm(f, A, b, Aeq, beq, na, nb)

        self.logger.trace("Final (approximated) result: \n {}".format(Z.argmax(axis=0)))

        cost = np.multiply(Z, delta)
        cost[cost == 0] = cost.max() + 1
        if (na < nb):
            idx = cost.argmin(axis=0)
            idx = np.column_stack((np.arange(idx.size), idx))
            cost = cost.min(axis=0)
        else:
            idx = cost.argmin(axis=1)
            idx = np.column_stack((idx, np.arange(idx.size)))
            cost = cost.min(axis=1)

        return {RESULT_MU: cost.mean(), RESULT_SIGMA: cost.std(), RESULT_KDE: KdeDistribution(cost), RESULT_IDX: idx}

    def solveMatlab(self, f, A, b, Aeq, beq, na, nb):
        from pymatbridge import Matlab

        if (shutil.which("matlab") is None):
            raise RuntimeError("Matlab not found. Please ensure that Matlab is in the path.")

        self.logger.debug("Connecting to Matlab")
        matlab = Matlab()
        matlab.start()

        z = np.repeat(1 / na * np.ones(na), nb)

        matlab.set_variable("f", f)
        matlab.set_variable("A", A)
        matlab.set_variable("b", b)
        matlab.set_variable("Aeq", Aeq)
        matlab.set_variable("beq", beq)
        matlab.set_variable("lb", np.zeros(na * nb))
        matlab.set_variable("ub", np.ones(na * nb))
        matlab.set_variable("z", z)

        matlab.run_code("[z_opt, val] = quadprog([], f, A, b, Aeq, beq, lb, ub, z);")
        z_opt = matlab.get_variable("z_opt")
        matlab.stop()
        self.logger.debug("Closing connection to Matlab")
        return np.reshape(z_opt, (nb, na))

    def solveScipy(self, f, A, b, Aeq, beq, na, nb):
        """ Solve the optimization problem using scipy.optimize.linprog().

        Performance highly depends on the maximum number of iterations
        """
        import scipy.optimize

        self.logger.debug("Using scipy to solve optimization problem")
        res = scipy.optimize.linprog(f, A, b, Aeq, beq, bounds=((0, 1),) * na * nb,
                                     options={"disp": True,
                                              "bland": True,
                                              "tol": 1e-12,
                                              "maxiter": 5000})
        if (not res.success):
            self.logger.warn("Unable to find solution: {}. Results may be bad.".format(res.message))

        return np.reshape(res.x, (nb, na))

    def solveCvxopt(self, f, A, b, Aeq, beq, na, nb):
        """ Solve the optimization problem using cvxopt.solvers.cpl().

        Works for higher dimensions but requires quite some time.
        """
        from cvxopt import matrix, solvers

        # add boundaries as lp has no build-in boundaries
        A1 = np.concatenate((A, -np.eye(na * nb), np.eye(na * nb)))
        b1 = np.concatenate((b, np.zeros(na * nb), np.ones(na * nb)))

        self.logger.debug("Using cvxopt to solve optimization problem")
        sol = solvers.lp(matrix(f), matrix(A1), matrix(b1), matrix(Aeq), matrix(beq), solver="glpk")

        if (sol["x"] is None):
            self.logger.warn("Unable to find solution")
            return np.zeros((nb, na))

        return np.reshape(sol["x"], (nb, na))
