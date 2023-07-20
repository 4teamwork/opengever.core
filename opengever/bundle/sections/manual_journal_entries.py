from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.utils import traverse
from DateTime import DateTime
from ftw.journal.interfaces import IJournalizable
from opengever.journal.manager import JournalManager
from plone import api
from plone.dexterity.utils import datify
from Products.CMFPlone.utils import safe_unicode
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
        self.items_with_journal_entries = []
        self.catalog = api.portal.get_tool('portal_catalog')

    def __iter__(self):
        for item in self.previous:
            if item.get('_journal_entries'):
                self.items_with_journal_entries.append(item)

            yield item

        # We make sure to add journal entries after everything else is done
        # so that we are sure that documents referenced in related_documents
        # actually exist.
        for item in self.items_with_journal_entries:
            path = item.get('_path')
            if not path:
                log.warning("Cannot set journal entries for {}. "
                            "Object doesn't have a path".format(path))
                continue

            obj = traverse(self.context, path, None)
            if obj is None:
                log.warning("Cannot set journal entries for {}. "
                            "Object doesn't exist".format(path))
                continue

            if not IJournalizable.providedBy(obj):
                log.warning("Cannot set journal entries for {}. "
                            "Object does not provide IJournalizable".format(path))
                continue

            self.add_journal_entries(obj, item)

    def add_journal_entries(self, obj, item):
        journal_entries = item.get('_journal_entries')
        for journal_entry in journal_entries:
            comment = safe_unicode(journal_entry.get('comment'))
            category = journal_entry.get('category', DEFAULT_COMMENT_CATEGORY)
            documents = [self.resolve_guid(guid) for guid in
                         journal_entry.get('related_documents', [])]
            documents = filter(None, documents)
            time = datify(journal_entry.get('time', DateTime()))
            actor = journal_entry.get('actor')
            JournalManager(obj).add_manual_entry(
                category, comment, documents, time, actor=actor)

    def resolve_guid(self, guid):
        results = self.catalog.unrestrictedSearchResults(bundle_guid=guid)
        if len(results) == 0:
            log.warning(
                u"Couldn't find object with GUID %s in catalog" % guid)
            return

        if len(results) > 1:
            # Ambiguous GUID - this should never happen
            log.warning(
                u"Ambiguous GUID! Found more than one result in catalog "
                u"for GUID %s " % guid)
            return

        return results[0].getObject()
