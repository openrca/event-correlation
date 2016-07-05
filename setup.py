from distutils.core import setup, Extension

module = Extension('fastLagEM', sources=['extensions/fastLagEM.cpp'])

setup(name='fastLagEM',
      version='1.0',
      description='C++ implementation of lagEM algorithm',
      ext_modules=[module], requires=['numpy', 'matplotlib', 'scipy', 'PySide', 'pymatbridge', 'cvxopt', 'pulp'])
