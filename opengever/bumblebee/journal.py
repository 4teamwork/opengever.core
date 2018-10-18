from ftw.bumblebee.interfaces import IBumblebeeable
from ftw.bumblebee.interfaces import IBumblebeeJournal
from logging import getLogger
from zope.component import adapter
from zope.interface import implementer
from plone.uuid.interfaces import IUUID


logger = getLogger('opengever.bumblebee')


@implementer(IBumblebeeJournal)
@adapter(IBumblebeeable)
class BumblebeeLogfileJournal(object):
    """Bumblebee journal implementation that logs to files instead of writing
    to persistent objects.

    This is mainly to avoid DB bloat and ConflictErrors that otherwise happen
    because ftw.bumblebee is very verbose in its journalling, and uses
    monotonically increasing timestamps as keys that make ConflictErrors
    likely.
    """

    def __init__(self, context):
        self.context = context

    def add(self, message, **details):
        uuid = IUUID(self.context, '<no-uuid>')
        logger.info('%s: %s (%r)' % (uuid, message, details))

    def as_json(self, *args, **kwargs):
        raise NotImplementedError

    def items(self):
        raise NotImplementedError
