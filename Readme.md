Root Cause Detection
==============


__Warning:__ This repo is in no good condition and may require some work to make the code actually working again.

Dependencies
--------------
- python-3.5
- numpy-1.11.0
- scipy-0.17.0
- Qt-4.8.7
- pyside-1.2.2
- Matplotlib-1.5.1
- networkx-1.11
- ProbPy
- pydotplus
- python-matlab-bridge-0.6 (optional)
- cvxopt-1.1.8 (optional, including glpk support)
- GLPK-4.57 (optional)
- GraphViz

- TODO add python-igraph --> 
	1. download whl. file and install local file with "pip install python_igraph-0.7.1.post6-cp37-cp37m-win_amd64.whl" due to missing compiled C core (https://igraph.org/python/)
	URL: https://www.lfd.uci.edu/~gohlke/pythonlibs/#python-igraph


_Info_: I have used and tested the above libraries in the stated version for project development.
 To my knowledge I have not used any specific features introduced in these versions. Consequently, it may be possible to use older versions of these libraries as well.

Citing
-------
If you are using this code, please cite it as

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
