# -*- coding: utf-8 -*-
from DateTime import DateTime
from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testing import freeze
from opengever.exportng.tests.base import MODIFIED
from opengever.exportng.tests.base import SYNC_1
from opengever.exportng.tests.base import SYNC_2
from opengever.exportng.tests.base import SYNC_3
from opengever.exportng.tests.base import SYSTEM_COLUMNS
from opengever.exportng.tests.layer import EXPORTNG_DB_INTEGRATION_TESTING
from opengever.journal.manager import JournalManager
from opengever.testing import IntegrationTestCase
from unittest import skip
import pytz


CREATED = datetime(2026, 5, 19, 10, 0, tzinfo=pytz.utc)
REPOFOLDER_UID = u'createrepositorytree000000000003'
USER = u'robert.ziegler@gever.local'
RESOLVED_TITLE = u'Dossier state changed to dossier-state-resolved'

NOT_UPDATED = (
    u'The syncer does not update the additional tables of modified objects '
    u'yet.')
NOT_DELETED = (
    u'The syncer does not flag the additional table rows of deleted objects '
    u'yet.')


class JournalExportTestCase(IntegrationTestCase):
    """Tests for the `journal_entries` and `remarks` tables.

    The tables are filled by the dossier and document syncers. Rows are
    identified by their columns, there is no primary key. Each test runs the
    syncers with new instances and a frozen time, like in `SyncerTestMixin`.
    """

    layer = EXPORTNG_DB_INTEGRATION_TESTING

    def setUp(self):
        super(JournalExportTestCase, self).setUp()
        # Import lazily: the db module reads the DSN at import time, which is
        # set by the layer.
        from opengever.exportng.db import metadata
        from opengever.exportng.sync import Syncer
        metadata.drop_all()
        metadata.clear()
        Syncer().create_tables()
        self.metadata = metadata
        self.login(self.manager)
        self.user = u'admin'

    # Sync helpers

    def sync_dossiers(self, at):
        from opengever.exportng.catalog import DossierSyncer
        with freeze(at):
            DossierSyncer().sync()

    def sync_documents(self, at):
        from opengever.exportng.catalog import DocumentSyncer
        with freeze(at):
            DocumentSyncer().sync()

    def sync_all(self, at):
        self.sync_dossiers(at)
        self.sync_documents(at)

    # Content helpers

    def modify(self, obj):
        """Modify and reindex `obj`, so that the next sync updates it."""
        with freeze(MODIFIED):
            obj.reindexObject()

    def add_entry(self, obj, action, title=None, **kwargs):
        with freeze(MODIFIED):
            JournalManager(obj).add_auto_entry(
                action, title or action, **kwargs)

    def add_remark(self, obj, comment, **kwargs):
        with freeze(MODIFIED):
            JournalManager(obj).add_manual_entry(
                kwargs.pop('category', 'information'), comment, **kwargs)

    def create_document(self, dossier, title=u'Journal'):
        with freeze(CREATED):
            return create(Builder('document').within(dossier).titled(title))

    # Row helpers

    def rows(self, table, *uids):
        """All rows (deleted ones included) of the given table, which belong
        to one of the given objects, without the system columns, except for
        `_deleted`. Sorted, so the result is comparable.
        """
        from opengever.exportng.db import engine
        with engine.connect() as conn:
            rows = [dict(row.items()) for row in conn.execute(
                self.metadata.tables[table].select()).fetchall()]
        keep = [
            {k: v for k, v in row.items()
             if k not in SYSTEM_COLUMNS or k == '_deleted'}
            for row in rows
            if row['objexternalkey'] in uids
            or row.get('historyobject') in uids]
        return sorted(keep, key=lambda row: sorted(row.items()))

    def journal(self, *uids):
        return self.rows('journal_entries', *uids)

    def remarks(self, *uids):
        return self.rows('remarks', *uids)

    def active(self, rows):
        return [row for row in rows if not row['_deleted']]

    def journal_row(self, key, event, timestamp, journal='dossiers',
                    historyobject=None, user=None, deleted=False):
        return {
            'objexternalkey': key,
            'historyobject': historyobject,
            'event': event,
            'timestamp': timestamp,
            'user': user or self.user,
            '_journal': journal,
            '_deleted': deleted,
        }

    def remark_row(self, key, remark, category=u'Information', time=None,
                   references=None, user=None, deleted=False):
        return {
            'objexternalkey': key,
            'user': user or self.user,
            'date': time,
            'remark': remark,
            'event': category,
            'references': references or [],
            '_deleted': deleted,
        }

    def flagged(self, rows, deleted=True):
        return [dict(row, _deleted=deleted) for row in rows]


class TestDossierJournalExport(JournalExportTestCase):

    def setUp(self):
        super(TestDossierJournalExport, self).setUp()
        self.target = self.empty_dossier
        self.uid = self.target.UID()
        # The dossier added entry of the fixture
        self.created = self.journal_row(
            self.uid, u'OBJECT_CREATED', datetime(2016, 8, 31, 16, 39, 33),
            historyobject=REPOFOLDER_UID, user=USER)

    def test_initial_sync_exports_journal_entries(self):
        self.add_entry(self.target, 'Dossier state changed', RESOLVED_TITLE)

        self.sync_dossiers(SYNC_1)

        self.assertEqual(
            [self.created,
             self.journal_row(self.uid, u'DOSSIER_CLOSED', MODIFIED_AT)],
            self.sorted(self.journal(self.uid)))

    def test_initial_sync_ignores_unmapped_journal_entries(self):
        self.add_entry(self.target, 'Dossier modified')

        self.sync_dossiers(SYNC_1)

        self.assertEqual([self.created], self.journal(self.uid))

    def test_initial_sync_exports_manual_entries_as_remarks_only(self):
        self.add_remark(
            self.target, u'<p>Hello <b>World</b></p>',
            category='phone-call', documents=[self.document],
            time=DateTime('2026/05/20 09:15:00 GMT+0'))

        self.sync_dossiers(SYNC_1)

        self.assertEqual([self.created], self.journal(self.uid))
        self.assertEqual(
            [self.remark_row(
                self.uid, u'Hello **World**\n\n',
                category=u'Telefongespr\xe4ch',
                time=datetime(2026, 5, 20, 9, 15),
                references=[self.document.UID()])],
            self.remarks(self.uid))

    def test_consecutive_sync_without_changes_changes_nothing(self):
        self.add_remark(self.target, u'Hello')
        self.sync_dossiers(SYNC_1)
        journal, remarks = self.journal(self.uid), self.remarks(self.uid)
        self.assertEqual(1, len(remarks))

        self.sync_dossiers(SYNC_2)

        self.assertEqual(journal, self.journal(self.uid))
        self.assertEqual(remarks, self.remarks(self.uid))

    @skip(NOT_UPDATED)
    def test_update_exports_new_journal_entries_once(self):
        self.sync_dossiers(SYNC_1)

        self.add_entry(self.target, 'Dossier state changed', RESOLVED_TITLE)
        self.modify(self.target)
        self.sync_dossiers(SYNC_2)

        expected = [
            self.created,
            self.journal_row(self.uid, u'DOSSIER_CLOSED', MODIFIED_AT)]
        self.assertEqual(expected, self.sorted(self.journal(self.uid)))

        # The modification is not exported again
        self.sync_dossiers(SYNC_3)
        self.assertEqual(expected, self.sorted(self.journal(self.uid)))

    @skip(NOT_UPDATED)
    def test_update_exports_new_remarks_once(self):
        self.add_remark(self.target, u'First', time=DateTime('2026/05/20 09:00:00 GMT+0'))
        self.sync_dossiers(SYNC_1)

        self.add_remark(self.target, u'Second', time=DateTime('2026/05/21 09:00:00 GMT+0'))
        self.modify(self.target)
        self.sync_dossiers(SYNC_2)

        expected = [
            self.remark_row(self.uid, u'First\n\n', time=datetime(2026, 5, 20, 9)),
            self.remark_row(self.uid, u'Second\n\n', time=datetime(2026, 5, 21, 9)),
        ]
        self.assertEqual(expected, self.remarks(self.uid))

        self.sync_dossiers(SYNC_3)
        self.assertEqual(expected, self.remarks(self.uid))

    @skip(NOT_UPDATED)
    def test_update_exports_changed_remarks(self):
        self.add_remark(self.target, u'Before', time=DateTime('2026/05/20 09:00:00 GMT+0'))
        self.sync_dossiers(SYNC_1)

        entry = JournalManager(self.target).list()[-1]
        with freeze(MODIFIED):
            JournalManager(self.target).update(
                entry['id'], comment=u'After', category='meeting')
        self.modify(self.target)
        self.sync_dossiers(SYNC_2)

        self.assertEqual(
            [self.remark_row(
                self.uid, u'After\n\n', category=u'Sitzung',
                time=datetime(2026, 5, 20, 9))],
            self.remarks(self.uid))

    @skip(NOT_UPDATED)
    def test_update_removes_deleted_remarks(self):
        self.add_remark(self.target, u'Gone')
        self.add_remark(self.target, u'Kept', time=DateTime('2026/05/21 09:00:00 GMT+0'))
        self.sync_dossiers(SYNC_1)

        entry = JournalManager(self.target).list()[-2]
        with freeze(MODIFIED):
            JournalManager(self.target).remove(entry['id'])
        self.modify(self.target)
        self.sync_dossiers(SYNC_2)

        self.assertEqual(
            [u'Kept\n\n'],
            [row['remark'] for row in self.active(self.remarks(self.uid))])

    def test_update_keeps_rows_of_other_dossiers(self):
        other = self.dossier
        self.add_remark(self.target, u'Hello')
        self.add_remark(other, u'Other')
        self.sync_dossiers(SYNC_1)
        before = (self.journal(other.UID()), self.remarks(other.UID()))

        self.add_remark(self.target, u'Again')
        self.modify(self.target)
        self.sync_dossiers(SYNC_2)

        self.assertEqual(
            before, (self.journal(other.UID()), self.remarks(other.UID())))

    @skip(NOT_UPDATED)
    def test_update_keeps_journal_entries_exported_by_document_syncer(self):
        document = self.create_document(self.target)
        self.sync_all(SYNC_1)
        from_documents = self.dossier_side_rows(document)
        self.assertEqual(1, len(from_documents))

        self.add_entry(self.target, 'Dossier state changed', RESOLVED_TITLE)
        self.modify(self.target)
        self.sync_all(SYNC_2)

        self.assertEqual(from_documents, self.dossier_side_rows(document))
        self.assertEqual(
            [u'DOSSIER_CLOSED'],
            [row['event'] for row in self.journal(self.uid)
             if row['historyobject'] is None])

    @skip(NOT_DELETED)
    def test_delete_flags_journal_entries_and_remarks(self):
        from plone import api
        self.add_remark(self.target, u'Hello')
        self.sync_dossiers(SYNC_1)
        journal, remarks = self.journal(self.uid), self.remarks(self.uid)
        other = self.dossier
        other_before = (self.journal(other.UID()), self.remarks(other.UID()))

        api.content.delete(obj=self.target, check_linkintegrity=False)
        self.sync_dossiers(SYNC_2)

        self.assertEqual(self.flagged(journal), self.journal(self.uid))
        self.assertEqual(self.flagged(remarks), self.remarks(self.uid))
        self.assertEqual(
            other_before, (self.journal(other.UID()), self.remarks(other.UID())))

    def dossier_side_rows(self, document):
        """Rows of the target dossier created by the document syncer."""
        return [row for row in self.journal(self.uid)
                if row['historyobject'] == document.UID()]

    def sorted(self, rows):
        return sorted(rows, key=lambda row: (row['timestamp'], row['event']))


class TestDocumentJournalExport(JournalExportTestCase):

    def setUp(self):
        super(TestDocumentJournalExport, self).setUp()
        self.target = self.empty_dossier
        self.dossier_uid = self.target.UID()
        self.document = self.create_document(self.target)
        self.uid = self.document.UID()

    def created_rows(self, document=None, deleted=False):
        """Rows exported for a document added by `create_document()`."""
        uid = (document or self.document).UID()
        return [
            self.journal_row(
                uid, u'DOCUMENT_CREATED', CREATED_AT, journal='documents',
                historyobject=self.dossier_uid, deleted=deleted),
            self.journal_row(
                self.dossier_uid, u'DOCUMENT_ADDED', CREATED_AT,
                historyobject=uid, deleted=deleted),
        ]

    def document_rows(self, document=None):
        uid = (document or self.document).UID()
        return self.sorted(self.journal(uid))

    def sorted(self, rows):
        return sorted(rows, key=lambda row: (
            row['timestamp'], row['event'], row['objexternalkey']))

    def test_initial_sync_exports_document_and_dossier_journal_entries(self):
        self.sync_all(SYNC_1)

        self.assertItemsEqual(self.created_rows(), self.document_rows())

    def test_initial_sync_of_documents_exports_dossier_entries_without_dossier_sync(self):
        self.sync_documents(SYNC_1)

        self.assertItemsEqual(self.created_rows(), self.document_rows())

    def test_initial_sync_exports_events_of_document_and_dossier(self):
        self.add_entry(self.document, 'Object restore')
        self.add_entry(self.document, 'Document checked in')

        self.sync_all(SYNC_1)

        self.assertItemsEqual(
            self.created_rows() + [
                self.journal_row(self.uid, u'DOCUMENT_RESTORED', MODIFIED_AT,
                                 journal='documents'),
                self.journal_row(self.dossier_uid, u'DOCUMENT_RESTORED',
                                 MODIFIED_AT, historyobject=self.uid),
                self.journal_row(self.uid, u'CONTENT_CHANGED', MODIFIED_AT,
                                 journal='documents'),
            ],
            self.document_rows())

    def test_manual_entries_of_documents_are_not_exported_as_remarks(self):
        self.add_remark(self.document, u'Hello')
        self.add_remark(self.target, u'Hello')

        self.sync_all(SYNC_1)

        self.assertEqual([], self.remarks(self.uid))
        self.assertEqual(
            [u'Hello\n\n'],
            [row['remark'] for row in self.remarks(self.dossier_uid)])

        self.add_remark(self.document, u'Again')
        self.modify(self.document)
        self.sync_all(SYNC_2)
        self.assertEqual([], self.remarks(self.uid))

    def test_consecutive_sync_without_changes_changes_nothing(self):
        self.sync_all(SYNC_1)
        before = self.journal(self.uid, self.dossier_uid)

        self.sync_all(SYNC_2)

        self.assertEqual(before, self.journal(self.uid, self.dossier_uid))

    def test_added_document_exports_dossier_entry_of_unmodified_dossier(self):
        self.sync_all(SYNC_1)
        before = self.journal(self.dossier_uid)

        other = self.create_document(self.target, u'Other')
        self.sync_documents(SYNC_2)

        self.assertItemsEqual(
            before + self.created_rows(other), self.journal(self.dossier_uid))
        self.assertItemsEqual(self.created_rows(), self.document_rows())

    @skip(NOT_UPDATED)
    def test_update_exports_new_entries_of_document_once(self):
        self.sync_all(SYNC_1)

        self.add_entry(self.document, 'Document checked in')
        self.modify(self.document)
        self.sync_all(SYNC_2)

        expected = self.created_rows() + [
            self.journal_row(self.uid, u'CONTENT_CHANGED', MODIFIED_AT,
                             journal='documents')]
        self.assertItemsEqual(expected, self.document_rows())

        self.sync_all(SYNC_3)
        self.assertItemsEqual(expected, self.document_rows())

    @skip(NOT_UPDATED)
    def test_update_exports_new_dossier_entries_of_modified_document(self):
        self.sync_all(SYNC_1)
        dossier_before = self.journal(self.dossier_uid)

        # The dossier itself is not modified
        self.add_entry(self.document, 'Object restore')
        self.modify(self.document)
        self.sync_all(SYNC_2)

        self.assertItemsEqual(
            dossier_before + [
                self.journal_row(self.dossier_uid, u'DOCUMENT_RESTORED',
                                 MODIFIED_AT, historyobject=self.uid)],
            self.journal(self.dossier_uid))

        self.sync_all(SYNC_3)
        self.assertEqual(
            len(dossier_before) + 1, len(self.journal(self.dossier_uid)))

    def test_update_keeps_dossier_entries_of_other_documents(self):
        other = self.create_document(self.target, u'Other')
        self.sync_all(SYNC_1)
        before = self.document_rows(other)

        self.add_entry(self.document, 'Object restore')
        self.modify(self.document)
        self.sync_all(SYNC_2)

        self.assertEqual(before, self.document_rows(other))

    def test_dossier_update_keeps_entries_exported_by_document_syncer(self):
        self.sync_all(SYNC_1)
        before = self.document_rows()

        self.add_remark(self.target, u'Hello')
        self.modify(self.target)
        self.sync_all(SYNC_2)

        self.assertEqual(before, self.document_rows())

    @skip(NOT_DELETED)
    def test_delete_flags_document_and_dossier_entries(self):
        from plone import api
        other = self.create_document(self.target, u'Other')
        self.sync_all(SYNC_1)
        other_before = self.document_rows(other)

        api.content.delete(obj=self.document, check_linkintegrity=False)
        self.sync_all(SYNC_2)

        self.assertItemsEqual(
            self.created_rows(deleted=True), self.document_rows())
        self.assertEqual(other_before, self.document_rows(other))

        self.sync_all(SYNC_3)
        self.assertItemsEqual(
            self.created_rows(deleted=True), self.document_rows())


# Journal timestamps are exported as naive local time (Europe/Zurich, CEST).
CREATED_AT = datetime(2026, 5, 19, 12, 0)
MODIFIED_AT = datetime(2026, 5, 21, 20, 0)
