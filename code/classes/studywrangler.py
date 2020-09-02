import study
import path
import progress
import exam

class StudyWrangler:
    def __init__(self, studies):
        self.studies = studies

    def get_all_line_data(self):
        return study.getAllLineData(self.studies)

    def get_all_paths(self):
        return study.getAllPaths(self.studies)

    def get_all_metadata(self):
        out = []
        for p in self.get_all_paths():
            if(p.ects != 0):
                out.append({
                        'label': p.label,
                        'semester': p.getLength(),
                        'ects': p.ects,
                        'studyid': p.studyid,
                        'state': p.state,
                        'peak': p.getPeakSemesterECTS(),
                        'meansemesterects': p.getMeanSemesterECTS(),
                        'startsemester': p.getFirstSemester(),
                        'meangrade': p.getMeanGrade(),
                        'mediangrade': p.getMedianGrade()
                    })

        return out
