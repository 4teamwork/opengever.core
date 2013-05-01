
from Acquisition import aq_inner
from Products.Five.browser import BrowserView
from zope.annotation.interfaces import IAnnotations, IAnnotatable
from zope.interface import alsoProvides

from ftw.journal.interfaces import IAnnotationsJournalizable, IWorkflowHistoryJournalizable
from ftw.journal.config import JOURNAL_ENTRIES_ANNOTATIONS_KEY

class JournalHistory(BrowserView):
    """ BrowserView listing the journal history
    """

    def __init__(self, context, *args, **kwargs):
        self.context = aq_inner(context)
        alsoProvides(self.context, IAnnotatable)
        super(JournalHistory, self).__init__(context, *args, **kwargs)

    def data(self):
        """
        """
        context = self.context
        history = []


        if IAnnotationsJournalizable.providedBy(self.context):
            annotations = IAnnotations(context)
            return annotations.get(JOURNAL_ENTRIES_ANNOTATIONS_KEY, [])
        elif IWorkflowHistoryJournalizable.providedBy(self.context):
            raise NotImplemented
