#include <stdlib.h>
#include <cmath>
#include <iostream>
#include <Python.h>


const static double PI = 3.141592653589793238463;

static double** calculateNormalMatrix(double* a, double* b, double** r, double mu, double variance, int sizeA, int sizeB) {
    double** result = new double*[sizeA];
    double scalar = 1 / std::sqrt(2 * PI * variance);
    
    for (int i = 0; i < sizeA; ++i) {
        result[i] = new double[sizeB];
        for (int j = 0; j < sizeB; ++j)
            result[i][j] = r[i][j] * scalar * std::exp( -((b[j] - a[i] - mu) * (b[j] - a[i] - mu)) / (2 * variance));
    }
    return result;
}


static void expectation(double* a, double* b, double** r, double mu, double variance, int sizeA, int sizeB) {
    double** tmp = calculateNormalMatrix(a, b, r, mu, variance, sizeA, sizeB);
    
    for (int i = 0; i < sizeA; ++i) {
        for (int j = 0; j < sizeB; ++j) {
            double sum = 0;
            for (int k = 0; k < sizeB; ++k)
                sum += tmp[i][k];
            r[i][j] = tmp[i][j] / sum;
        }
    }
    
    for (int i = 0; i < sizeA; ++i) {
        delete[] tmp[i];
    }
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


static double* calculate(double* a, double* b, double initMu, double initVariance, int sizeA, int sizeB) {
    double** r = new double*[sizeA];
    for (int i = 0; i < sizeA; ++i) {
        r[i] = new double[sizeB];
        for (int j = 0; j < sizeB; ++j)
            r[i][j] = 1.0 / sizeB;
    }
    double mu = initMu;
    double var = initVariance;
    
    
    while (true) {
        expectation(a, b, r, mu, var, sizeA, sizeB);
        double* result = maximization(a, b, r, sizeA, sizeB);
        double newMu = result[0];
        double newVar = result[1];
        delete[] result;
        
        double deltaMu = std::abs(mu - newMu);
        double deltaVar = std::abs(var - newVar);
        mu = newMu;
        var = newVar;
        
        if (deltaMu < 1e-2 && deltaVar < 1e-2)
            break;
    }
    
    double likelihood = 1;
    double** tmp = calculateNormalMatrix(a, b, r, mu, var, sizeA, sizeB);
    for (int j = 0; j < sizeB; ++j) {
        double sum = 0;
        for (int i = 0; i < sizeA; ++i)
            sum += tmp[i][j];
        likelihood *= sum;
    }
    
    for(int i = 0; i < sizeA; ++i) {
        delete[] r[i];
        delete[] tmp[i];
    }
    delete[] r;
    delete[] tmp;
    
    
    double* result = new double[3];
    result[0] = mu;
    result[1] = std::sqrt(var);
    result[2] = likelihood;
    return result;
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
    
    double* result = calculate(a, b, initMu, initVar, sizeA, sizeB);
    PyObject* res = Py_BuildValue("ddd", result[0], result[1], result[2]);
    
    delete[] result;
    delete[] a;
    delete[] b;
    
    return res;
}


static PyMethodDef fastLagEMMethods[] = {
    {"calculate", fastLagEM, METH_VARARGS, "Run lagEM algorithm"},
    {NULL, NULL, 0, NULL}
};


static struct PyModuleDef fastLagEMModule = {
    PyModuleDef_HEAD_INIT, "fastLagEM", "C implementation of lagEM", -1, fastLagEMMethods
};


PyMODINIT_FUNC PyInit_fastLagEM(void) {
    return PyModule_Create(&fastLagEMModule);
}
