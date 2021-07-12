from distutils.core import setup, Extension


def get_requirements():
    with open('requirements.txt') as requirements:
        return requirements.read().splitlines()


lagEMModule = Extension('fastLagEM', sources=['extensions/fastLagEM.cpp'])
energyDistanceModule = Extension('fastEnergyDistance', sources=['extensions/fastEnergyDistance.cpp'])

setup(name='EventCorrelation',
      version='1.0',
      description='Correlation of events based on label and timestamp',
      ext_modules=[lagEMModule, energyDistanceModule],
      install_requires=get_requirements())
