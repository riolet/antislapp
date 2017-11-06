import os
import time
from itertools import count
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
        self.date = date.fromtimestamp(time.time()).strftime("%B %d, %Y")  # "September 07, 1998"
        self.claims_admitted = []
        self.claims_unanswered = []
        self.claims_denied = []
        self.was_defamatory = None
        self.was_damaging = None
        self.apology_given = None
        self.apology_date = ''
        self.apology_method = ''
        self.additional_facts = []
        self.defence_paragraphs = []

    def set_additional_facts(self, fact_paragraphs):
        self.additional_facts = fact_paragraphs

    def set_defences(self, paragraphs):
        self.defence_paragraphs = paragraphs

    @staticmethod
    def numbered_paragraph(n, p):
        p = "{}. {}\n".format(n, p)
        return p

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
                 "\nFax number address for service (if any):\t" + field,
                 "\nE-mail address for service (if any):\t\t" + field,
                 "\n\n\nDate:\t" + self.date + "\t\t\t" + field,
                 "\t\t\t\t\t\t" + "Signature of defendant " + self.defendant]
        return '\n'.join(lines)

    def build_part1(self):
        p_num = count(1)
        # Division 1
        paragraph = 'paragraph' if len(self.claims_admitted) == 1 else 'paragraphs'
        if self.claims_admitted:
            numbers = index.join_list([str(claim['paragraph']) for claim in self.claims_admitted])
        else:
            numbers = "NIL"
        p_agree = "The facts alleged in {} {} of Part 1 of the notice of civil claim are admitted."\
            .format(paragraph, numbers)

        paragraph = 'paragraph' if len(self.claims_denied) == 1 else 'paragraphs'
        if self.claims_denied:
            numbers = index.join_list([str(claim['paragraph']) for claim in self.claims_denied])
        else:
            numbers = 'NIL'
        p_deny = "The facts alleged in {} {} of Part 1 of the notice of civil claim are denied."\
            .format(paragraph, numbers)

        paragraph = 'paragraph' if len(self.claims_unanswered) == 1 else 'paragraphs'
        if self.claims_unanswered:
            numbers = index.join_list([str(claim['paragraph']) for claim in self.claims_unanswered])
        else:
            numbers = 'NIL'
        p_withheld = 'The facts alleged in {} {} of Part 1 of the notice of civil claim are outside the knowledge of the defendant {}'\
            .format(paragraph, numbers, self.defendant)

        lines = [
            self.writer.bold("Part 1: RESPONSE TO NOTICE OF CIVIL CLAIM FACTS\n"),
            self.writer.bold("Division 1 -- Defendant's Response to Facts\n"),
            self.numbered_paragraph(next(p_num), p_agree),
            self.numbered_paragraph(next(p_num), p_deny),
            self.numbered_paragraph(next(p_num), p_withheld),
            self.writer.bold("Division 2 -- Defendant's Version of Facts\n"),
        ]

        in_the_alternative = False
        alternative = "Further, and in the alternative, "
        paragraph = 'paragraphs' if len(self.claims_denied) > 1 else 'paragraph'
        numbers = index.join_list([str(claim['paragraph']) for claim in self.claims_denied])
        not_alternative = "Regarding allegations in {para} {numbers}, ".format(para=paragraph, numbers=numbers)


        if self.was_defamatory is False:
            lines.append(self.numbered_paragraph(next(p_num), not_alternative + "if the defendant {} made any statements about the plaintiff, those statements were not capable of being defamatory of the plaintiff, and were not in fact defamatory of the plaintiff, as alleged or at all.".format(self.defendant)))
            in_the_alternative = True

        for p_def in self.defence_paragraphs:
            if in_the_alternative:
                lines.append(self.numbered_paragraph(next(p_num), alternative + p_def))
            else:
                lines.append(self.numbered_paragraph(next(p_num), not_alternative + p_def))
            in_the_alternative = True

        if self.was_damaging is False:
            if in_the_alternative:
                lines.append(self.numbered_paragraph(next(p_num), alternative + "the defendant {} expressly denies that the plaintiff has suffered injury, loss, or damage as alleged or at all.".format(self.defendant)))

        if self.apology_given is True or len(self.additional_facts) > 0:
            lines.append(self.writer.bold("Division 3 -- Additional Facts\n"))
            if self.was_damaging is False:
                deny = "which is not admitted but expressly denied, "
            else:
                deny = ""
            lines.append(self.numbered_paragraph(next(p_num), alternative + "if the plaintiff has suffered injury, loss, or damage as alleged or at all, {}the defendant {} made a full and fair apology on {} by way of {}.".format(deny, self.defendant, self.apology_date, self.apology_method)))

            for p_fact in self.additional_facts:
                lines.append(self.numbered_paragraph(next(p_num), alternative + p_fact))

        return '\n'.join(lines)

    def build_part2(self):
        p_num = count(1)
        lines = [
            self.writer.bold("Part 2: RESPONSE TO RELIEF SOUGHT\n"),
            self.numbered_paragraph(next(p_num), "The defendant {} consents to the granting of the relief sought in paragraphs NIL of Part 2 of the notice of civil claim.".format(self.defendant)),
            self.numbered_paragraph(next(p_num), "The defendant {} opposes the granting of the relief sought in all paragraphs of Part 2 of the notice of civil claim.".format(self.defendant)),
            self.numbered_paragraph(next(p_num), "The defendant {} takes no position on the granting of the relief sought in paragraphs NIL of Part 2 of the notice of civil claim.".format(self.defendant)),
        ]
        return '\n'.join(lines)
    
    def build_part3(self):
        p_num = count(1)
        lines = [
            self.writer.bold("Part 3: LEGAL BASIS\n"),
            self.numbered_paragraph(next(p_num), "The common law including the common law relating to defamation and damages."),
            self.numbered_paragraph(next(p_num), "The common law relating to pleading claims for defamation and damages."),
        ]
        return '\n'.join(lines)

    def write(self):
        header = self.build_header()
        self.writer.append(header)

        part1 = self.build_part1()
        self.writer.append(part1)

        part2 = self.build_part2()
        self.writer.append(part2)

        part3 = self.build_part3()
        self.writer.append(part3)
        
        footer = self.build_footer()
        self.writer.append(footer)

        if not os.path.exists(os.path.dirname(self.path)):
            os.makedirs(os.path.dirname(self.path))
        self.writer.write()

    def get_link(self):
        path = self.path
        i = path.find("/static")
        return path[i:]
