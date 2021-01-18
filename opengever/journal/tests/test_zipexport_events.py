from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.journal.handlers import DOCUMENT_EXPORTED
from opengever.journal.handlers import DOSSIER_EXPORTED
from opengever.testing import FunctionalTestCase


class TestZipExportJournalizations(FunctionalTestCase):

    def setUp(self):
        super(TestZipExportJournalizations, self).setUp()

        self.dossier = create(
            Builder('dossier')
        )

        self.document = create(
            Builder('document')
            .within(self.dossier)
            .with_dummy_content()
        )

    @browsing
    def test_exported_dossier_with_files_gets_journalized(self, browser):
        browser.login().open(self.dossier,
                             view="zip_export")

        self.assert_journal_entry(self.document,
                                  DOCUMENT_EXPORTED,
                                  u'Document included in ZIP export: {0}'
                                  .format(self.document.title_or_id())
                                  )

        self.assert_journal_entry(self.dossier,
                                  DOSSIER_EXPORTED,
                                  u'Dossier included in ZIP export: {0}'
                                  .format(self.dossier.title_or_id())
                                  )
