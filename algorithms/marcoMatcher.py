import shutil
from enum import Enum

import numpy as np

from algorithms import Matcher, RESULT_MU, RESULT_SIGMA, RESULT_KDE, RESULT_IDX
from core.distribution import KdeDistribution


class Method(Enum):
    MATLAB = "matlab"
    SCIPY = "scipy"
    CVXOPT = "cvxopt"
    PULP = "pulp"


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
                pulp
            All these values are also defined in marcoMatcher.Method
        """
        algorithm = kwargs["algorithm"]
        if (algorithm == Method.MATLAB or algorithm == Method.SCIPY or algorithm == Method.CVXOPT or
                    algorithm == Method.PULP):
            self.algorithm = algorithm
        else:
            raise ValueError("No algorithm specified.")

    # noinspection PyUnboundLocalVariable, PyTypeChecker
    def compute(self):
        eventA = self.sequence.asVector(self.eventA)
        eventB = self.sequence.asVector(self.eventB)

        na = len(eventA)
        nb = len(eventB)

        [TA, TB] = np.meshgrid(eventA, eventB)
        delta = TB - TA

        if (self.algorithm is not Method.PULP):
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

        Z = None
        if (self.algorithm == Method.PULP):
            Z = self.solvePulp(f, -delta.reshape(-1), na, nb)
        elif (self.algorithm == Method.MATLAB):
            Z = self.solveMatlab(f, A, b, Aeq, beq, na, nb)
        elif (self.algorithm == Method.SCIPY):
            Z = self.solveScipy(f, A, b, Aeq, beq, na * nb)
        elif (self.algorithm == Method.CVXOPT):
            Z = self.solveCvxopt(f, A, b, Aeq, beq, na * nb)

        tmp = np.reshape(Z, (nb, na))
        idx = tmp.argmax(axis=1)
        Z = np.zeros(tmp.shape)
        Z[np.arange(idx.size), idx] = 1
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
        """ Solve the optimization problem with Matlabs linprog """

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

        matlab.run_code("[z_opt, val] = linprog(f, A, b, Aeq, beq, lb, ub, z);")
        z_opt = matlab.get_variable("z_opt")
        matlab.stop()
        self.logger.debug("Closing connection to Matlab")
        return z_opt

    def solveScipy(self, f, A, b, Aeq, beq, n):
        """ Solve the optimization problem using scipy.optimize.linprog().

        Performance highly depends on the maximum number of iterations
        """
        import scipy.optimize

        self.logger.debug("Using scipy to solve optimization problem")
        res = scipy.optimize.linprog(f, A, b, Aeq, beq, bounds=((0, 1),) * n,
                                     options={"disp": True,
                                              "bland": True,
                                              "tol": 1e-12,
                                              "maxiter": 5000})
        if (not res.success):
            self.logger.warn("Unable to find solution: {}. Results may be bad.".format(res.message))

        return res.x

    def solveCvxopt(self, f, A, b, Aeq, beq, n):
        """ Solve the optimization problem using cvxopt.solvers.cpl().

        Works for higher dimensions but requires quite some time.
        """
        from cvxopt import matrix, solvers

        # add boundaries as lp has no build-in boundaries
        A1 = np.concatenate((A, -np.eye(n), np.eye(n)))
        b1 = np.concatenate((b, np.zeros(n), np.ones(n)))

        self.logger.debug("Using cvxopt to solve optimization problem")
        sol = solvers.lp(matrix(f), matrix(A1), matrix(b1), matrix(Aeq), matrix(beq), solver="glpk")

        if (sol["x"] is None):
            self.logger.warn("Unable to find solution")
            return np.zeros(n)

        return sol["x"]

    def solvePulp(self, f, A, na, nb):
        """ Solve the problem by formulating it as a CPLEX LP problem.

        CPLEX LP (http://lpsolve.sourceforge.net/5.0/CPLEX-format.htm) is a format for formulating sparse problems.
        """

        from pulp.pulp import LpAffineExpression, LpMinimize, LpProblem, LpVariable
        problem = LpProblem("test1", LpMinimize)
        template = "x{0:0" + str(len(str(na * nb))) + "d}"

        variables = [None] * (na * nb)
        objective = {}
        for i in range(na * nb):
            var = LpVariable(template.format(i), 0, 1)
            variables[i] = var
            objective[var] = f[i]
            problem.addConstraint(A[i] * var <= 0)

        problem.setObjective(LpAffineExpression(objective))

        if (na >= nb):
            for j in range(nb):
                oneToOneConstraint = {}
                for i in np.arange(j, na * nb, na):
                    oneToOneConstraint[variables[i]] = 1
                problem.addConstraint(LpAffineExpression(oneToOneConstraint) <= 1)

        for i in range(na):
            onlyOneConstraint = {}
            for j in range(i * nb, (i + 1) * nb):
                onlyOneConstraint[variables[j]] = 1
            problem.addConstraint(LpAffineExpression(onlyOneConstraint) == 1)

        self.logger.debug("Starting to solve with glpk")
        problem.solve()

        result = np.zeros(na * nb)
        for i, v in enumerate(problem.variables()):
            result[i] = v.varValue
        return result
