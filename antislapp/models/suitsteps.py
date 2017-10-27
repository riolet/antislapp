import os
from antislapp import index
from antislapp.models import rtf
from antislapp.models import defence

template = """
1. Bringing a claim: Complete

You have been sued by someone and they started it by creating the statement of claim.

2. Defending a claim: In Progress

This is where we are right now. You've divided the allegations they made against you into things you accept, things you deny, and things you can't answer.

We took the facts you'll need later and listed them out in a statement of defence.

To do next: this statement needs to be proofread by you, filling in any missing information, and then printed out in a few copies.  You need to deliver a copy to everyone involved, including the court, the person suing you, and any other defendants.

3. Discovery

This is where you meet with the other team's lawyers and both of you show the other all the relevant documents you have, providing copies as needed. This is all your evidence like contracts, recordings, emails, etc. 

Beyond documents, you also meet up and ask each other questions each other's documents

4. Setting an action for trial

Either you or them can do this, it is notifying the court that the case is ready to be tried. It involves filing a trial record to all involved, and the court, and paying a court fee.

5. Pre-trial conference

This is a discussion between you and them and a judge, trying to simplify the case where possible, and determine how long the trial is expected to last. 

The possibility of settlements (agreeing to pay an amount instead of going to court) is usually brought up and decided here.

6. Trial

6.1 They (the plaintiff) and you (the defendant) make opening statements.
6.2 The plaintiff's witnesses are questioned by the plaintiff, then by the defendant.
6.3 The defendant's witnesses are questioned by the defendant, then by the plaintiff.
6.4 The plaintiff and defendant make their closing arguments.
6.5 The judge makes a judgement either right away in court, or later after considering. 
"""


class SuitSteps:
    OUTPATH = os.path.join(index.BASE_FOLDER, 'static', 'forms')

    def __init__(self, session_id):
        self.path = os.path.join(SuitSteps.OUTPATH, '{}_steps.rtf'.format(session_id))
        self.writer = rtf.RTF(self.path)
        self.template = template

    def populate(self, defence):
        """
        :param defence:
        :type defence: defence.Defence
        :return:
        """
        pass

    def write(self):
        # write to file.

        self.writer.append(self.template)

        if not os.path.exists(os.path.dirname(self.path)):
            os.makedirs(os.path.dirname(self.path))
        self.writer.write()

    def get_link(self):
        path = self.path
        i = path.find("/static")
        return path[i:]

