def dateToSemester(date):
    semester = str(date.year)
    if(date.month > 2 and date.month < 10):
        semester += 'S'
    else:
        semester += 'W'
    return semester

class Progress:
    def __init__(self, identifier, matnr, study, start, end, reason, state):
        self.identifier     = identifier
        self.matnr          = matnr
        self.study          = study
        self.start          = start
        self.end            = end
        self.reason         = reason
        self.state          = state
        self.startSemester  = dateToSemester(start)
        self.endSemester    = dateToSemester(end)

    def __str__(self):
        return "Progress { \n\tidentifier: " + str(self.identifier) + \
        "\n\tmatnr: " + self.matnr + "\n\tstudy: " + str(self.study) + \
        "\n\tstart: " + str(self.start) + "\n\tend: " + str(self.end) + \
        "\n\tstartsem: " + str(self.startSemester) + \
        "\n\tendsem: " + str(self.endSemester) + \
        "\n\treason: " + self.reason + "\n\tstate: " + self.state + \
        "\n}"
