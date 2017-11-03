import os
import time
from datetime import date
from antislapp import index
from antislapp.models import rtf


class FormS2600:
    OUTPATH = os.path.join(index.BASE_FOLDER, 'static', 'forms')
    def __init__(self, session_id):
        self.path = os.path.join(FormS2600.OUTPATH, '{}.rtf'.format(session_id))
        self.writer = rtf.RTF(self.path)
        self.court_name = "[name of court, from notice of claim]"
        self.plaintiff = "Their Name Here"
        self.defendant = "Your Name Here"
        self.fax_number = ""
        self.email = ""
        self.date = date.fromtimestamp(time.time()).strftime("%B %d, %Y")  # "September 07, 1998"
        self.admissions = []
        self.unanswered = []
        self.denials = []
        self.facts = []

    def build_header(self):

        court = self.court_name.upper()
        if court[:3] == "THE":
            court = "IN " + court
        else:
            court = "IN THE " + court
        lines = ["{}\n\n".format(court),
                 "BETWEEN:\n",
                 '{}\n({})'.format(self.writer.bold(self.plaintiff.upper()), self.writer.italic('Plaintiff')),
                 '\nAND:\n',
                 '{}\n({})'.format(self.writer.bold(self.defendant.upper()), self.writer.italic('Defendant')),
                 self.writer.bold(self.writer.underline('\n\nRESPONSE TO CIVIL CLAIM')) + '\n',
                 self.writer.bold('Filed By: \t{}').format(self.defendant) + ' (the "defendant")']
        return '\n'.join(lines)

    def build_footer(self):
        field = self.writer.underline(" "*60)
        lines = ["\nDefendant's address for service:\t\t" + field,
                 "\t\t\t\t\t\t" + field,
                 "\nFax number address for service (if any):\t" + (self.fax_number or "None"),
                 "\nE-mail address for service (if any):\t\t" + (self.email or "None"),
                 "\n\n\nDate:\t" + self.date + "\t\t\t" + field,
                 "\t\t\t\t\t\t" + "Signature of defendant " + self.defendant]
        return '\n'.join(lines)



    def write(self):
        header = self.build_header()
        self.writer.append(header)

        if not os.path.exists(os.path.dirname(self.path)):
            os.makedirs(os.path.dirname(self.path))
        self.writer.write()
