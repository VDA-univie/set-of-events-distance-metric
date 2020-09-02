import copy
import path
import progress

def createSemesters(f, t):
    out = []
    curr = copy.copy(f)
    out.append(curr)
    while( curr != t ):
        y = int(curr[0:4])
        s = curr[4]
        if( s == 'S'):
            curr = str(y) + 'W'
        else:
            curr = str(y+1) + 'S'
        out.append(curr)
    return out

def changeSemester(sem, change):
    if(change == 0):
        return sem
    year = int(sem[:4])
    season = sem[4]
    schange = change%2
    ychange = int((change - schange)/2)
    year += ychange
    if(schange):
        if(change > 0):
            if(season == 'S'):
                return str(year)+'W'
            else:
                return str(year+1)+'S'
        else:
            if(season == 'S'):
                return str(year)+'W'
            else:
                return str(year+1)+'S'
    else:
        return str(year)+season

def getAllPaths(studies):
    paths = []
    for s in studies:
        paths.append(s.path)
    return paths

def getAllLineData(studies):
    linedata = []
    for s in studies:
        linedata.append(s.getLineData())
    return linedata

class Study:
    def __init__(self, studycode, studentid, matnr, exams, progress = None, label = ""):
        self.id         = str(studentid) + '-' + str(studycode)
        self.studycode  = studycode
        self.studentid  = studentid
        self.matnr      = matnr
        self.exams      = []
        self.progress   = progress
        if label is "":
            self.label = str(self.progress.identifier) + "-" + str(self.progress.study)
        else:
            self.label = label
        self.path       = None
        self.semester   = {}
        self.sects      = {}

        if len(exams): self.addExams(exams)

        self.path = self.createPath()
        self.lineData = self.getLineData()
        self.semesterArray = self.getSemesterArray()

    def addExams(self, e):
        for x in e: self.addExam(x)

    def addExam(self, e):
        self.exams.append(e)
        self.addToSemester(e)

    def createPath(self):
        if self.progress:
            return path.Path(self.getSemesterArray(), self.label, self.id, \
                             self.studentid, self.studycode, self.progress.state)
        else:
            return path.Path(self.getSemesterArray(), self.label, self.id, \
                             self.studentid, self.studycode)

    def addToSemester(self, e):
        if e.semester not in self.semester:
            self.semester[e.semester] = []
            self.sects[e.semester] = 0
        self.semester[e.semester].append(e)
        self.sects[e.semester] += e.ects

    def getSemesterArray(self):
        out = []
        sem = list(self.semester.keys())
        sem.sort()
        for k in sem:
            out.append(self.semester[k])
        return out

    def getSemesterVars(self):
        out = {}
        sem = list(self.semester.keys())
        for k in sem:
            for ex in self.semester[k]:
                if k not in out:
                    out[k] = []
                add = ex.__dict__
                date = str(add['date'])
                add['date'] = date
                out[k].append(add)
        return out


    def getLineData(self):
        out = []
        sem = list(self.semester.keys())
        sem.sort()
        allsem = createSemesters(sem[0], sem[-1])
        for i, s in enumerate(allsem):
            out.append({'x': i, 'y': self.sects[s] if s in self.sects else 0})
        return {
            'id': self.id,
            'matnr': self.matnr,
            'label': self.label,
            'line': out,
            'semester': self.getSemesterVars(),
            'path': self.path.getPrintableShortPath()
        }
