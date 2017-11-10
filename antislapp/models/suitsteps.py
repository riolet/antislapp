import os
from antislapp import index
from antislapp.models import rtf
from antislapp.models.defence import Defence


class SuitSteps:
    OUT_PATH = os.path.join(index.BASE_FOLDER, 'static', 'forms')

    def __init__(self, session_id):
        self.path = os.path.join(SuitSteps.OUT_PATH, '{}_steps.rtf'.format(session_id))
        self.writer = rtf.RTF(self.path)

    def header(self):
        title = self.writer.bold(self.writer.underline("Defence Guide: Steps in your defence"))
        return title

    def step1(self):
        title = self.writer.bold("1. Bringing a claim:")
        progress = self.writer.italic(" Complete")
        content = "This is the statement of claim that they brought against you. " \
                  "It means you have been sued and it started this process."
        return "{}{}\n\n{}".format(title, progress, content)

    def step2(self):
        title = self.writer.bold("2. Defending a claim:")
        progress = self.writer.italic(" In Progress")
        paragraphs = [
            "This is where we are right now. You've divided the allegations they made against you into things "
            "you accept, things you deny, and things you can't answer.",

            "We took the facts you'll need later and listed them out in a statement of defence.",

            "To do next: this statement needs to be proofread by you--filling in any missing information--and then "
            "printed out in a few copies.  You need to deliver a copy to everyone involved, including the court, "
            "the person suing you, and any other defendants.",
        ]
        return "{}{}\n\n{}".format(title, progress, "\n\n".join(paragraphs))

    def step3(self):
        title = self.writer.bold("3. Discovery")
        paragraphs = [
            "This is where you meet with the other team's lawyers and both of you show the other all the "
            "relevant documents you have, providing copies as needed. This is all your evidence like "
            "contracts, recordings, emails, etc.",

            "This phase is also to determine exactly what the other person has to say, including anything they "
            "agree with you on and to try and get the other person to admit something that can be used against "
            "them later in trial.  There is no judge present for this, but a court reporter will be there.",
        ]
        return "{}\n\n{}".format(title, "\n\n".join(paragraphs))

    def step4(self):
        title = self.writer.bold("4. Setting an action for trial")
        content = "This is when you notify the court that the case is ready to be tried. Either you, or them, " \
                  "can do this. It involves filing a trial record to all involved, and the court, " \
                  "and paying a court fee."
        return "{}\n\n{}".format(title, content)

    def step5(self):
        title = self.writer.bold("5. Pre-trial conference")
        paragraphs = [
            "This is a discussion between you and them and a judge, trying to simplify the case where possible, "
            "and determine how long the trial is expected to last.",

            "The possibility of settlements (agreeing to pay an amount instead of going to court) is usually "
            "brought up and decided here.",
        ]
        return "{}\n\n{}".format(title, "\n\n".join(paragraphs))

    def step6(self):
        title = self.writer.bold("6. Trial")
        steps = [
            self.writer.italic("6.1") + " They (the plaintiff) and you (the defendant) make opening statements.",
            self.writer.italic("6.2") + " The plaintiff's witnesses are questioned by the plaintiff, "
                                        "then by the defendant.",
            self.writer.italic("6.3") + " The defendant's witnesses are questioned by the defendant, "
                                        "then by the plaintiff.",
            self.writer.italic("6.4") + " The plaintiff and defendant make their closing arguments.",
            self.writer.italic("6.5") + " The judge makes a judgement either right away in court, "
                                        "or later after considering."
        ]
        return "{}\n\n{}".format(title, "\n".join(steps))

    def populate(self, defence):
        """
        :param defence:
        :type defence: Defence
        :return:
        """
        # extract any variables needed from the defence (like plaintiff name, defences chosen, etc...)
        pass

    def write(self):
        # write to file.

        parts = [
            self.header(),
            self.step1(),
            self.step2(),
            self.step3(),
            self.step4(),
            self.step5(),
            self.step6(),
        ]

        self.writer.append("\n\n".join(parts))

        if not os.path.exists(os.path.dirname(self.path)):
            os.makedirs(os.path.dirname(self.path))
        self.writer.write()

    def get_link(self):
        path = self.path
        i = path.find("/static")
        return path[i:]
