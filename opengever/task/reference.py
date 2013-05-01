from five import grok
from opengever.task.task import ITask
from opengever.base.interfaces import IReferenceNumber
from opengever.base.reference import BasicReferenceNumber


class TaskReferenceNumber(BasicReferenceNumber):
    """ Reference number adapter specially for task.
    For more information see base class BasicReferenceNumber.
    """

    grok.provides(IReferenceNumber)
    grok.context(ITask)

    def get_number(self):
        # get the parent number
        parent_num = self.get_parent_number()
        if parent_num:
            return str(parent_num)
        else:
            return ''
