from opengever.base.interfaces import ISequenceNumber
from opengever.base.reference import BasicReferenceNumber
from opengever.document.behaviors import IBaseDocument
from zope.component import adapter
from zope.component import getUtility


@adapter(IBaseDocument)
class DocumentReferenceNumber(BasicReferenceNumber):
    """ Reference number for documents
    """
    ref_type = 'document'

    def get_local_number(self):
        num = getUtility(ISequenceNumber).get_number(self.context)
        return num and str(num) or ''
