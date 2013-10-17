from ftw.journal.config import JOURNAL_ENTRIES_ANNOTATIONS_KEY
from zope.annotation.interfaces import IAnnotations


def get_journal_length(obj):
    """ Get the lenght of the journal
    """
    return len(IAnnotations(
        obj, JOURNAL_ENTRIES_ANNOTATIONS_KEY).get(
            JOURNAL_ENTRIES_ANNOTATIONS_KEY))


def get_journal_entry(obj, entry=-1):
    journal = IAnnotations(
        obj, JOURNAL_ENTRIES_ANNOTATIONS_KEY).get(
        JOURNAL_ENTRIES_ANNOTATIONS_KEY)[entry]

    return journal
