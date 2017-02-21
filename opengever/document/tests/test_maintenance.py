from datetime import date
from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.mail.mail import IMail
from ftw.testing import freeze
from opengever.document.document import IDocumentSchema
from opengever.document.maintenance import DocumentMaintenance
from opengever.dossier.interfaces import ISourceFileHasBeenPurged
from opengever.testing import FunctionalTestCase
from zope.interface import alsoProvides


class TestDocumentMaintenance(FunctionalTestCase):

    def test_get_dossiers_to_erase_returns_all_resolved_dossiers_with_expired_waiting_period(self):
        dossier_a = create(Builder('dossier')
                           .in_state('dossier-state-resolved')
                           .having(end=date(2016, 1, 2)))
        dossier_b = create(Builder('dossier')
                           .in_state('dossier-state-resolved')
                           .having(end=date(2015, 2, 1)))
        dossier_c = create(Builder('dossier')
                           .in_state('dossier-state-resolved')
                           .having(end=date(2013, 5, 12)))
        dossier_d = create(Builder('dossier')
                           .having(end=date(2013, 5, 12)))

        with freeze(datetime(2017, 3, 5)):
            self.assertItemsEqual(
                [dossier_c],
                DocumentMaintenance().get_dossiers_to_erase())

    def test_dossiers_where_source_file_has_been_purged_are_excluded(self):
        dossier_a = create(Builder('dossier')
                           .in_state('dossier-state-resolved')
                           .having(end=date(2013, 5, 12)))
        dossier_b = create(Builder('dossier')
                           .in_state('dossier-state-resolved')
                           .having(end=date(2013, 5, 12)))

        alsoProvides(dossier_b, ISourceFileHasBeenPurged)

        with freeze(datetime(2017, 3, 5)):
            self.assertItemsEqual(
                [dossier_a],
                DocumentMaintenance().get_dossiers_to_erase())


class TestSourceFilePurgement(FunctionalTestCase):

    def test_get_documents_to_erase_returns_only_docs_with_expired_waiting_period(self):
        dossier_a = create(Builder('dossier')
                           .in_state('dossier-state-resolved')
                           .having(end=date(2015, 2, 1)))
        document_a = create(Builder('document')
                            .attach_archival_file_containing('DATA')
                            .within(dossier_a))
        dossier_b = create(Builder('dossier')
                           .in_state('dossier-state-resolved')
                           .having(end=date(2013, 5, 12)))
        document_b = create(Builder('document')
                            .attach_archival_file_containing('DATA')
                            .within(dossier_b))
        document_c = create(Builder('document')
                            .attach_archival_file_containing('DATA')
                            .within(dossier_b))

        with freeze(datetime(2017, 3, 5)):
            maintenance = DocumentMaintenance()
            dossiers = maintenance.get_dossiers_to_erase()
            self.assertItemsEqual(
                [document_b, document_c],
                maintenance.get_documents_to_erase_source_file(dossiers))

    def test_get_documents_to_erase_returns_only_docs_with_archival_file(self):
        dossier = create(Builder('dossier')
                         .in_state('dossier-state-resolved')
                         .having(end=date(2013, 5, 12)))
        document_a = create(Builder('document')
                            .attach_file_containing('DATA')
                            .attach_archival_file_containing('DATA')
                            .within(dossier))
        document_b = create(Builder('document')
                            .attach_file_containing('DATA')
                            .within(dossier))

        with freeze(datetime(2017, 3, 5)):
            maintenance = DocumentMaintenance()
            dossiers = maintenance.get_dossiers_to_erase()
            self.assertItemsEqual(
                [document_a],
                maintenance.get_documents_to_erase_source_file(dossiers))

    def test_purge_source_files_sets_file_to_none_for_documents(self):
        dossier = create(Builder('dossier')
                         .in_state('dossier-state-resolved')
                         .having(end=date(2013, 5, 12)))
        document_a = create(Builder('document')
                            .attach_file_containing('DATA')
                            .attach_archival_file_containing('DATA')
                            .within(dossier))
        document_b = create(Builder('document')
                            .attach_file_containing('DATA')
                            .within(dossier))

        with freeze(datetime(2017, 3, 5)):
            DocumentMaintenance().purge_source_files()

        self.assertIsNone(IDocumentSchema(document_a).file)
        self.assertIsNotNone(IDocumentSchema(document_b).file)

    def test_purge_source_files_sets_message_to_none_for_mails(self):
        dossier = create(Builder('dossier')
                         .in_state('dossier-state-resolved')
                         .having(end=date(2013, 5, 12)))
        mail_a = create(Builder('mail')
                        .with_dummy_message()
                        .attach_archival_file_containing('DATA')
                        .within(dossier))
        mail_b = create(Builder('mail')
                        .with_dummy_message()
                        .within(dossier))

        with freeze(datetime(2017, 3, 5)):
            DocumentMaintenance().purge_source_files()

        self.assertIsNone(IMail(mail_a).message)
        self.assertIsNotNone(IMail(mail_b).message)

    def test_purge_source_files_marks_dossiers_with_marker_interface(self):
        dossier = create(Builder('dossier')
                         .in_state('dossier-state-resolved')
                         .having(end=date(2013, 5, 12)))
        document_a = create(Builder('document')
                            .attach_file_containing('DATA')
                            .attach_archival_file_containing('DATA')
                            .within(dossier))

        self.assertFalse(ISourceFileHasBeenPurged.providedBy(dossier))

        with freeze(datetime(2017, 3, 5)):
            DocumentMaintenance().purge_source_files()

        self.assertTrue(ISourceFileHasBeenPurged.providedBy(dossier))
