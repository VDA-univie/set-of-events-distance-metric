import study

def extractPaths(students):
    out = []
    for student in students:
        for study in student.studies:
            out += [study.path]
    return out

def extractTrimmedPaths(students, sem):
    out = []
    for stdnt in students:
        for stdy in stdnt.studies:
            if len(stdy.path.semester) > sem and len(stdy.exams) != 0:
                p = stdy.path
                p.trimSemesters(sem)
                out += [p]
    return out

def extractStudies(students):
    out = []
    for student in students:
        out += student.studies
    return out

def getStudentByMatNr(students, id):
    return [x for x in students if x.matnr == id]

def getStudentById(students, id):
    search = 0
    if(isinstance(id, str)):
        if '-' in id:
            search = int(id.split('-')[0])
        else:
            search = int(id)
    elif(isinstance(id, int)):
        search = id
    else:
        return "not string or int"
    return next((x for x in students if x.id == search), None)

def filterStudyPaths(students, startsemester = None, endsemester = None, \
    ects = None, state = None, studycode = None, id = None):
    out = []
    for istudent in students:
        for istudy in istudent.studies:
            add = True
            if not istudy.path.isEmpty():
                if startsemester is not None:
                    if isinstance(startsemester, list):
                        if len(startsemester) > 1:
                            add = startsemester[0] <= istudy.progress.startSemester \
                            and startsemester[1] >= istudy.progress.startSemester
                        else:
                            add = startsemester[0] <= istudy.progress.startSemester
                    else:
                        add = startsemester <= istudy.progress.startSemester
                if endsemester is not None and add is True:
                    if isinstance(endsemester, list):
                        if len(endsemester) > 1:
                            add = endsemester[0] <= istudy.progress.endSemester \
                            and endsemester[1] >= istudy.progress.endSemester
                        else:
                            add = endsemester[0] <= istudy.progress.endSemester
                    else:
                        add = endsemester <= istudy.progress.endSemester
                if ects is not None and add is True:
                    if isinstance(ects, list):
                        if len(ects) > 1:
                            add = ects[0] <= istudy.path.ects \
                            and ects[1] >= istudy.path.ects
                        else:
                            add = ects[0] <= istudy.path.ects
                    else:
                        add = ects <= istudy.path.ects
                if state is not None and add is True:
                    add = state == istudy.progress.state
                if studycode is not None and add is True:
                    if isinstance(studycode, list):
                        add = istudy.studycode in studycode
                    else:
                        add = studycode == istudy.studycode
                if id is not None and add is True:
                    if isinstance(id, list):
                        add = istudy.id in id
                    else:
                        add = id == istudy.id
                if add is True:
                    out.append(istudy.path)
    return out

class Student:
    def __init__(self, matnr, id, progresses, exams = None, label = ''):
        self.matnr      = matnr
        self.id         = id
        self.label = label

        self.progresses = progresses
        if exams is None:
            self.exams = []
        else:
            self.exams = exams
        self.studies    = []

        if len(exams): self.createStudies()

    def createStudies(self):
        sorted = {}
        for e in self.exams:
            if e.study not in sorted: sorted[e.study] = []
            sorted[e.study].append(e)
        for k, v in sorted.items():
            self.studies.append(
                study.Study(k, self.id, self.matnr, sorted[k],
                    next((item for item in self.progresses if item.study == k)),
                    self.label
                )
            )

    def __str__(self):
        out = str(self.id) + ":\n"
        for p in self.progresses:
            out += str(p) + "\n"
        return out
