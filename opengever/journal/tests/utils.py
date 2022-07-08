from opengever.journal.manager import JournalManager


def get_journal_length(obj):
    """ Get the lenght of the journal
    """
    return JournalManager(obj).count()


def get_journal_entry(obj, entry=-1):
    return JournalManager(obj).list()[entry]
