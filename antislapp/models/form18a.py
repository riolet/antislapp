import os
from datetime import date
import time
from antislapp import index
from antislapp.models import rtf


class Form18A:
    OUTPATH = os.path.join(index.BASE_FOLDER, 'static', 'forms')
    def __init__(self, session_id):
        self.path = os.path.join(Form18A.OUTPATH, '{}.rtf'.format(session_id))
        self.writer = rtf.RTF(self.path)
        self.plaintiff = "Their Name Here"
        self.defendant = "Your Name Here"
        self.date = date.fromtimestamp(time.time()).strftime("%B %d, %Y")  # "September 07, 1998"
        self.admissions = []
        self.unanswered = []
        self.denials = []
        self.facts = []

    def set_plaintiff(self, title):
        """
        :type title: str
        """
        self.plaintiff = title

    def set_defendant(self, title):
        """
        :type title: str
        """
        self.defendant = title

    def set_admissions(self, admissions):
        """
        :type admissions: list [ str ]
        """
        self.admissions = admissions

    def set_unanswered(self, unanswered):
        """
        :type unanswered: list[ str ]
        """
        self.unanswered = unanswered

    def set_denials(self, denials):
        """
        :type denials: list[ str ]
        """
        self.denials = denials

    def set_facts(self, facts):
        """
        :type facts: list[ str ]
        """
        self.facts = facts

    def build_head(self):
        lines = [
            'FORM 18A',
            self.writer.italic('Courts of Justice Act'),
            '\n\nB E T W E E N\n',
            '{}\n({})'.format(self.writer.bold(self.plaintiff.upper()), self.writer.italic('Plaintiff')),
            '\n- and -\n',
            '{}\n({})'.format(self.writer.bold(self.defendant.upper()), self.writer.italic('Defendant')),
            '\nSTATEMENT OF DEFENCE\n\n'
        ]
        return '\n'.join(lines)

    def numbered_paragraph(self, n, p):
        p = "{}. {}\n".format(n, p)
        return p

    def build_body(self):
        # 1. accusations agreed with.
        # 2. accusations refuted.
        # 3. accusations unanswered.
        # 4+. consecutive numbered paragraphs detailing the relevant facts to be used.
        #
        if self.admissions:
            paragraph = 'paragraphs' if len(self.admissions) > 1 else 'paragraph'
            numbers = index.join_list([str(claim['paragraph']) for claim in self.admissions])
            p_agree = "The defendant admits the allegations contained in {} {} of the statement of claim."\
                .format(paragraph, numbers)
        else:
            p_agree = "The defendant admits none of the allegations in the statement of claim."

        if self.denials:
            paragraph = 'paragraphs' if len(self.denials) > 1 else 'paragraph'
            numbers = index.join_list([str(claim['paragraph']) for claim in self.denials])
            p_deny = "The defendant denies the allegations contained in {} {} of the statement of claim."\
                .format(paragraph, numbers)
        else:
            p_deny = "The defendant denies none of the allegations in the statement of claim."

        if self.unanswered:
            paragraph = 'paragraphs' if len(self.unanswered) > 1 else 'paragraph'
            numbers = index.join_list([str(claim['paragraph']) for claim in self.unanswered])
            p_withheld = 'The defendant has no knowledge in respect of the allegations contained in {} {} of' \
                         ' the statement of claim.'\
                .format(paragraph, numbers)
        else:
            p_withheld = 'There are no paragraphs in the statement of claim that the defendant cannot answer.'

        lines = [
            self.numbered_paragraph(1, p_agree),
            self.numbered_paragraph(2, p_deny),
            self.numbered_paragraph(3, p_withheld),
        ]
        for i, fact in enumerate(self.facts):
            p = self.numbered_paragraph(i+4, fact)
            lines.append(p)

        return '\n'.join(lines)

    def build_tail(self):
        #{date}, {from}, TO: {to}
        lines = [
            '\n',
            self.date,
            '\n',
            self.writer.bold(self.defendant),
            '(defendant address here)',
            '\n\nTO:\n',
            self.writer.bold(self.plaintiff),
            '(plaintiff address here)',
            '\nRCP-E 18A (July 1, 2007)'
        ]
        return '\n'.join(lines)

    def write(self):
        head = self.build_head()
        body = self.build_body()
        tail = self.build_tail()

        self.writer.append(head)
        self.writer.append(body)
        self.writer.append(tail)

        if not os.path.exists(os.path.dirname(self.path)):
            os.makedirs(os.path.dirname(self.path))
        self.writer.write()

    def get_link(self):
        path = self.path
        i = path.find("/static")
        return path[i:]

def test():
    r1 = Form18A('session1')
    r1.write()

    r2 = Form18A('session2')
    r2.set_defendant("Mr. Def")
    r2.set_plaintiff("Mr. Plaint")
    r2.set_admissions(['4', '5', '7', '10'])
    r2.set_denials(['1', '2', '6', '9'])
    r2.set_unanswered(['3', '8'])
    r2.set_facts(['facts article A', 'facts article B', 'facts article C'])
    r2.write()
