from datetime import date
from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testing import freeze
from opengever.document.behaviors.metadata import IDocumentMetadata
from opengever.dossier.maintenance import SourceFileEraser
from opengever.testing import FunctionalTestCase


class TestSourceFileEraser(FunctionalTestCase):

    def test_get_dossiers_with_expired_waiting_period(self):
        dossier_a = create(Builder('dossier')
                           .having(end=date(2016, 1, 2)))
        dossier_b = create(Builder('dossier')
                           .having(end=date(2015, 1, 2)))
        dossier_c = create(Builder('dossier')
                           .having(end=date(2013, 5, 12)))

        with freeze(datetime(2017, 1, 2)):
            self.assertItemsEqual(
                [dossier_b, dossier_c],
                SourceFileEraser().get_dossiers_to_erase())

    def test_erase_source_file_only_when_archival_file_exists(self):
        dossier = create(Builder('dossier')
                         .having(end=date(2014, 1, 2)))
        document_a = create(Builder('document')
                            .within(dossier)
                            .attach_file_containing('source data')
                            .attach_archival_file_containing('archive data'))
        document_b = create(Builder('document')
                            .within(dossier)
                            .attach_file_containing('source data'))

        SourceFileEraser().erase()

        self.assertIsNone(IDocumentMetadata(document_a).file)
        self.assertIsNotNone(IDocumentMetadata(document_b).file)

    def test_erase_only_documents_from_expired_dossiers(self):
        # expired
        dossier_a = create(Builder('dossier')
                           .having(end=date(2012, 1, 2)))
        document_a = create(Builder('document')
                            .within(dossier_a)
                            .attach_file_containing('source data')
                            .attach_archival_file_containing('archive data'))

        # not_expired
        dossier_b = create(Builder('dossier')
                           .having(end=date(2016, 1, 2)))
        document_b = create(Builder('document')
                            .within(dossier_b)
                            .attach_file_containing('source data')
                            .attach_archival_file_containing('archive data'))

        with freeze(datetime(2016, 1, 1)):
            SourceFileEraser().erase()

        self.assertIsNone(IDocumentMetadata(document_a).file)
        self.assertIsNotNone(IDocumentMetadata(document_b).file)

    def test_erase_source_file_of_mails(self):
        dossier = create(Builder('dossier')
                         .having(end=date(2014, 1, 2)))
        mail = create(Builder('mail')
                      .within(dossier)
                      .with_message('source data')
                      .attach_archival_file_containing('archive data'))

        self.assertIsNotNone(IDocumentMetadata(mail).message)
        SourceFileEraser().erase()
        self.assertIsNone(IDocumentMetadata(mail).message)
