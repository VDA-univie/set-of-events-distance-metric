import copy
import abstract
import numpy as np

class RaphMetricImproved(abstract.AbstractMetric):
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
        coursesA = abstract.extractAllCourseNames([pathA])
        coursesB = abstract.extractAllCourseNames([pathB])
        coursesCombined = np.intersect1d(coursesA, coursesB)
        courseNames = abstract.extractAllCourseNames([pathA, pathB])
        coursesOnlyA = list(set(courseNames) - set(coursesB))
        coursesOnlyB = list(set(courseNames) - set(coursesA))
        #semesterA, semesterB = abstract.createExtendedLookUpList(pathA, pathB, courseNames)
        semesterA, semesterB = abstract.createReducedLookUpList(pathA, pathB, coursesCombined)

        metricDistance = 1
        if(len(semesterA) and len(semesterB)):
            distanceA = self.generateDistanceMatrix(semesterA)
            distanceB = self.generateDistanceMatrix(semesterB)
            distanceDiff = np.absolute(np.sign(np.subtract(distanceA, distanceB)))
            tri = distanceDiff[np.triu_indices_from(distanceDiff, 1)]
            if(len(tri) != 0):
                metricDistance = sum(tri)/len(tri)
            else:
                metricDistance = distanceDiff[0][0]

        countCoursesDifferent = len(coursesOnlyA) + len(coursesOnlyB)
        countCourses = len(coursesA) + len(coursesB)
        if countCourses == 0:
            print(pathA.label)
            print(pathA.studentid)
            print(pathA.studyid)
            print(pathA)
            print(pathA.courses)
            print(pathB.label)
            print(pathB.studentid)
            print(pathB.studyid)
            print(pathB)
            print(pathB.courses)
        diffFactor = countCoursesDifferent/countCourses
        distance = diffFactor + metricDistance * (1-diffFactor)
        #print(pathA.getPrintableShortPath(), pathB.getPrintableShortPath(), semesterA, semesterB, coursesOnlyA, coursesOnlyB, metricDistance, diffFactor, distance)
        return distance

    def setNonOverlap(self, distanceMatrix, courseNames, ownCourses, val):
        indices = []
        for i, course in enumerate(courseNames):
            if course not in ownCourses:
                indices.append(i)
        out = self.replaceRowCol(distanceMatrix, indices, val)
        return out

    def replaceRowCol(self, M, indices, val):
        nrows, ncols = M.shape
        #if(index>nrows or index>ncols) return
        out = M
        x = np.full([1, ncols], val)
        y = np.full([nrows, 1], val)
        for i in indices:
            out[i,:] = x
            out[:,i:(i+1)] = y
        np.fill_diagonal(out, 0)
        return out

    def generateDistanceMatrix(self, semesterVector):
        out = []
        for el in semesterVector:
            out.append(np.subtract(semesterVector, el))
        return np.transpose(np.sign(out))
