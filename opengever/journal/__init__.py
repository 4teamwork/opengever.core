from opengever.journal.interfaces import IManualJournalActor
from zope.globalrequest import getRequest
from zope.i18nmessageid import MessageFactory
from zope.interface import alsoProvides
from zope.interface import noLongerProvides


_ = MessageFactory('opengever.journal')


class ManualJournalActor(object):
    """Contextmanager that temporarily creates journal entry for the given
    actor, instaed of the current user.
    """

    def __init__(self, actor):
        self.actor = actor

    def __enter__(self):
        request = getRequest()
        alsoProvides(request, IManualJournalActor)
        request.set('_manual_journal_actor', self.actor)

    def __exit__(self, exc_type, exc_val, exc_tb):
        request = getRequest()
        noLongerProvides(request, IManualJournalActor)
        request.other.pop('_manual_journal_actor')
