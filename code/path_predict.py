#!/usr/local/bin/python
import sys
import csv
import random
import copy
from itertools import chain
from importlib import reload
from sklearn import metrics
from sklearn import cluster
from sklearn.neighbors import NearestNeighbors
import numpy as np

sys.path.append('classes')
sys.path.append('metrics')
import exam
import path
import student
import study
import raphimproved
import emd
import energy
import dameraulevenshtein
import userpath

def all_techs(paths_in):
    paths = copy.deepcopy(paths_in)
    emdm = emd.EarthMoversMetric(paths)
    energym = energy.EnergyDistanceMetric(paths)
    dlevm = dameraulevenshtein.DamerauLevenshteinMetric(paths)
    metric2m = raphimproved.RaphMetricImproved(paths)

    rdistanceMatrix, rnames = metric2m.calculateDistance()
    emdistanceMatrix, emnames = emdm.calculateDistance()
    endistanceMatrix, ennames = energym.calculateDistance()
    dlevdistanceMatrix, dlevnames = dlevm.calculateDistance()

    out = {
        'raph': {
            'matrix': rdistanceMatrix,
            'labels': rnames
            },
        'energy': {
            'matrix': endistanceMatrix,
            'labels': ennames
            },
        'earthmover': {
            'matrix': emdistanceMatrix,
            'labels': emnames
            },
        'stringedit': {
            'matrix': dlevdistanceMatrix,
            'labels': dlevnames
            }
        }

    return out

def find_k_neighbors(path_label, distances, k):
    all = dict()
    for dist in distances:
        m = distances[dist]['matrix']
        l = distances[dist]['labels']
        i = l.index(path_label)
        row = m[i]
        R = row.reshape(-1,1)
        nbrs = NearestNeighbors(n_neighbors=k+1, algorithm='ball_tree').fit(R)
        distces, indices = nbrs.kneighbors(R)
        result = []
        for e in indices[i]:
            if l[e] != path_label:
                result.append(l[e])
        if len(result) > k:
            result.pop()
        all[dist] = result
    return all

def generate_prediction(prediction_array, past_exams):
    out = []
    l = len(prediction_array)
    pred_array = [item for sublist in prediction_array for item in sublist]
    pred_names = list(map(lambda x: str(x), pred_array))
    past_array = [item for sublist in past_exams for item in sublist]
    past_names = list(map(lambda x: str(x), past_array))
    pred_names_shortened = []
    for n in pred_names:
        if n not in past_names:
            pred_names_shortened.append(n)
    avg_len = int(np.rint(np.average(list(map(lambda x: len(x), prediction_array)))))
    med_len = int(np.rint(np.median(list(map(lambda x: len(x), prediction_array)))))
    names, counts = np.unique(pred_names_shortened, return_counts=True)
    names = names.tolist()
    counts = counts.tolist()
    for i in range(avg_len):
        highest = -1
        if len(counts) == 0:
            break
        for v in counts:
            highest = v if v > highest else highest
        out.append(names.pop(counts.index(highest)))
        counts.pop(counts.index(highest))
    return out, med_len, avg_len

def run_prediction(students, semesters, ks, samples, npred, seed):
    outstring = "samples,semester,k,delta_length_raph,delta_median_length_raph,delta_length_energy,delta_median_length_energy,delta_length_earthmover,delta_median_length_earthmover,delta_length_stringedit,delta_median_length_stringedit"
    out = dict()
    for s in semesters:
        a = student.extractTrimmedPaths(copy.deepcopy(students), s)
        b = []
        actual = dict()
        for p in a:
            if len(p.semester_original) > s and len(p.courses) != 0:
                b.append(copy.deepcopy(p))
                actual[p.label] = {
                    "length": len(p.semester_original),
                    "predict": p.predict,
                    "semesters": p.semester
                }
        random.seed(seed)
        if samples > len(b):
            samples = len(b)
            npred = int(samples*0.2)

        c = random.sample(b, samples)
        c_names = sorted(list(map(lambda x: x.label, c)))
        distances = all_techs(c)
        t = random.sample(c, npred)
        test_names = sorted(list(map(lambda x: x.label, t)))

        predictions = dict()
        for k in ks:
            for t_id in test_names:
                res = dict()
                neighbors = find_k_neighbors(t_id, distances, k)
                res['actual_length'] = actual[t_id]["length"]
                for metric in neighbors:
                    res[metric] = dict()
                    res[metric]['length'] = 0
                    res[metric]['semester'] = []
                    res[metric]['median_length'] = []
                    for i in neighbors[metric]:
                        res[metric]['length'] += actual[i]["length"]
                        res[metric]['semester'].append(actual[i]["predict"])
                        res[metric]['median_length'].append(actual[i]['length'])
                    res[metric]['length'] /= k
                    res["delta_length_" + metric] = res['actual_length'] - res[metric]['length']
                    res[metric]["median_length"] = np.median(res[metric]['median_length'])
                    res["delta_median_length_" + metric] = res["actual_length"] - res[metric]['median_length']

                predictions[t_id] = res

            all_predictions = {
                'raph_length' : [],
                'raph_median_length' : [],
                'energy_length': [],
                'energy_median_length': [],
                'earthmover_length': [],
                'earthmover_median_length': [],
                'stringedit_length': [],
                'stringedit_median_length': []
            }

            all_delta = {
                'raph_length' : [],
                'raph_median_length' : [],
                'energy_length': [],
                'energy_median_length': [],
                'earthmover_length': [],
                'earthmover_median_length': [],
                'stringedit_length': [],
                'stringedit_median_length': []
            }

            for inc in predictions:
                all_predictions['raph_length'].append(predictions[inc]['raph']['length'])
                all_delta['raph_length'].append(predictions[inc]['delta_length_raph'])
                all_predictions['energy_length'].append(predictions[inc]['energy']['length'])
                all_delta['energy_length'].append(predictions[inc]['delta_length_energy'])
                all_predictions['earthmover_length'].append(predictions[inc]['earthmover']['length'])
                all_delta['earthmover_length'].append(predictions[inc]['delta_length_earthmover'])
                all_predictions['stringedit_length'].append(predictions[inc]['stringedit']['length'])
                all_delta['stringedit_length'].append(predictions[inc]['delta_length_stringedit'])

                all_predictions['raph_median_length'].append(predictions[inc]['raph']['median_length'])
                all_delta['raph_median_length'].append(predictions[inc]['delta_median_length_raph'])
                all_predictions['energy_median_length'].append(predictions[inc]['energy']['median_length'])
                all_delta['energy_median_length'].append(predictions[inc]['delta_median_length_energy'])
                all_predictions['earthmover_median_length'].append(predictions[inc]['earthmover']['median_length'])
                all_delta['earthmover_median_length'].append(predictions[inc]['delta_median_length_earthmover'])
                all_predictions['stringedit_median_length'].append(predictions[inc]['stringedit']['median_length'])
                all_delta['stringedit_median_length'].append(predictions[inc]['delta_median_length_stringedit'])

            dlr = np.absolute(np.average(all_delta['raph_length']))
            dlen = np.absolute(np.average(all_delta['energy_length']))
            dlem = np.absolute(np.average(all_delta['earthmover_length']))
            dlse = np.absolute(np.average(all_delta['stringedit_length']))

            dlrm = np.absolute(np.average(all_delta['raph_median_length']))
            dlenm = np.absolute(np.average(all_delta['energy_median_length']))
            dlemm = np.absolute(np.average(all_delta['earthmover_median_length']))
            dlsem = np.absolute(np.average(all_delta['stringedit_median_length']))

            outstring += "\n" + str(samples) + "," + str(s) + "," + str(k) + "," + str(dlr) + "," + str(dlrm) + "," + str(dlen) + "," + str(dlenm) + "," + str(dlem) + "," + str(dlemm) + "," + str(dlse) + "," + str(dlsem)
        out[s] = predictions
    return outstring, predictions

textpaths = []
with open("data/paths.txt", "r") as text_file:
    lines = text_file.readlines()
    for line in lines:
        textpaths.append(line.strip())

students = userpath.create_user_students(textpaths)

semesters = [2, 3, 4]
ks = [5,10,15,20,25,30,40]
samples = 500
npred = int(samples*0.2)
seed = 0

outstring, predictions = run_prediction(students, semesters, ks, samples, npred, seed)

with open("out/results_predict.csv", "w") as text_file:
    print(outstring, file=text_file)

print("number samples decreases with increasing number of semesters, since some paths are shorter than that")
print("all files written to the 'out' directory")
