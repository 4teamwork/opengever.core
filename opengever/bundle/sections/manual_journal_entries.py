from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.utils import traverse
from DateTime import DateTime
from ftw.journal.interfaces import IJournalizable
from opengever.journal.manager import JournalManager
from plone.dexterity.utils import datify
from zope.interface import classProvides
from zope.interface import implements
import logging


log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


DEFAULT_COMMENT_CATEGORY = 'information'


class ManualJournalEntriesSection(object):
    """Add manual journal entries
    """

    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.context = transmogrifier.context

    def __iter__(self):
        for item in self.previous:
            if not item.get('_journal_entries'):
                yield item
                continue

            path = item.get('_path')
            if not path:
                log.warning("Cannot set journal entries for {}. "
                            "Object doesn't have a path".format(path))
                yield item
                continue

            obj = traverse(self.context, path, None)
            if obj is None:
                log.warning("Cannot set journal entries for {}. "
                            "Object doesn't exist".format(path))
                yield item
                continue

            if not IJournalizable.providedBy(obj):
                log.warning("Cannot set journal entries for {}. "
                            "Object does not provide IJournalizable".format(path))
                yield item
                continue

            self.add_journal_entries(obj, item)

            yield item

    def add_journal_entries(self, obj, item):
        journal_entries = item.get('_journal_entries')
        for journal_entry in journal_entries:
            comment = journal_entry.get('comment')
            category = journal_entry.get('category', DEFAULT_COMMENT_CATEGORY)
            documents = journal_entry.get('related_documents', [])
            time = datify(journal_entry.get('time', DateTime()))
            actor = journal_entry.get('actor')
            JournalManager(obj).add_manual_entry(
                category, comment, documents, time, actor=actor)
