import copy
import abstract
import numpy as np
from scipy.stats import energy_distance

class EnergyDistanceMetric(abstract.AbstractMetric):
    def __init__(self, paths):
        self.distanceMatrix = None
        self.distanceDict   = dict()
        self.paths          = sorted(paths, key=lambda x: x.label)
        self.pathNames      = sorted(list(map(lambda x: x.label, paths)))
        self.allCourseNames = abstract.extractAllCourseNames(paths)
        np.set_printoptions(suppress=True)

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

    def calculatePathDistance(self, pathA, pathB):
        courseNames = abstract.extractAllCourseNames([pathA, pathB])
        semesterA, semesterB = abstract.createExtendedLookUpList(pathA, pathB, courseNames)
        distance = energy_distance(semesterA, semesterB)
        return distance
