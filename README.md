Event Correlation
=================

# Prerequisites

This project uses Qt for grpahical user interface. Prior to installing the project, the set of Qt libraries must be installed into the system:

For MacOS:

```
$ brew install qt
```

# Installation

First off, install [pyenv](https://github.com/pyenv/pyenv) for seamless Python version management.

Then, install Python into local environment (the latest tested version of Python was `3.9.5`):

```
$ pyenv install 3.9.5
```

Create and activate [virtual environment](https://docs.python-guide.org/dev/virtualenvs/#lower-level-virtualenv) for project dependencies:

```
$ cd ./event-correlation
$ virtualenv -p "$(pyenv root)/versions/3.9.5/bin/python" ./.venv/event-correlation
$ source ./.venv/event-correlation/bin/activate
```

Install project dependencies:

```
$ pip install -r requirements.txt
```

Finally, install the project (use `-e` flag for editable mode):

```
$ pip install -e .
```

# Usage

The CLI takes the following arguments and options:

```
usage: main.py [-h] -m {gen,load,symantec,hdPrinter} -i INPUT -a ALGORITHM [-t TRIGGER] [-r RESPONSE] [-d DISTRIBUTIONS] [-o OUTPUT]

optional arguments:
  -h, --help            show this help message and exit
  -m {gen,load,symantec,hdPrinter}, --method {gen,load,symantec,hdPrinter}
                        Method to create sequence.
  -i INPUT, --input INPUT
                        Path to file containing sequence
  -a ALGORITHM, --algorithm ALGORITHM
                        Algorithm to use for alignment
  -t TRIGGER, --trigger TRIGGER
                        Match only given trigger and response
  -r RESPONSE, --response RESPONSE
                        Match only given trigger and response
  -d DISTRIBUTIONS, --distributions DISTRIBUTIONS
                        Path to file containing true empirical distributions
  -o OUTPUT, --output OUTPUT
                        Path to file for storing sequence data
```

For instance:

```
$ python3 main.py \
  --method load \
  --input event_data.json \
  --algorithm ICE \
  --output sequence.json
```

# Citing

If you are using this code, please cite it as:

```
@inproceedings{zoeller2017,
  author={Zöller, Marc-Andre and Baum, Marcus and Huber, Marco F.},
  booktitle={2017 IEEE 15th International Conference on Industrial Informatics (INDIN)},
  title={Framework for mining event correlations and time lags in large event sequences},
  year={2017},
  volume={},
  number={},
  pages={805-810},
  doi={10.1109/INDIN.2017.8104876}
}
```

or

```
@article{huber2018,
  title = {Linear programming based time lag identification in event sequences},
  journal = {Automatica},
  volume = {98},
  pages = {14-19},
  year = {2018},
  issn = {0005-1098},
  doi = {https://doi.org/10.1016/j.automatica.2018.08.025},
  url = {https://www.sciencedirect.com/science/article/pii/S0005109818304242},
  author = {Marco F. Huber and Marc-André Zöller and Marcus Baum}
}
```
