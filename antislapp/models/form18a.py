import os
from antislapp import index
from antislapp.models import rtf


class Form18A:
    OUTPATH = os.path.join(index.BASE_FOLDER, 'static', 'forms')
    def __init__(self, session_id):
        self.path = os.path.join(Form18A.OUTPATH, '{}.rtf'.format(session_id))
        self.writer = rtf.RTF(self.path)
        self.plaintiff = "Plaintiff"
        self.defendant = "Defendant"
        self.admitted = "..."
        self.denied = "..."
        self.unanswered = "..."
        self.date = 'Today' # TODO: build date like "September 13, 2017"

    def set_plaintiff(self, title):
        pass

    def set_defendant(self, title):
        pass

    def build_head(self):
        #
        lines = [
            'FORM 18A',
            self.writer.italic('Courts of Justice Act'),
            'B E T W E E N\n',
            '{} ({})'.format(self.plaintiff.upper(), self.writer.italic('Plaintiff')),
            '\n- and -\n',
            '{} ({})'.format(self.defendant.upper(), self.writer.italic('Defendant')),
            '\nSTATEMENT OF DEFENCE\n'
        ]
        return "\n".join(lines)

    def build_body(self):
        pass

    def build_tail(self):
        #{date}, {from}, TO: {to}
        pass

    def prepare(self):
        head = self.build_head()
        body = self.build_body()
        tail = self.build_tail()

        self.writer.append(head)
        self.writer.append(body)
        self.writer.append(tail)

        self.writer.write()
