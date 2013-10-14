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

    ref_type = 'document'

    def get_local_number(self):
        num = getUtility(ISequenceNumber).get_number(self.context)
        return num and str(num) or ''
