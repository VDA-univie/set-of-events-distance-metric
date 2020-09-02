# Supplemental Material for A Distance Metric for Sets of Events

This archive contains the appendix, the full code to generate the results shown in the paper as well as the survey questions and results of the user survey.

The instructions below are for the bash shell, since it is available on all operating systems. To run the experiments described in this work, the following steps need to be done first to set up the environment:

1. download the 'code' directory to your machine
2. navigate to the 'code' directory in a terminal
3. create a virtual environment using python3
   - `python3 -m venv env`
4. activate the virtual environment
   - `source env/bin/activate`
5. install all required packages
   - `pip install -r pip-requirements`



**The following command can then be used to replicate the different experiments from section IV:**

- Clustering generated paths
  - `python path_clustering_generic.py`
- Clustering of real paths
  - `python path_clustering.py`
- Predicting path lengths
  - `python path_predict.py`
