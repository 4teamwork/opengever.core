from five import grok
from opengever.task.task import ITask
from opengever.base.interfaces import IReferenceNumber
from opengever.base.reference import BasicReferenceNumber


class DocumentReferenceNumber(BasicReferenceNumber):
    """ Reference number for documents
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
