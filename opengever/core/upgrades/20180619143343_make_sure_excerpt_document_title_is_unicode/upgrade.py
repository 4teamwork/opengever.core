from ftw.journal.config import JOURNAL_ENTRIES_ANNOTATIONS_KEY
from ftw.journal.interfaces import IAnnotationsJournalizable
from opengever.base.archeologist import Archeologist
from opengever.core.upgrade import SQLUpgradeStep
from opengever.ogds.base.utils import get_current_admin_unit
from plone import api
from Products.CMFPlone.utils import safe_unicode
from sqlalchemy.sql.expression import column
from sqlalchemy.sql.expression import table
from zope.annotation.interfaces import IAnnotations
from zope.app.intid.interfaces import IIntIds
from zope.component import getUtility
from zope.i18nmessageid import Message


excerpts_table = table(
    'excerpts',
    column('excerpt_admin_unit_id'),
    column('excerpt_int_id'),
)


generateddocuments_table = table(
    'generateddocuments',
    column('generated_document_type'),
    column('admin_unit_id'),
    column('int_id'),
)


class MakeSureExcerptDocumentTitleIsUnicode(SQLUpgradeStep):
    """Make sure excerpt document title is unicode.

    also fix:
    - title of document's versions
    - persisted title in i18n messages of the journal

    """

    deferrable = True

    def migrate(self):
        has_meeting_feature = api.portal.get_registry_record(
            'opengever.meeting.interfaces.IMeetingSettings.is_feature_enabled')
        if not has_meeting_feature:
            return

        self.admin_unit_id = get_current_admin_unit().id()
        self.intids = getUtility(IIntIds)
        self.repository = api.portal.get_tool('portal_repository')
        self.journal_fixer = JournalMessageFixer(keys_to_fix=['title'])

        self.migrate_ad_hoc_excerpts()
        self.migrate_submitted_proposal_excerpts()
        self.migrate_excerpts_in_dossiers()

    def fix_document_title(self, document):
        """Make sure document title is unicode."""
        if not document:
            return

        document.title = safe_unicode(document.title)

        for version in self.repository.getHistory(document):
            archived_document = Archeologist(document, version).excavate()
            archived_document.title = safe_unicode(archived_document.title)
            archived_document._p_changed = True

        self.journal_fixer.fix_entries(document)

    def migrate_ad_hoc_excerpts(self):
        """Migrate excerpts for ad-hoc agenda items.

        These excerpts are stored in the meeting dossier.
        """
        excerpts = self.execute(
                excerpts_table.select()
                .where(excerpts_table.c.excerpt_admin_unit_id == self.admin_unit_id)
            ).fetchall()
        for excerpt in excerpts:
            excerpt_document = self.intids.queryObject(excerpt.excerpt_int_id)
            self.fix_document_title(excerpt_document)

    def migrate_submitted_proposal_excerpts(self):
        """Migrate excerpts for proposals.

        These excerpts are stored in the submitted proposal in a committee.
        """
        for submitted_proposal in self.objects(
                {'portal_type': 'opengever.meeting.submittedproposal'},
                'Fix submitted proposal excerpts title.'):
            excerpts = self.get_submitted_proposal_excerpts(submitted_proposal)
            for excerpt_document in excerpts:
                self.fix_document_title(excerpt_document)

    def get_submitted_proposal_excerpts(self, submitted_proposal):
        """Copy of SubmittedProposal.get_excerpts but omitting the sorting
        as that may trigger errors before THIS upgrade is run.
        """
        excerpts = []
        for relation_value in getattr(submitted_proposal, 'excerpts', ()):
            obj = relation_value.to_object
            excerpts.append(obj)

        return excerpts

    def migrate_excerpts_in_dossiers(self):
        """Migrate excerpts that were returned to dossier of their proposal."""

        excerpts = self.execute(
                generateddocuments_table.select()
                .where(generateddocuments_table.c.admin_unit_id == self.admin_unit_id)
                .where(generateddocuments_table.c.generated_document_type == 'generated_excerpt')
            ).fetchall()
        for excerpt in excerpts:
            excerpt_document = self.intids.queryObject(excerpt.int_id)
            self.fix_document_title(excerpt_document)


class JournalMessageFixer(object):
    """Fixes encoding for zope.i18nmessageid.Message mapping values, for
    journal entries of objects.

    Copied from https://github.com/4teamwork/opengever.maintenance/pull/90.
    """
    def __init__(self, keys_to_fix=None):
        self.keys_to_fix = keys_to_fix if keys_to_fix else []

    def get_journal_entries(self, obj):
        """Returns all journal entries for the given object.
        """
        if IAnnotationsJournalizable.providedBy(obj):
            annotations = IAnnotations(obj)
            return annotations.get(JOURNAL_ENTRIES_ANNOTATIONS_KEY, [])

        return []

    def fix_entries(self, obj):
        for entry in self.get_journal_entries(obj):
            message = entry['action'].get('title')
            if message and isinstance(message, Message) and message.mapping:
                if self.needs_fixing(message):
                    self.fix_message(entry, message)

    def needs_fixing(self, message):
        for key in self.keys_to_fix:
            if key in message.mapping:
                value = message.mapping[key]
                if not isinstance(value, unicode):
                    return True
        return False

    def fix_message(self, entry, old_message):
        """Replaces the existing Messsage object with a new one,
        with mapping values in the correct encoding (unicode).
        Just replacing the mapping value is not enough, because the
        journal store (a persistent dict) is not marked as changed.
        """
        mapping = old_message.mapping
        for key in mapping.keys():
            if key in self.keys_to_fix:
                value = mapping[key]
                if not isinstance(value, unicode):
                    mapping[key] = value.decode('utf-8')

        entry['action']['title'] = Message(
            unicode(old_message), domain=old_message.domain,
            default=old_message.default, mapping=mapping)
