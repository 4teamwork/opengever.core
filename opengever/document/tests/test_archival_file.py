from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.document.archival_file import ArchivalFileConverter
from opengever.document.archival_file import STATE_CONVERTED
from opengever.document.archival_file import STATE_CONVERTING
from opengever.document.archival_file import STATE_MANUALLY_PROVIDED
from opengever.document.behaviors.metadata import IDocumentMetadata
from opengever.testing import FunctionalTestCase


class TestArchivalFile(FunctionalTestCase):

    def setUp(self):
        super(TestArchivalFile, self).setUp()
        self.document = create(Builder('document')
                               .titled(u'\xdcberpr\xfcfung XY')
                               .with_dummy_content())

        self.grant('Manager')

    @browsing
    def test_archival_file_state_is_omitted(self, browser):
        browser.login().open(self.document, view='edit')

        self.assertEquals(
            [],
            browser.css('#formfield-form-widgets-'
                        'IDocumentMetadata-archival_file_state'))

    @browsing
    def test_archival_file_is_ommitted_for_normal_users_by_default(self, browser):
        """By default only managers have the ModifyArchivalFile permission.
        """

        self.grant('Contributor', 'Editor', 'Reader')
        browser.login().open(self.document, view='edit')

        self.assertEquals(
            [],
            browser.css('#formfield-form-widgets-'
                        'IDocumentMetadata-archival_file'))

    def test_file_name_is_file_filename_with_pdf_extension(self):
        self.assertEquals(
            'Ueberpruefung XY.pdf',
            ArchivalFileConverter(self.document).get_file_name())

    def test_trigger_conversion_sets_state_to_converting(self):
        ArchivalFileConverter(self.document).trigger_conversion()
        self.assertEquals(STATE_CONVERTING,
                          IDocumentMetadata(self.document).archival_file_state)

    def test_trigger_conversion_skip_files_in_manually_state(self):
        document = create(Builder('document')
                          .titled(u'\xdcberpr\xfcfung XY')
                          .with_dummy_content()
                          .having(archival_file_state=STATE_MANUALLY_PROVIDED))

        ArchivalFileConverter(self.document).trigger_conversion()

        self.assertEquals(STATE_MANUALLY_PROVIDED,
                          IDocumentMetadata(document).archival_file_state)

    def test_store_file_sets_state_to_converted(self):
        ArchivalFileConverter(self.document).store_file('TEST DATA')
        self.assertEquals(
            STATE_CONVERTED,
            IDocumentMetadata(self.document).archival_file_state)

    def test_store_file_decodes_unicode_contenttypes(self):
        ArchivalFileConverter(self.document).store_file(
            'TEST DATA', mimetype=u'application/pdf')

        archival_file = IDocumentMetadata(self.document).archival_file
        self.assertTrue(isinstance(archival_file.contentType, str))


class TestArchivalFileState(FunctionalTestCase):

    def setUp(self):
        super(TestArchivalFileState, self).setUp()
        self.dossier = create(Builder('dossier'))
        self.grant('Manager')

    @browsing
    def test_set_to_manually_when_archival_file_is_added_in_edit_form(self, browser):
        document = create(Builder('document').within(self.dossier))

        browser.login().open(document, view='edit')
        browser.fill(
            {'Archival File': ('FILE DATA', 'archival_file.pdf')})
        browser.click_on('Save')

        self.assertEquals(
            STATE_MANUALLY_PROVIDED,
            IDocumentMetadata(document).archival_file_state)

    @browsing
    def test_is_not_updated_when_archival_file_is_not_changed(self, browser):
        document = create(Builder('document')
                          .within(self.dossier)
                          .attach_archival_file_containing('DATA')
                          .having(archival_file_state=STATE_CONVERTED))

        browser.login().open(document, view='edit')
        browser.fill({'Title': u'New document title'})
        browser.click_on('Save')

        self.assertEquals(
            STATE_CONVERTED,
            IDocumentMetadata(document).archival_file_state)

    @browsing
    def test_set_to_manually_when_archival_file_is_updated_in_edit_form(self, browser):
        document = create(Builder('document')
                          .within(self.dossier)
                          .attach_archival_file_containing('DATA')
                          .having(archival_file_state=STATE_CONVERTED))

        browser.login().open(document, view='edit')
        browser.fill(
            {'Archival File': ('NEW FILE DATA', 'ddd.pdf')})
        browser.click_on('Save')

        self.assertEquals(
            STATE_MANUALLY_PROVIDED,
            IDocumentMetadata(document).archival_file_state)

    @browsing
    def test_removes_state_when_archival_file_is_removed(self, browser):
        document = create(Builder('document')
                          .within(self.dossier)
                          .attach_archival_file_containing('DATA')
                          .having(archival_file_state=STATE_CONVERTED))

        browser.login().open(document, view='edit')

        remove_radio_button = browser.css(
            '#form-widgets-IDocumentMetadata-archival_file-remove').first
        remove_radio_button.checked = 'checked'
        browser.find('Save').click()

        self.assertIsNone(IDocumentMetadata(document).archival_file_state)

    @browsing
    def test_set_to_manually_when_archival_file_is_added_in_archival_file_form(self, browser):
        document = create(Builder('document').within(self.dossier))

        browser.login().open(document, view='edit_archival_file')
        browser.fill(
            {'Archival File': ('FILE DATA', 'archival_file.pdf')})
        browser.click_on('Save')

        self.assertEquals(
            STATE_MANUALLY_PROVIDED,
            IDocumentMetadata(document).archival_file_state)

    @browsing
    def test_set_to_manually_when_archival_file_is_updated_in_archival_file_form(self, browser):
        document = create(Builder('document')
                          .within(self.dossier)
                          .attach_archival_file_containing('DATA')
                          .having(archival_file_state=STATE_CONVERTED))

        browser.login().open(document, view='edit_archival_file')
        browser.fill(
            {'Archival File': ('NEW FILE DATA', 'ddd.pdf')})
        browser.click_on('Save')

        self.assertEquals(
            STATE_MANUALLY_PROVIDED,
            IDocumentMetadata(document).archival_file_state)

    @browsing
    def test_removes_state_when_archival_file_is_removed_in_archival_file_form(self, browser):
        document = create(Builder('document')
                          .within(self.dossier)
                          .attach_archival_file_containing('DATA')
                          .having(archival_file_state=STATE_CONVERTED))

        browser.login().open(document, view='edit_archival_file')
        remove_radio_button = browser.css(
            '#form-widgets-archival_file-remove').first
        remove_radio_button.checked = 'checked'
        browser.find('Save').click()

        self.assertIsNone(IDocumentMetadata(document).archival_file_state)
