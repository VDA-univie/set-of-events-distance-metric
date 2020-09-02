#!/usr/local/bin/python
import sys
import csv
import random
from sklearn import metrics
from sklearn import cluster
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

sys.path.append('classes')
sys.path.append('metrics')
import student
import study
import abstract
import raphimproved
import emd
import energy
import dameraulevenshtein
import userpath

def scale(X, x_min, x_max):
    nom = (X-X.min(axis=0))*(x_max-x_min)
    denom = X.max(axis=0) - X.min(axis=0)
    denom[denom==0] = 1
    return x_min + nom/denom

def createPathVariations(students, ipath, label, count, amount = [0.5, 0.4, 0.1], direction = 0):
    #paths = []
    studies = []
    testy = student.getStudentById(students, ipath.studentid)
    testystudy = next((x for x in testy.studies if x.id == ipath.studyid), None)
    firstsem = ipath.getFirstSemester()
    lastsem = study.changeSemester(ipath.getLastSemester(), 2)
    allsem = study.createSemesters(firstsem, lastsem)
    random.seed(0)

    for c in range(count):
        courses = []
        for i, sem in enumerate(ipath.semester):
            for course in sem:
                change = random.random()
                add = 0
                am = 0
                for j, x in enumerate(amount):
                    am += x
                    add = j
                    if change <= am:
                        break

                if direction == 0:
                    if random.random() <= 0.5:
                        add *= -1
                else:
                    add *= direction
                if add + i < 0:
                    add = 0
                pos = i + add
                course.semester = allsem[pos]
                courses.append(course)

        studies.append(study.Study(testystudy.studycode, testystudy.studentid,
                            testystudy.matnr, courses, testystudy.progress,
                            label + "-" + str(c)))
    return studies

def run_variation_clustering(students, n, variation, epsval, minsampleval):
    a = student.extractPaths(students)

    genstudies = (createPathVariations(students, a[0], "0", n, variation)
        + createPathVariations(students, a[1], "1", n, variation)
        + createPathVariations(students, a[2], "2", n, variation)
        + createPathVariations(students, a[3], "3", n, variation))

    a[0].label = "0"
    a[1].label = "1"
    a[2].label = "2"
    a[3].label = "3"
    b = study.getAllPaths(genstudies)
    b[0] = a[0]
    b[n] = a[1]
    b[n*2] = a[2]
    b[n*3] = a[3]
    emdist = emd.EarthMoversMetric(b)
    energydist = energy.EnergyDistanceMetric(b)
    dlev = dameraulevenshtein.DamerauLevenshteinMetric(b)
    metric2 = raphimproved.RaphMetricImproved(b)

    rdistanceMatrix, rnames = metric2.calculateDistance()
    rlabels_true = np.array(list(map(lambda x: int(x.split("-")[0]), rnames)))
    emdistanceMatrix, emnames = emdist.calculateDistance()
    emlabels_true = np.array(list(map(lambda x: int(x.split("-")[0]), emnames)))
    endistanceMatrix, ennames = energydist.calculateDistance()
    enlabels_true = np.array(list(map(lambda x: int(x.split("-")[0]), ennames)))
    dlevdistanceMatrix, dlevnames = dlev.calculateDistance()
    dlabels_true = np.array(list(map(lambda x: int(x.split("-")[0]), dlevnames)))

    rpred = cluster.KMeans(n_clusters = 4).fit_predict(rdistanceMatrix)
    rkmeans = cluster_metrics(rlabels_true, rpred, rdistanceMatrix)
    rdb = run_dbscan(rdistanceMatrix, epsval, minsampleval)
    rdbscan = cluster_metrics(rlabels_true, rdb["labels"], rdistanceMatrix)

    empred = cluster.KMeans(n_clusters = 4).fit_predict(emdistanceMatrix)
    emkmeans = cluster_metrics(emlabels_true, empred, emdistanceMatrix)
    emdb = run_dbscan(emdistanceMatrix, epsval, minsampleval)
    emdbscan = cluster_metrics(emlabels_true, emdb["labels"], emdistanceMatrix)

    enpred = cluster.KMeans(n_clusters = 4).fit_predict(endistanceMatrix)
    enkmeans = cluster_metrics(enlabels_true, enpred, endistanceMatrix)
    endb = run_dbscan(endistanceMatrix, epsval, minsampleval)
    endbscan = cluster_metrics(enlabels_true, endb["labels"], endistanceMatrix)

    dpred = cluster.KMeans(n_clusters = 4).fit_predict(dlevdistanceMatrix)
    dkmeans = cluster_metrics(dlabels_true, dpred, dlevdistanceMatrix)
    ddb = run_dbscan(dlevdistanceMatrix, epsval, minsampleval)
    ddbscan = cluster_metrics(dlabels_true, ddb["labels"], dlevdistanceMatrix)

    outstring = "name,homogeneity_score,completeness_score,v_measure_score,adjusted_rand_score,adjusted_mutual_info_score,normalized_mutual_info_score,silhouette_score,clusters,noise\n"
    outstring += "rkmeans," + ",".join(list(map(lambda x: str(x), list(rkmeans.values())))) + ",4,0\n"
    outstring += "enkmeans," + ",".join(list(map(lambda x: str(x), list(enkmeans.values())))) + ",4,0\n"
    outstring += "emkmeans," + ",".join(list(map(lambda x: str(x), list(emkmeans.values())))) + ",4,0\n"
    outstring += "dlevkmeans," + ",".join(list(map(lambda x: str(x), list(dkmeans.values())))) + ",4,0\n"
    outstring += "rdbscan," + ",".join(list(map(lambda x: str(x), list(rdbscan.values())))) + "," + str(rdb["clusters"]) + "," + str(rdb["noise"])+ "\n"
    outstring += "endbscan," + ",".join(list(map(lambda x: str(x), list(endbscan.values())))) + "," + str(endb["clusters"]) + "," + str(endb["noise"])+ "\n"
    outstring += "emdbscan," + ",".join(list(map(lambda x: str(x), list(emdbscan.values())))) + "," + str(emdb["clusters"]) + "," + str(emdb["noise"])+ "\n"
    outstring += "dlevdbscan," + ",".join(list(map(lambda x: str(x), list(ddbscan.values())))) + "," + str(ddb["clusters"]) + "," + str(ddb["noise"])+ "\n"

    dist_matrices = {
        "raph": rdistanceMatrix,
        "em": emdistanceMatrix,
        "en": endistanceMatrix,
        "dlev": dlevdistanceMatrix,
        "names": rnames
    }

    return outstring, dist_matrices

def cluster_metrics(labels_true, labels_predicted, distance_matrix):
    try:
        silhouette_score = metrics.silhouette_score(distance_matrix, labels_predicted)
    except:
        silhouette_score = 0
    return {
        "homogeneity_score": metrics.homogeneity_score(labels_true, labels_predicted),
        "completeness_score": metrics.completeness_score(labels_true, labels_predicted),
        "v_measure_score": metrics.v_measure_score(labels_true, labels_predicted),
        "adjusted_rand_score": metrics.adjusted_rand_score(labels_true, labels_predicted),
        "adjusted_mutual_info_score": metrics.adjusted_mutual_info_score(labels_true, labels_predicted),
        "normalized_mutual_info_score": metrics.normalized_mutual_info_score(labels_true, labels_predicted),
        "silhouette_score": silhouette_score
    }

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

textpaths = []
with open("data/paths_gen.txt", "r") as text_file:
    lines = text_file.readlines()
    for line in lines:
        textpaths.append(line.strip())


epsval = 0.8
minsampleval = 5

stds = userpath.create_user_students(textpaths)
n = 25

variatons = [
    [0.7, 0.2, 0.1],
    [0.5, 0.3, 0.2],
    [0.3, 0.4, 0.3]
]

dmatrices = None
for variation in variatons:
    outstring, dmatrices = run_variation_clustering(stds, n, variation, epsval, minsampleval)

    with open("out/cluster_metrics_"+str(n*4)+"_students_"+str(int(variation[0]*100))+str(int(variation[1]*100))+str(int(variation[2]*100))+".csv", "w") as text_file:
        print(outstring, file=text_file)

    rmatrix = mirror_matrix(dmatrices['raph'])
    dlevmatrix = mirror_matrix(dmatrices['dlev'])
    emmatrix = mirror_matrix(scale(dmatrices['em'], 0, 1))
    enmatrix = mirror_matrix(scale(dmatrices['en'], 0, 1))
    color = "hot"
    dpi = 300

    dlevheat = sns.heatmap(dlevmatrix, cmap=color, vmin=0, vmax=1, square=True, yticklabels=10, xticklabels=10)
    plt.figure()
    df = dlevheat.get_figure()
    df.savefig("out/dlev_heatmap_"+str(n*4)+"_students_"+str(int(variation[0]*100))+str(int(variation[1]*100))+str(int(variation[2]*100))+".png", dpi=dpi)

    endheat = sns.heatmap(enmatrix, cmap=color, vmin=0, vmax=1, square=True, yticklabels=10, xticklabels=10)
    plt.figure()
    enf = endheat.get_figure()
    enf.savefig("out/energy_heatmap_"+str(n*4)+"_students_"+str(int(variation[0]*100))+str(int(variation[1]*100))+str(int(variation[2]*100))+".png", dpi=dpi)

    emdheat = sns.heatmap(emmatrix, cmap=color, vmin=0, vmax=1, square=True, yticklabels=10, xticklabels=10)
    plt.figure()
    emf = emdheat.get_figure()
    emf.savefig("out/earthmovers_heatmap_"+str(n*4)+"_students_"+str(int(variation[0]*100))+str(int(variation[1]*100))+str(int(variation[2]*100))+".png", dpi=dpi)

    rdheat = sns.heatmap(rmatrix, cmap=color, vmin=0, vmax=1, square=True, yticklabels=10, xticklabels=10)
    plt.figure()
    rf = rdheat.get_figure()
    rf.savefig("out/raph_heatmap_"+str(n*4)+"_students_"+str(int(variation[0]*100))+str(int(variation[1]*100))+str(int(variation[2]*100))+".png", dpi=dpi)

print("all files written to the 'out' directory")
