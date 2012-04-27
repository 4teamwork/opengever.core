from five import grok
from opengever.base.interfaces import IReferenceNumber
from opengever.base.interfaces import ISequenceNumber
from opengever.base.reference import BasicReferenceNumber
from opengever.document.behaviors import IBaseDocument
from zope.component import getUtility


class DocumentReferenceNumber(BasicReferenceNumber):
    """ Reference number for documents
    """
    grok.provides(IReferenceNumber)
    grok.context(IBaseDocument)

    def get_number(self):
        # get local sequence_number
        sequenceNr = getUtility(ISequenceNumber)
        num = sequenceNr.get_number(self.context)
        num = num and str(num) or ''
        # get the parent number
        parent_num = self.get_parent_number()
        if parent_num:
            return str(parent_num) + ' / ' + num
        else:
            return num
