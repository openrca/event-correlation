from distutils.core import setup, Extension

lagEMModule = Extension('fastLagEM', sources=['extensions/fastLagEM.cpp'])
energyDistanceModule = Extension('fastEnergyDistance', sources=['extensions/fastEnergyDistance.cpp'])

setup(name='EventCorrelation',
      version='1.0',
      description='Correlation of events based on label and timestamp',
      ext_modules=[lagEMModule, energyDistanceModule],
      requires=['numpy', 'matplotlib', 'scipy', 'PySide', 'pymatbridge', 'cvxopt', 'pulp', 'aniso8601', 'networkx',
                'igraph', 'ProbPy'])
