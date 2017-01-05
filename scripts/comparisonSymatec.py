import matplotlib.pyplot as plt

from visualization import CORRECT, ICP, LP, LAGEM, plotDistributions

correlation66_65 = {
    CORRECT: [1.23, 1.82, 2.02, 2.87, 6.56, 13.87, 18.19, 19.31, 20.33, 25.2, 35.96, 35.97, 35.97, 35.98, 35.98, 35.98,
              35.98, 35.98, 35.98, 35.99, 35.99, 35.99, 36.19, 36.52, 36.52, 36.59, 37.78],
    LP: [1.23, 1.82, 2.02, 2.87, 6.56, 13.87, 18.19, 19.31, 20.33, 25.2, 35.96, 35.97, 35.97, 35.98, 35.98, 35.98,
         35.98, 35.98, 35.98, 35.99, 35.99, 35.99, 36.19, 36.52, 36.52, 36.59, 37.78],
    ICP: [1.23, 1.82, 2.02, 2.87, 6.56, 13.87, 18.19, 19.31, 20.33, 25.2, 35.96, 35.97, 35.97, 35.98, 35.98, 35.98,
          35.98, 35.98, 35.98, 35.99, 35.99, 35.99, 36.19, 36.52, 36.52, 36.59, 37.78],
    LAGEM: [19.125, 12.9365]
}

correlation34054_34057 = {
    CORRECT: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              0.00999999977648],
    LP: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    ICP: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
          0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    LAGEM: [-1.4085e-04, 1.1784e-03]
}

correlation7_66 = {
    CORRECT: [15.08, 16.63, 17.62, 19.78, 28.58, 42.85, 50.37, 50.39, 53.65, 54.13, 54.66, 59.36, 65.67, 68.27, 72.66,
              87.61, 89.09, 90.64, 91.57, 93.74, 94.49, 96.35, 280.82, 442.09, 840.24],
    LP: [15.08, 16.63, 17.62, 19.78, 28.58, 42.85, 50.37, 50.39, 53.65, 54.13, 54.66, 59.36, 65.67, 68.27, 72.66, 87.61,
         89.09, 90.64, 91.57, 93.74, 94.49, 96.35, 280.82, 442.09, 840.24, 1098.99, 1124.59, 1710.95],
    ICP: [-91.85, -34.84, -19.71, -18.64, -13.92, -13.22, -12.81, -8.48, -7.87, -7.56, -4.57, 15.08, 16.63, 17.62,
          28.58, 42.85, 50.37, 50.39, 53.65, 65.67, 68.27, 69.32, 72.66, 89.09, 89.52, 90.64, 91.26, 91.57, 93.74,
          94.02, 94.49, 96.35, 96.94, 280.82],
    LAGEM: [2.3066, 59.0427]
}

correlation202_200 = {
    CORRECT: [0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.01, 0.01, 0.01, 0.01],
    ICP: [-0.07, -0.03, -0.02, -0.02, -0.01, -0.01, -0.01, -0.01, -0.01, -0.01, -0.01, -0.01, -0.01, -0.01, -0.01,
          -0.01, -0.01, -0.01, -0.01, -0.01, -0.01, -0.01, -0.01, -0.01, -0.01, -0.01, -0.01, -0.01, -0.01, -0.01,
          -0.01, -0.01, -0.01, -0.01, -0.01, -0.01, -0.01, -0.01, -0.01, -0.01, -0.01, -0.01, -0.01, -0.01, -0.01,
          -0.01, -0.01, -0.01, -0.01, -0.01, -0.01, -0.01, -0.01, -0.01, -0.01, -0.01, -0.01, -0.01, -0.01, -0.01,
          -0.01, -0.01, -0.01, -0.01, -0.01, -0.01, -0.01, -0.01, -0.01, 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
          0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
          0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
          0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
          0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
          0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
          0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
          0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
          0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
          0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
          0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
          0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
          0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
          0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
          0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
          0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
          0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
          0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
          0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
          0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
          0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
          0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
          0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
          0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
          0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
          0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
          0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
          0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
          0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
          0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
          0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
          0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
          0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
          0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
          0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
          0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.01, 0.01, 0.01, 0.01,
          0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01,
          0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01,
          0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.02, 0.02, 0.02, 0.02, 0.02,
          0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.03, 0.03, 0.03, 0.03,
          0.04, 0.04, 0.04, 0.04, 0.05, 0.05, 0.06],
    LP: [0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00,
         0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00,
         0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00,
         0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00,
         0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00,
         0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00,
         0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00,
         0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00,
         0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00,
         0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00,
         0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00,
         0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00,
         0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00,
         0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00,
         0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00,
         0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00,
         0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00,
         0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00,
         0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00,
         0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00,
         0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00,
         0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00,
         0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00,
         0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 1.0000e-02,
         1.0000e-02, 1.0000e-02, 1.0000e-02, 1.0000e-02, 1.0000e-02, 1.0000e-02, 1.0000e-02, 1.0000e-02, 1.0000e-02,
         1.0000e-02, 1.0000e-02, 1.0000e-02, 1.0000e-02, 1.0000e-02, 1.0000e-02, 1.0000e-02, 1.0000e-02, 1.0000e-02,
         1.0000e-02, 1.0000e-02, 1.0000e-02, 1.0000e-02, 1.0000e-02, 1.0000e-02, 1.0000e-02, 1.0000e-02, 1.0000e-02,
         1.0000e-02, 1.0000e-02, 1.0000e-02, 1.0000e-02, 1.0000e-02, 1.0000e-02, 1.0000e-02, 1.0000e-02, 1.0000e-02,
         1.0000e-02, 1.0000e-02, 1.0000e-02, 1.0000e-02, 1.0000e-02, 1.0000e-02, 1.0000e-02, 1.0000e-02, 1.0000e-02,
         1.0000e-02, 1.0000e-02, 1.0000e-02, 1.0000e-02, 1.0000e-02, 1.0000e-02, 1.0000e-02, 1.0000e-02, 1.0000e-02,
         1.0000e-02, 1.0000e-02, 1.0000e-02, 1.0000e-02, 1.0000e-02, 1.0000e-02, 1.0000e-02, 1.0000e-02, 1.0000e-02,
         1.0000e-02, 1.0000e-02, 1.0000e-02, 1.0000e-02, 1.0000e-02, 1.0000e-02, 1.0000e-02, 1.0000e-02, 1.0000e-02,
         1.0000e-02, 1.0000e-02, 1.0000e-02, 1.0000e-02, 1.0000e-02, 1.0000e-02, 1.0000e-02, 1.0000e-02, 1.0000e-02,
         1.0000e-02, 1.0000e-02, 1.0000e-02, 1.0000e-02, 1.0000e-02, 1.0000e-02, 1.0000e-02, 1.0000e-02, 1.0000e-02,
         1.0000e-02, 1.0000e-02, 1.0000e-02, 1.0000e-02, 2.0000e-02, 2.0000e-02, 2.0000e-02, 2.0000e-02, 2.0000e-02,
         2.0000e-02, 2.0000e-02, 2.0000e-02, 2.0000e-02, 2.0000e-02, 2.0000e-02, 2.0000e-02, 2.0000e-02, 2.0000e-02,
         2.0000e-02, 2.0000e-02, 2.0000e-02, 2.0000e-02, 2.0000e-02, 2.0000e-02, 2.0000e-02, 2.0000e-02, 2.0000e-02,
         2.0000e-02, 2.0000e-02, 2.0000e-02, 2.0000e-02, 2.0000e-02, 2.0000e-02, 2.0000e-02, 2.0000e-02, 2.0000e-02,
         2.0000e-02, 2.0000e-02, 2.0000e-02, 2.0000e-02, 2.0000e-02, 2.0000e-02, 2.0000e-02, 2.0000e-02, 2.0000e-02,
         2.0000e-02, 2.0000e-02, 2.0000e-02, 2.0000e-02, 2.0000e-02, 2.0000e-02, 2.0000e-02, 2.0000e-02, 2.0000e-02,
         3.0000e-02, 3.0000e-02, 3.0000e-02, 3.0000e-02, 3.0000e-02, 3.0000e-02, 3.0000e-02, 3.0000e-02, 3.0000e-02,
         3.0000e-02, 3.0000e-02, 3.0000e-02, 3.0000e-02, 3.0000e-02, 3.0000e-02, 3.0000e-02, 3.0000e-02, 3.0000e-02,
         3.0000e-02, 3.0000e-02, 3.0000e-02, 3.0000e-02, 4.0000e-02, 4.0000e-02, 4.0000e-02, 4.0000e-02, 4.0000e-02,
         4.0000e-02, 4.0000e-02, 4.0000e-02, 4.0000e-02, 4.0000e-02, 5.0000e-02, 5.0000e-02, 5.0000e-02, 5.0000e-02,
         5.0000e-02, 5.0000e-02, 5.0000e-02, 5.0000e-02, 6.0000e-02, 6.0000e-02, 6.0000e-02, 6.0000e-02, 8.0000e-02,
         1.0000e-01, 1.0000e-01, 1.8000e-01, 2.6000e-01, 2.7000e-01, 2.7000e-01, 2.7000e-01, 2.8000e-01, 2.8000e-01,
         2.8000e-01, 2.9000e-01, 2.9000e-01, 2.9000e-01, 2.9000e-01, 3.0000e-01, 3.0000e-01, 3.1000e-01, 3.1000e-01,
         3.1000e-01, 3.2000e-01, 3.2000e-01, 3.2000e-01, 3.3000e-01, 3.3000e-01, 3.3000e-01, 3.3000e-01, 3.3000e-01,
         3.3000e-01, 3.4000e-01, 3.5000e-01, 3.5000e-01, 3.5000e-01, 3.5000e-01, 3.5000e-01, 3.6000e-01, 3.6000e-01,
         3.7000e-01, 3.7000e-01, 3.7000e-01, 3.7000e-01, 3.7000e-01, 3.8000e-01, 3.8000e-01, 3.8000e-01, 3.9000e-01,
         3.9000e-01, 3.9000e-01, 4.0000e-01, 4.2000e-01, 4.2000e-01, 4.2000e-01, 4.3000e-01, 4.3000e-01, 4.4000e-01,
         4.7000e-01, 4.8000e-01, 5.3000e-01, 6.5000e-01, 9.2000e-01],
    LAGEM: [-0.0372299, 0.011798]
}

correlation2_3 = {
    CORRECT: [6019.63, 6022.82, 6041.13, 6042.45, 6059.41, 6063.53, 6102.49, 6902.83],
    LP: [6019.63, 6041.13, 6059.41, 6063.53, 6102.49],
    ICP: [6041.13, 6042.45, 6059.41],
    LAGEM: [6046.53625, 26.4066426005]
}

correlation201_6 = {
    CORRECT: [],
    LP: [13017.83, 24050.41, 24050.41, 24050.41, 24050.42, 24051.33, 24052.73, 24052.73, 24052.73, 24053.21, 43144.6,
         43145.49, 43146.85, 43146.85, 43146.85, 43147.31, 51089.2, 55373.5, 57084.31, 57084.31, 57084.32, 57098.54,
         57099.19, 57100.99, 57104.04, 57105.47, 57105.49, 57106.19, 57106.19, 57106.19, 57135.79, 60195.68, 60195.81,
         60211.67, 60212.09, 60215.74, 60216.32, 60331.57, 63176.62, 64035.58, 64036.07, 64037.73, 66385.98, 66385.98],
    ICP: [-738.96, -738.96, -730.51, -730.51, -311.82, -311.4, -303.81, -303.38, -295.85, -295.43, -290.54, -290.12,
          -274.13, -273.71, -267.89, -267.47, 86.7, 86.71, 86.71, 90.6, 90.6, 90.61, 90.61, 90.62, 916.04, 1075.18,
          1721.94, 1721.94, 1721.94, 1721.94, 1862.85, 1862.85, 1862.85, 2627.04, 2627.04, 2627.04, 2637.97, 2637.97,
          2637.97, 2650., 2650., 2650.01, 2666.68, 2666.68, 2666.68, 2673.61, 2673.63, 2673.66, 2676.78, 2676.78,
          2676.78, 2693.41, 2706.39, 2706.39, 2706.39, 2725.39, 2725.39, 2725.39, 2725.4, 3588.21, 3588.21, 3588.21],
    LAGEM: [639.858407259, 1171.10706201]
}

correlation101_100 = {
    CORRECT: [],
    LP: [5003.74, 5005.24, 5181.83, 9340.7, 9485.62, 10201.17, 11066.66, 11143.43, 11145.65, 11927.97, 12061.56,
         12067.61, 12100.22, 12101.47, 12103.03, 14517.31, 15379.54, 16358., 17979.11, 17987.93, 18041.67, 18089.05,
         19064.71, 19097.05, 19183.81, 19819.17, 19824., 19870.84, 19980.31, 20011.97, 20593.71, 20703.5, 20728.26,
         21431.79, 21548.78, 22381.46, 22472.72, 22477.84, 23216.22, 23280.21, 23329.4, 23331.37, 23341.78, 23399.67,
         23460.16, 23490.2, 23741.76, 23876.89, 23959.95, 24018.18, 24177.63, 24206.8, 24274.84, 24457.18, 24933.23,
         25019.53, 25027.53, 25057.63, 25083.19, 25239.5, 25925.04, 26004.36, 26007.55, 26633.6, 26633.64, 26649.25,
         26819.32, 27473.62, 27584.23, 29200.8, 29375.74, 29484.54, 30057.32, 30288.56, 30333.13, 31141.37, 31233.36,
         31925.99, 32665.88, 32674.06, 32804.39, 32804.79, 32810.92, 32841.37, 32849.08, 32886.3, 32897.52, 33549.19,
         33580.58, 33587.31, 33587.37, 33682.29, 33722.87, 33729.27, 34305.55, 34503.65, 34535.68, 34800.79, 35436.76,
         35487.17, 36114.24, 37019.84, 38714.96, 38726.42, 38885.65, 38926.34, 39726.24, 40270.04, 40548.2, 40551.97,
         40608.03, 41349.78, 41351.24, 41366.28, 41548.66, 41929.08, 42251.82, 42254.33, 42282.14, 42282.16, 42335.69,
         42350.72, 42352.68, 42363.91, 42441.15, 42538.58, 42546.24, 42885.88, 43159.71, 43261.18, 44691.86, 44704.77,
         44753.25, 44872.12, 45402.67, 45730.6, 45787.37, 45800.51, 45821.22, 46574.28, 47405.19, 47406.53, 47410.72,
         47487.52, 47487.84, 47546.41, 47546.5, 47566.31, 47842.83, 47989.18, 48067.09, 48074.55, 48274.55, 48384.5,
         48408.48, 48415.48, 49131.33, 49133.65, 49175.21, 49234.81, 49240.98, 49267.25, 49276., 50118.09, 50617.75,
         50934.22, 50997.68, 51140.85, 51666.89, 51695.31, 51818.01, 51821.61, 51877.35, 52548.17, 52633.62, 52752.1,
         53392.05, 53588.03, 53594.58, 53603.41, 53729.24, 53736.84, 54221.68, 54270.5, 54360.95, 54450.4, 54477.48,
         54641.56, 54989.61, 55050.28, 55206.84, 55251.5, 55407.43, 55417.43, 56877.57, 56877.57, 56934.81, 57051.15,
         57714.06, 57714.25, 57781.51, 58607.54, 59283.3],
    ICP: [4.2789e+02, -3.4740e+02, -3.0634e+02, -3.0608e+02, -2.9159e+02, -2.9150e+02, -2.8906e+02, -2.8713e+02,
          -2.8685e+02, -2.8600e+02, -2.6162e+02, -2.2709e+02, -2.0167e+02, -1.5908e+02, -1.4518e+02, -1.0508e+02,
          -7.2530e+01, -4.1820e+01, -4.0710e+01, -3.6950e+01, -3.6100e+01, -3.5840e+01, -3.3690e+01, -3.2120e+01,
          -3.0660e+01, -2.9080e+01, -2.7250e+01, -2.6950e+01, -2.6430e+01, -2.6350e+01, -2.5150e+01, -2.4490e+01,
          -2.2980e+01, -2.0910e+01, -2.0730e+01, -2.0090e+01, -1.9170e+01, -1.8740e+01, -1.7700e+01, -1.7660e+01,
          -1.7130e+01, -1.6470e+01, -1.5290e+01, -1.4990e+01, -1.2980e+01, -1.2600e+01, -1.0460e+01, -1.0310e+01,
          -8.7200e+00, -8.5800e+00, -7.2900e+00, -6.7900e+00, -6.6600e+00, -6.0500e+00, -6.0400e+00, -5.5800e+00,
          -5.2700e+00, -3.6300e+00, -3.3500e+00, -3.1300e+00, -2.5100e+00, -2.2100e+00, -1.1600e+00, -7.4000e-01,
          -7.0000e-01, -2.5000e-01, -2.4000e-01, -1.4000e-01, -1.1000e-01, -7.0000e-02, -6.0000e-02, -6.0000e-02,
          -3.0000e-02, -1.0000e-02, -1.0000e-02, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00,
          0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00,
          0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 0.0000e+00, 1.0000e-02, 1.0000e-02, 1.0000e-02,
          1.0000e-02, 1.0000e-02, 1.0000e-02, 1.0000e-02, 1.0000e-02, 1.0000e-02, 1.0000e-02, 1.0000e-02, 1.0000e-02,
          1.0000e-02, 2.0000e-02, 2.0000e-02, 3.0000e-02, 3.0000e-02, 4.0000e-02, 4.0000e-02, 4.0000e-02, 4.0000e-02,
          5.0000e-02, 5.0000e-02, 6.0000e-02, 7.0000e-02, 8.0000e-02, 8.0000e-02, 8.0000e-02, 9.0000e-02, 9.0000e-02,
          9.0000e-02, 9.0000e-02, 9.0000e-02, 1.0000e-01, 1.0000e-01, 1.0000e-01, 1.0000e-01, 1.1000e-01, 1.1000e-01,
          1.1000e-01, 1.1000e-01, 1.1000e-01, 1.1000e-01, 1.1000e-01, 1.2000e-01, 1.2000e-01, 1.2000e-01, 1.2000e-01,
          1.2000e-01, 1.2000e-01, 1.2000e-01, 1.2000e-01, 1.2000e-01, 1.2000e-01, 1.3000e-01, 1.3000e-01, 1.3000e-01,
          1.3000e-01, 1.3000e-01, 1.3000e-01, 1.3000e-01, 1.4000e-01, 1.4000e-01, 1.4000e-01, 1.4000e-01, 1.4000e-01,
          1.5000e-01, 1.5000e-01, 1.5000e-01, 1.6000e-01, 1.6000e-01, 1.6000e-01, 1.6000e-01, 1.6000e-01, 1.7000e-01,
          1.7000e-01, 1.7000e-01, 1.7000e-01, 1.8000e-01, 1.9000e-01, 1.9000e-01, 2.1000e-01, 2.2000e-01, 2.2000e-01,
          2.2000e-01, 2.3000e-01, 2.4000e-01, 2.4000e-01, 2.5000e-01, 2.7000e-01, 2.7000e-01, 2.8000e-01, 3.0000e-01,
          3.1000e-01, 3.1000e-01, 3.1000e-01, 3.2000e-01, 3.2000e-01, 3.4000e-01, 3.4000e-01, 3.5000e-01, 3.7000e-01,
          3.8000e-01, 4.3000e-01, 4.4000e-01, 4.7000e-01, 4.9000e-01, 5.1000e-01, 8.6000e-01, 1.6500e+00, 1.7500e+00,
          5.6500e+00, 6.5400e+00, 7.7500e+00, 1.5040e+01, 3.0020e+01, 4.6620e+01, 6.9460e+01, 8.5930e+01, 9.8390e+01,
          1.5031e+02, 3.4855e+02, 5.4252e+02],
    LAGEM: [4170.3020799999995, 1452.5985400000002]
}


if (__name__ == "__main__"):
    plotDistributions(correlation66_65, '66-65')
    plotDistributions(correlation34054_34057, '34054-34057')
    plotDistributions(correlation7_66, '7-66')
    plotDistributions(correlation202_200, '202-200')
    plotDistributions(correlation2_3, '2-3')
    plotDistributions(correlation201_6, '201-6')
    plotDistributions(correlation101_100, '101-100')
    plt.show()
