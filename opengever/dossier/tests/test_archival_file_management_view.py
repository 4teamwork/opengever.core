from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import plone
from opengever.document.archival_file import ArchivalFileConverter
from opengever.document.archival_file import STATE_FAILED_TEMPORARILY
from opengever.document.behaviors.metadata import IDocumentMetadata
from opengever.testing import IntegrationTestCase


class TestArchivalFileManagementView(IntegrationTestCase):

    @browsing
    def test_archival_file_management_view_only_visible_for_managers(self, browser):
        self.login(self.regular_user, browser)
        with browser.expect_unauthorized():
            browser.open(self.expired_dossier, view="archival_file_management")
        self.assertEqual('Insufficient Privileges', plone.first_heading())

        self.login(self.manager, browser)
        browser.open(self.expired_dossier, view="archival_file_management")
        self.assertEqual(self.expired_dossier.Title().decode("utf-8"),
                         plone.first_heading())

    @browsing
    def test_archival_file_management_view_listing(self, browser):
        self.login(self.manager, browser)
        subdossier = create(Builder('dossier')
                            .within(self.expired_dossier)
                            .titled(u"Subdossier"))
        subdocument = create(Builder('document')
                             .within(subdossier)
                             .with_dummy_content()
                             .titled(u"subdocument"))
        document = create(Builder('document')
                          .within(self.expired_dossier)
                          .with_dummy_content()
                          .titled(u"Another document"))

        ArchivalFileConverter(subdocument).store_file('TEST DATA')
        IDocumentMetadata(self.expired_document).archival_file_state = STATE_FAILED_TEMPORARILY

        # make sure that document with no archival file is handled by the view
        self.assertIsNone(IDocumentMetadata(document).archival_file)

        browser.open(self.expired_dossier, view="archival_file_management")
        table = browser.css('table').first
        expected = [['Path', 'Filetype', 'Has archival PDF',
                     'Archival file state'],
                    [self.expired_document.absolute_url_path(), '.doc',
                     'True', "STATE_FAILED_TEMPORARILY"],
                    [document.absolute_url_path(), '.doc',
                     'False', ''],
                    [subdocument.absolute_url_path(), '.doc',
                     'True', "STATE_CONVERTED"]
                    ]
        self.assertEqual(expected, table.lists())
