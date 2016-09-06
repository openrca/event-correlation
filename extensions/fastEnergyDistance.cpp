#include <algorithm>
#include <cmath>
#include <ctime>
#include <vector>
#include <Python.h>

static double computeSum(std::vector<double> &eventA, std::vector<double> & eventB) {
    double sum = 0;
    for(std::vector<double>::iterator it = eventA.begin(); it != eventA.end(); ++it) {
        for(std::vector<double>::iterator it2 = eventB.begin(); it2 != eventB.end(); ++it2)
            sum += std::abs(*it2 - *it);
    }
    return sum / (eventA.size() * eventB.size());
}

static double computeUnNormalized(std::vector<double> &eventA, std::vector<double> & eventB) {
    double A = computeSum(eventA, eventB);
    double B = computeSum(eventA, eventA);
    double C = computeSum(eventB, eventB);
    return 2 * A - B - C;
}

static inline double computeTestStatistic(std::vector<double> &eventA, std::vector<double> & eventB) {
    return (eventA.size() * eventB.size()) / (eventA.size() + eventB.size()) * computeUnNormalized(eventA, eventB);
}

static double computeMultivariateTest(std::vector<double> &eventA, std::vector<double> & eventB) {
    double value = 0;
    value += computeTestStatistic(eventA, eventA);
    value += computeTestStatistic(eventA, eventB);
    value += computeTestStatistic(eventB, eventA);
    value += computeTestStatistic(eventB, eventB);
    return value;
}

static double computePValue(std::vector<double> &eventA, std::vector<double> &eventB, int n) {
    std::srand(unsigned(std::time(0)));

    double p = 0;
    double ref = computeMultivariateTest(eventA, eventB);

    std::vector<double> allEvents(eventA);
    allEvents.insert(allEvents.end(), eventB.begin(), eventB.end());
    for (int i = 0; i < n; ++i) {
        std::random_shuffle(allEvents.begin(), allEvents.end());

        std::vector<double> splitLow(allEvents.begin(), allEvents.begin() + eventA.size());
        std::vector<double> splitHigh(allEvents.begin() + eventA.size(), allEvents.end());

        double v = computeMultivariateTest(splitLow, splitHigh);
        if (ref > v)
            ++p;
    }
    return (p + 1) / (n + 1);
}

static void pyobjectToVector(std::vector<double> &vector, PyObject* obj, int size) {
    vector.reserve(size);

    PyObject *iter = PyObject_GetIter(obj);
    for(int i = 0; i < size; ++i) {
        PyObject *next = PyIter_Next(iter);
        if (!next)
            break;
        vector.push_back(PyFloat_AsDouble(next));
    }
}


static PyObject* compute(PyObject *self, PyObject *args) {
    PyObject* arg0;
    PyObject* arg1;
    int sizeA = 0;
    int sizeB = 0;
    int n = 0;

    if (!PyArg_ParseTuple(args, "OOiii", &arg0, &arg1, &sizeA, &sizeB, &n))
        return NULL;

    std::vector<double> eventA;
    pyobjectToVector(eventA, arg0, sizeA);
    std::vector<double> eventB;
    pyobjectToVector(eventB, arg1, sizeB);

    double score = computeUnNormalized(eventA, eventB) / (2 * computeSum(eventA, eventB));
    double p = computePValue(eventA, eventB, n);

    PyObject* res = Py_BuildValue("dd", score, p);
    return res;
}

static PyMethodDef fastEnergyDistanceMethods[] = {
    {"compute", compute, METH_VARARGS, "Run energy distance algorithm"},
    {NULL, NULL, 0, NULL}
};


static struct PyModuleDef fastEnergyDistanceModule = {
    PyModuleDef_HEAD_INIT, "fastEnergyDistance", "C implementation of energy distance", -1, fastEnergyDistanceMethods
};


PyMODINIT_FUNC PyInit_fastEnergyDistance(void) {
    return PyModule_Create(&fastEnergyDistanceModule);
}
