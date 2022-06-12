
from Acquisition import aq_inner
from ftw.journal.config import JOURNAL_ENTRIES_ANNOTATIONS_KEY
from ftw.journal.interfaces import IAnnotationsJournalizable
from ftw.journal.interfaces import IWorkflowHistoryJournalizable
from Products.Five.browser import BrowserView
from zope.annotation.interfaces import IAnnotatable
from zope.annotation.interfaces import IAnnotations
from zope.interface import alsoProvides


class JournalHistory(BrowserView):
    """BrowserView listing the journal history."""

    def __init__(self, context, *args, **kwargs):
        self.context = aq_inner(context)
        alsoProvides(self.context, IAnnotatable)
        super(JournalHistory, self).__init__(context, *args, **kwargs)

    def data(self):
        if IAnnotationsJournalizable.providedBy(self.context):
            annotations = IAnnotations(self.context)
            return annotations.get(JOURNAL_ENTRIES_ANNOTATIONS_KEY, [])
        elif IWorkflowHistoryJournalizable.providedBy(self.context):
            raise NotImplementedError
