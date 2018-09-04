from ftw.journal.config import JOURNAL_ENTRIES_ANNOTATIONS_KEY
from ftw.journal.interfaces import IAnnotationsJournalizable
from opengever.core.upgrade import SQLUpgradeStep
from opengever.ogds.base.utils import get_current_admin_unit
from plone import api
from sqlalchemy.sql.expression import column
from sqlalchemy.sql.expression import table
from zope.annotation.interfaces import IAnnotations
from zope.app.intid.interfaces import IIntIds
from zope.component import getUtility
from zope.i18nmessageid import Message


generateddocuments_table = table(
    'generateddocuments',
    column('generated_document_type'),
    column('admin_unit_id'),
    column('int_id'),
    )


class FixDossierJournalEntriesOfBrokenTitledMeetingExcerpts(SQLUpgradeStep):
    """Fix dossier journal entries of broken-titled meeting excerpts."""

    def migrate(self):
        has_meeting_feature = api.portal.get_registry_record('opengever.meeting.interfaces.IMeetingSettings.is_feature_enabled')  # noqa

        if not has_meeting_feature:
            return

        admin_unit_id = get_current_admin_unit().id()
        excerpts = self.execute(
            generateddocuments_table.select()
            .where(generateddocuments_table.c.admin_unit_id == admin_unit_id)
            .where(generateddocuments_table.c.generated_document_type == 'generated_excerpt')
            ).fetchall()

        if not excerpts:
            return

        intid_util = getUtility(IIntIds)
        dossiers = set(
            excerpt.get_parent_dossier()
            for excerpt in (intid_util.queryObject(excerpt.int_id) for excerpt in excerpts if excerpt.int_id)
            if excerpt
            )

        journal_fixer = JournalMessageFixer(keys_to_fix=['title'])
        for dossier in dossiers:
            journal_fixer.fix_entries(dossier)


class JournalMessageFixer(object):
    """Fixes encoding for zope.i18nmessageid.Message mapping values, for
    journal entries of objects.
    Copied from https://github.com/4teamwork/opengever.maintenance/pull/90.
    """

    def __init__(self, keys_to_fix=None):
        self.keys_to_fix = keys_to_fix if keys_to_fix else []

    def get_journal_entries(self, obj):
        """Returns all journal entries for the given object."""
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
            unicode(old_message),
            domain=old_message.domain,
            default=old_message.default,
            mapping=mapping,
            )
