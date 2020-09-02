import numpy as np
import abstract
from pyxdameraulevenshtein import damerau_levenshtein_distance, normalized_damerau_levenshtein_distance

# 1. transform course names into unicode characters
# 2. form sets of characters for each semesters
# 3. calculate symmetric_difference between all semester sets
# 4. find the minmal distance between semester sets and match them
# 5. label matches identically
# 6. calculate levenshtein distance between strings of labeled semesters
# 7. find useful way to join both distances

# NO 2. sort characters per semester
# NO 3. join characters into words, one word per semester
# NO 4. calculate damerau levenshtein distance between all semesterwords
# NO 5. find the set of minimal distance using all semesterwords (annealing)
# NO 6. calculate GraphEditDistance
# NO 7. find useful way to join both distances

class SetDifferenceLevenshteinMetric(abstract.AbstractMetric):
    def __init__(self, paths):
        self.distanceMatrix = None
        self.distanceDict   = dict()
        self.paths          = sorted(paths, key=lambda x: x.label)
        self.pathNames      = sorted(list(map(lambda x: x.label, paths)))
        self.allCourseNames = abstract.extractAllCourseNames(paths)
        np.set_printoptions(suppress=True)

    def createSemesterWords(self, pathA, pathB):
        courseNames = abstract.extractAllCourseNames([pathA, pathB])
        idDict = dict()
        for i, n in enumerate(courseNames):
            idDict[n] = i
        semesterA, semesterB = [], []
        for sem in pathA.semester:
            tempArr = []
            for c in sem:
                tempArr.append(chr(idDict[c.name]))
            tempArr.sort()
            semesterA.append(''.join(tempArr))
        for sem in pathB.semester:
            tempArr = []
            for c in sem:
                tempArr.append(chr(idDict[c.name]))
            tempArr.sort()
            semesterB.append(''.join(tempArr))
        return semesterA, semesterB

    def calculateIndividualSemesterDistances(self, semA, semB):
        distances = np.array([])
        for i, a in enumerate(semA):
            sa = set(a)
            distRow = np.array([])
            for j, b in enumerate(semB):
                sb = set(b)
                if j <= i:
                    distRow = np.append(distRow, [0])
                else:
                    distRow = np.append([sa.symmetric_difference(sb)])


    def calculatePathDistance(self, pathA, pathB):
        semA, semB = self.createSemesterWords(pathA, pathB)
        for i, s1 in enumerate(semA):
            distRow = np.array([])
            for j, path2 in enumerate(self.paths):
                if j <= i:
                    distRow = np.append(distRow, [0])
                else:
                    distRow = np.append(distRow, [self.calculatePathDistance(path, path2)])
            if self.distanceMatrix is None:
                self.distanceMatrix = np.array([distRow])
            else:
                self.distanceMatrix = np.vstack((self.distanceMatrix, distRow))

        distance = normalized_damerau_levenshtein_distance(strSemesterA, strSemesterB)
        return distance

    def calculateDistance(self):
        self.distanceMatrix = None
        for i, path in enumerate(self.paths):
            distRow = np.array([])
            for j, path2 in enumerate(self.paths):
                if j <= i:
                    distRow = np.append(distRow, [0])
                else:
                    distRow = np.append(distRow, [self.calculatePathDistance(path, path2)])
            if self.distanceMatrix is None:
                self.distanceMatrix = np.array([distRow])
            else:
                self.distanceMatrix = np.vstack((self.distanceMatrix, distRow))
        i_lower = np.tril_indices(len(self.pathNames), -1)
        self.distanceMatrix[i_lower] = self.distanceMatrix.T[i_lower]
        return self.distanceMatrix, self.pathNames

    def calculateDistanceDict(self):
        self.distanceDict = dict()
        for path in self.paths:
            distRow = dict()
            for path2 in self.paths:
                if path.label == path2.label:
                    distRow[path2.label] = 0
                else:
                    distRow[path2.label] = self.calculatePathDistance(path, path2)
            self.distanceDict[path.label] = distRow
        return self.distanceDict
