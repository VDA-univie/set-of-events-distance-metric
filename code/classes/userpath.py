import datetime

import exam
import progress
import student
import study

__all__ = ['create_user_student', 'create_user_students']

user_student_id = 0
user_start_semester = "2000W"
user_study = "999"
user_start_year = 2000
user_reason = "generated"
user_state = "generated"

def create_user_exam(name, matnr, semestercount, semester):
    ects = 6
    grade = 1
    year = user_start_year
    month = 1
    if semestercount % 2 == 1:
        semestercount -= 1
        month = 6
    date = datetime.date(year, month, 30)
    return exam.Exam(matnr, user_study, name, name, date, semester, ects, grade)

def create_user_progress(id, semestercount):
    matnr = "student" + str(id)
    year = user_start_year
    month = 10
    day = 1
    start = datetime.date(year, month, day)
    if semestercount % 2 == 1:
        month = 2
        year += 1 + (semestercount-1)/2
    elif semestercount == 0:
        day = 15
    else:
        month = 7
        year += semestercount/2
    end = datetime.date(int(year), month, day)
    return progress.Progress(id, matnr, user_study, start, end, user_reason, user_state)

def create_user_student(stringpath):
    semester = stringpath.split("-")
    exams = []
    global user_student_id
    id = user_student_id
    user_student_id += 1
    progress = create_user_progress(id, len(semester))
    semesternames = study.createSemesters(user_start_semester,
        study.changeSemester(user_start_semester, len(semester)-1))
    for i, sem in enumerate(semester):
        for c in sem:
            exams.append(create_user_exam(c, progress.matnr, i, semesternames[i]))
    return student.Student(progress.matnr, id, [progress], exams, stringpath)

def create_user_students(stringpaths):
    out = []
    for i, path in enumerate(stringpaths):
        out.append(create_user_student(path))
    return out
