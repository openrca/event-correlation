#include <stdlib.h>
#include <algorithm>
#include <cmath>
#include <iostream>
#include <Python.h>
#include <limits>


const static double PI = 3.141592653589793238463;

struct Result {
    double mu;
    double std;
    double likelihood;
    PyObject *idx;
};


PyObject* parseAssignments(double **r, int sizeA, int sizeB) {
    PyObject *list = PyList_New(0);

    for (int i = 0; i < sizeA; ++i) {
        double max = 0;
        int idx = -1;
        for (int j = 0; j < sizeB; ++j) {
            if (r[i][j] > max) {
                max = r[i][j];
                idx = j;
            }
        }
        if (idx >= 0) {
            PyObject *list2 = PyList_New(2);
            PyList_SetItem(list2, 0, PyLong_FromLong(i));
            PyList_SetItem(list2, 1, PyLong_FromLong(idx));

            PyList_Append(list, list2);
        }
    }
    return list;
}

static int findClosest(double *a, int sizeA, double t) {
    double dist = std::numeric_limits<double>::max();
    int idx = -1;
    for (int i = 0; i < sizeA; ++i) {
        if (std::abs(a[i] - t) < dist) {
            dist = std::abs(a[i] - t);
            idx = i;
        }
    }
    return idx;
}

static int* greedyBound(double *a, int sizeA, double **r, int j, double b, double mu, double epsilon) {
    double t = b - mu;
    int i = findClosest(a, sizeA, t);

    int min = i;
    int max = i;

    double prob = 0;
    while (prob < 1 - epsilon) {
        if (min == 0 && max == sizeA - 1)
            break;

        if (min == 0) {
            i = max + 1;
            max = i;
        }
        else if (max == sizeA - 1) {
            i = min - 1;
            min = i;
        }
        else if (r[std::max(0, min - 1)][j] >= r[std::min(sizeA - 1, max + 1)][j]) {
            i = std::max(0, min - 1);
            min = i;
        }
        else {
            i = std::min(sizeA - 1, max + 1);
            max = i;
        }
        prob += r[i][j];
    }

    int *res = new int[2];
    res[0] = min;
    res[1] = max;
    return res;
}

static double** computeNormalMatrix(double* a, double* b, double** r, double mu, double variance, int sizeA, int sizeB) {
    double** result = new double*[sizeA];
    double scalar = 1 / std::sqrt(2 * PI * variance);
    
    for (int i = 0; i < sizeA; ++i) {
        result[i] = new double[sizeB];
        for (int j = 0; j < sizeB; ++j)
            result[i][j] = r[i][j] * scalar * std::exp( -((b[j] - a[i] - mu) * (b[j] - a[i] - mu)) / (2 * variance));
    }
    return result;
}


static void expectation(double* a, double* b, double** r, int j, int min, int max, double mu, double variance, int sizeA, int sizeB) {
    double** tmp = computeNormalMatrix(a, b, r, mu, variance, sizeA, sizeB);

    for (int i = min; i < max; ++i) {
        double sum = 0;
        for (int k = 0; k < sizeB; ++k)
            sum += tmp[i][k];
        if (sum != 0)
            r[i][j] = tmp[i][j] / sum;
        else
            r[i][j] = 0;
    }

    for (int i = 0; i < sizeA; ++i)
        delete[] tmp[i];
    delete[] tmp;
}


static double* maximization(double* a, double* b, double** r, int sizeA, int sizeB) {
    double mu = 0;
    for (int i = 0; i < sizeA; ++i) {
        for (int j = 0; j < sizeB; ++j) {
            double dist = b[j] - a[i];
            mu += dist * r[i][j];
        }
    }
    mu /= sizeA;
    
    double var = 0;
    for (int i = 0; i < sizeA; ++i) {
        for (int j = 0; j < sizeB; ++j) {
            double dist = b[j] - a[i];
            var += (dist - mu) * (dist - mu) * r[i][j];
        }
    }
    var /= sizeA;
    
    double* result = new double[2];
    result[0] = mu;
    result[1] = var;
    return result;
}


static Result* compute(double* a, double* b, double initMu, double initVariance, int sizeA, int sizeB) {
    double** r = new double*[sizeA];
    for (int i = 0; i < sizeA; ++i) {
        r[i] = new double[sizeB];
        for (int j = 0; j < sizeB; ++j)
            r[i][j] = 1.0 / sizeB;
    }
    double mu = initMu;
    double var = initVariance;
    double epsilon = 0.2;

    while (true) {
        for (int j = 0; j < sizeB; ++j) {
//            int *bounds = greedyBound(a, sizeA, r, j, b[j], mu, epsilon);
//            expectation(a, b, r, j, bounds[0], bounds[1], mu, var, sizeA, sizeB);
            expectation(a, b, r, j, 0, sizeA, mu, var, sizeA, sizeB);
//            delete[] bounds;
        }
        double* result = maximization(a, b, r, sizeA, sizeB);
        double newMu = result[0];
        double newVar = result[1];
        delete[] result;
        
        double deltaMu = std::abs(mu - newMu);
        double deltaVar = std::abs(var - newVar);
        mu = newMu;
        var = newVar;

        if (mu != mu || var != var) {
            std::cout << "Numerical problems: Mu or Var is NaN. Aborting calculation" << std::endl;
            break;
        }
        
        if (deltaMu < 1e-2 && deltaVar < 1e-2)
            break;
    }
    
    double likelihood = 0;
    double** tmp = computeNormalMatrix(a, b, r, mu, var, sizeA, sizeB);
    for (int j = 0; j < sizeB; ++j) {
        double sum = 0;
        for (int i = 0; i < sizeA; ++i)
            sum += tmp[i][j];
        likelihood += std::log(sum);
    }

    struct Result *returnValue = new Result;
    returnValue->mu = mu;
    returnValue->std = std::sqrt(var);
    returnValue->likelihood = likelihood;
    returnValue->idx = parseAssignments(r, sizeA, sizeB);
    
    for(int i = 0; i < sizeA; ++i) {
        delete[] r[i];
        delete[] tmp[i];
    }
    delete[] r;
    delete[] tmp;
    return returnValue;
}


double* pyobjectToArray(PyObject* obj, int size) {
    double* array = new double[size];
    
    PyObject *iter = PyObject_GetIter(obj);
    for(int i = 0; i < size; ++i) {
        PyObject *next = PyIter_Next(iter);
        if (!next)
            break;
        array[i] = PyFloat_AsDouble(next);
    }
    return array;
}


static PyObject* fastLagEM(PyObject *self, PyObject *args) {
    int sizeA = 0;
    int sizeB = 0;
    double initMu;
    double initVar;
    PyObject* arg0;
    PyObject* arg1;
    
    if (!PyArg_ParseTuple(args, "OOddii", &arg0, &arg1, &initMu, &initVar, &sizeA, &sizeB))
    return NULL;
    
    double* a = pyobjectToArray(arg0, sizeA);
    double* b = pyobjectToArray(arg1, sizeB);

    Result* result = compute(a, b, initMu, initVar, sizeA, sizeB);
    PyObject* res = Py_BuildValue("dddO", result->mu, result->std, result->likelihood, result->idx);

    delete result;
    delete[] a;
    delete[] b;

    return res;
}


static PyMethodDef fastLagEMMethods[] = {
    {"compute", fastLagEM, METH_VARARGS, "Run lagEM algorithm"},
    {NULL, NULL, 0, NULL}
};


static struct PyModuleDef fastLagEMModule = {
    PyModuleDef_HEAD_INIT, "fastLagEM", "C implementation of lagEM", -1, fastLagEMMethods
};


PyMODINIT_FUNC PyInit_fastLagEM(void) {
    return PyModule_Create(&fastLagEMModule);
}
