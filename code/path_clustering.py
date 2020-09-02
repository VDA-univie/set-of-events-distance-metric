#!/usr/local/bin/python
import sys
import csv
import random
from importlib import reload
from sklearn import metrics
from sklearn import cluster
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

sys.path.append('classes')
sys.path.append('metrics')
import exam
import path
import progress
import student
import study
import abstract
import raphimproved
import emd
import energy
import dameraulevenshtein
import studywrangler
import userpath

def run_dbscan(distance_matrix, epsval, minsampleval):
    db = cluster.DBSCAN(eps=epsval, min_samples=minsampleval).fit(distance_matrix)
    core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
    core_samples_mask[db.core_sample_indices_] = True
    labels = db.labels_
    n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
    n_noise_ = list(labels).count(-1)

    return {
        "clusters": n_clusters_,
        "noise": n_noise_,
        "labels": labels
        }

def mirror_matrix(m):
    for i in range(len(m)):
        for j in range(i, len(m)):
            m[j][i] = m[i][j]
    return m

def calculate_clustering(paths, epsval, minsampleval):
    emdist = emd.EarthMoversMetric(paths)
    energydist = energy.EnergyDistanceMetric(paths)
    dlev = dameraulevenshtein.DamerauLevenshteinMetric(paths)
    metric2 = raphimproved.RaphMetricImproved(paths)

    rdistanceMatrix, rnames = metric2.calculateDistance()
    emdistanceMatrix, emnames = emdist.calculateDistance()
    endistanceMatrix, ennames = energydist.calculateDistance()
    dlevdistanceMatrix, dlevnames = dlev.calculateDistance()

    rdb = run_dbscan(rdistanceMatrix, epsval, minsampleval)
    emdb = run_dbscan(emdistanceMatrix, epsval, minsampleval)
    endb = run_dbscan(endistanceMatrix, epsval, minsampleval)
    ddb = run_dbscan(dlevdistanceMatrix, epsval, minsampleval)
    rdb['matrix'] = rdistanceMatrix
    emdb['matrix'] = emdistanceMatrix
    endb['matrix'] = endistanceMatrix
    ddb['matrix'] = dlevdistanceMatrix

    results = {
        'dlev' : ddb,
        'em' : emdb,
        'en' : endb,
        'raph' : rdb
    }

    return results

def create_heatmap(matrix, labels):
    l = labels
    m = mirror_matrix(matrix)
    ll = len(set(l))

    buckets = []
    for i in range(ll):
        buckets.append([])
    for i, e in enumerate(l):
        buckets[e].append(m[i])

    sortedmatrix = []
    for b in buckets:
        for e in b:
            sortedmatrix.append(e)

    bounds = list(map(lambda x: len(x), buckets))
    clu = []
    curr = 0
    for e in bounds:
        clu.append(curr + e)
        curr += e

    color='hot'

    heat = sns.heatmap(sortedmatrix, cmap=color, vmin=0, vmax=1, square=True, yticklabels=10, xticklabels=10)
    ret = {
        'figure': heat,
        'bounds': bounds
    }
    return heat, clu

textpaths = []
with open("data/paths.txt", "r") as text_file:
    lines = text_file.readlines()
    for line in lines:
        textpaths.append(line.strip())

students = userpath.create_user_students(textpaths)
paths = student.extractPaths(students)
random.seed(0)
paths = random.sample(paths, 100)

epsval = 1.3
minsampleval = 4

clusterings = calculate_clustering(paths, epsval, minsampleval)

mets = ["raph", "dlev", "em", "en"]

outstring = "metric,clusters,noise,cluster_boundaries\n"
for m in mets:
    hm, bounds = create_heatmap(clusterings[m]['matrix'], clusterings[m]['labels'])
    plt.figure()
    fig = hm.get_figure()
    fig.savefig("out/"+m+"_heatmap_dbscan_eps_"+str(epsval)+"_minsamples_"+str(minsampleval)+".png")
    outstring += m + "," + str(clusterings[m]["clusters"]) + "," + str(clusterings[m]["noise"]) + "," + str(bounds) + "\n"

with open("out/clustering_dbscan_results.csv", "w") as text_file:
    print(outstring, file=text_file)
print("all files written to the 'out' directory")
