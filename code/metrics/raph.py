import copy
import abstract
import numpy as np

class RaphMetric(abstract.AbstractMetric):
    def __init__(self, paths):
        self.distanceMatrix = None
        self.distanceDict   = dict()
        self.paths          = sorted(paths, key=lambda x: x.label)
        self.pathNames      = sorted(list(map(lambda x: x.label, paths)))
        self.allCourseNames = abstract.extractAllCourseNames(paths)
        np.set_printoptions(suppress=True)

    def calculateDistanceDict(self):
        #create array of all courses, sorted
        #create vector from lookuptable (sorted courses)
        #vector - each value as new internal representation matrix
        #transpose before output
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
        #i_lower = np.tril_indices(len(self.pathNames), -1)
        #self.distanceMatrix[i_lower] = self.distanceMatrix.T[i_lower]
        return self.distanceMatrix, self.pathNames

    def calculatePathDistance(self, pathA, pathB):
        courseNames = abstract.extractAllCourseNames([pathA, pathB])
        semesterA, semesterB = abstract.createExtendedLookUpList(pathA, pathB, courseNames)
        distanceA = self.generateDistanceMatrix(semesterA)
        distanceB = self.generateDistanceMatrix(semesterB)
        distanceDiff = np.absolute(np.sign(np.subtract(distanceA, distanceB)))

        n, m = distanceDiff.shape
        size = n - 1
        tri = np.fliplr(distanceDiff)[np.triu_indices(size)]
        distance = sum(tri)/len(tri)

        return distance

    def generateDistanceMatrix(self, semesterVector):
        out = []
        for el in semesterVector:
            out.append(np.subtract(semesterVector, el))
        return np.transpose(np.sign(out))
