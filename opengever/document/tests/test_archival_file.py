from ftw.testbrowser import browsing
from opengever.document.archival_file import ArchivalFileConverter
from opengever.document.archival_file import STATE_CONVERTED
from opengever.document.archival_file import STATE_CONVERTING
from opengever.document.archival_file import STATE_MANUALLY_PROVIDED
from opengever.document.behaviors.metadata import IDocumentMetadata
from opengever.testing import IntegrationTestCase


class TestArchivalFile(IntegrationTestCase):

    def setUp(self):
        super(TestArchivalFile, self).setUp()
        self.login(self.regular_user)
        self.test_document = self.document

    @browsing
    def test_archival_file_conversion_state_is_omitted(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.test_document, view='edit')

        self.assertEquals(
            [],
            browser.css('#formfield-form-widgets-'
                        'IDocumentMetadata-archival_file_state'))

    @browsing
    def test_archival_file_is_ommitted_for_normal_users_by_default(self, browser):
        """By default only managers have the ModifyArchivalFile permission.
        """
        self.login(self.regular_user, browser=browser)
        browser.open(self.test_document, view='edit')
        self.assertEquals(
            [],
            browser.css('#formfield-form-widgets-IDocumentMetadata-archival_file'))
        browser.css('#form-buttons-cancel').first.click()

        self.login(self.manager, browser=browser)
        browser.open(self.test_document, view='edit')
        self.assertEquals(
            1,
            len(browser.css('#formfield-form-widgets-IDocumentMetadata-archival_file')))

    def test_file_name_is_file_filename_with_pdf_extension(self):
        self.login(self.regular_user)

        self.assertEquals(
            u'Vertraegsentwurf.pdf',
            ArchivalFileConverter(self.test_document).get_file_name())

    def test_trigger_conversion_sets_state_to_converting(self):
        self.login(self.regular_user)

        ArchivalFileConverter(self.test_document).trigger_conversion()
        self.assertEquals(STATE_CONVERTING,
                          IDocumentMetadata(self.test_document).archival_file_state)

    def test_trigger_conversion_skip_files_in_manually_state(self):
        self.login(self.regular_user)
        self.set_archival_file(self.test_document, 'ARCH TEST',
                               conversion_state=STATE_MANUALLY_PROVIDED)

        ArchivalFileConverter(self.test_document).trigger_conversion()

        self.assertEquals(STATE_MANUALLY_PROVIDED,
                          IDocumentMetadata(self.test_document).archival_file_state)
        self.assertEquals('ARCH TEST',
                          IDocumentMetadata(self.test_document).archival_file.data)

    def test_store_file_sets_state_to_converted(self):
        self.login(self.regular_user)

        ArchivalFileConverter(self.test_document).store_file('TEST DATA')
        self.assertEquals(
            STATE_CONVERTED,
            IDocumentMetadata(self.test_document).archival_file_state)

    def test_store_file_decodes_unicode_contenttypes(self):
        self.login(self.regular_user)

        ArchivalFileConverter(self.test_document).store_file(
            'TEST DATA', mimetype=u'application/pdf')

        archival_file = IDocumentMetadata(self.test_document).archival_file
        self.assertTrue(isinstance(archival_file.contentType, str))


class TestArchivalFileState(IntegrationTestCase):

    @browsing
    def test_set_to_manually_when_archival_file_is_added_in_edit_form(self, browser):
        self.login(self.manager, browser=browser)

        browser.open(self.document, view='edit')
        browser.fill(
            {'Archival File': ('FILE DATA', 'archival_file.pdf')})
        browser.click_on('Save')

        self.assertEquals(
            STATE_MANUALLY_PROVIDED,
            IDocumentMetadata(self.document).archival_file_state)

    @browsing
    def test_is_not_updated_when_archival_file_is_not_changed(self, browser):
        self.login(self.manager, browser=browser)

        self.set_archival_file(self.document, 'ARCH TEST')

        self.login(self.regular_user, browser=browser)
        browser.open(self.document, view='edit')
        browser.fill({'Title': u'New document title'})
        browser.click_on('Save')

        self.assertEquals(
            STATE_CONVERTED,
            IDocumentMetadata(self.document).archival_file_state)

    @browsing
    def test_set_to_manually_when_archival_file_is_updated_in_edit_form(self, browser):
        self.login(self.manager, browser=browser)

        self.set_archival_file(self.document, 'ARCH TEST')

        browser.open(self.document, view='edit')
        browser.fill(
            {'Archival File': ('NEW FILE DATA', 'ddd.pdf')})
        browser.click_on('Save')

        self.assertEquals(
            STATE_MANUALLY_PROVIDED,
            IDocumentMetadata(self.document).archival_file_state)

    @browsing
    def test_removes_state_when_archival_file_is_removed(self, browser):
        self.login(self.manager, browser=browser)

        self.set_archival_file(self.document, 'ARCH TEST')

        browser.open(self.document, view='edit')

        remove_radio_button = browser.css(
            '#form-widgets-IDocumentMetadata-archival_file-remove').first
        remove_radio_button.checked = 'checked'
        browser.find('Save').click()

        self.assertIsNone(IDocumentMetadata(self.document).archival_file_state)
        self.assertIsNone(IDocumentMetadata(self.document).archival_file)

    @browsing
    def test_set_to_manually_when_archival_file_is_added_in_archival_file_form(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.document, view='edit_archival_file')
        browser.fill(
            {'Archival File': ('FILE DATA', 'archival_file.pdf')})
        browser.click_on('Save')

        self.assertEquals(
            STATE_MANUALLY_PROVIDED,
            IDocumentMetadata(self.document).archival_file_state)

    @browsing
    def test_set_to_manually_when_archival_file_is_updated_in_archival_file_form(self, browser):
        self.login(self.regular_user, browser=browser)

        self.set_archival_file(self.document, 'ARCH TEST')

        browser.open(self.document, view='edit_archival_file')
        browser.fill(
            {'Archival File': ('NEW FILE DATA', 'ddd.pdf')})
        browser.click_on('Save')

        self.assertEquals(
            STATE_MANUALLY_PROVIDED,
            IDocumentMetadata(self.document).archival_file_state)

    @browsing
    def test_removes_state_when_archival_file_is_removed_in_archival_file_form(self, browser):
        self.login(self.regular_user, browser=browser)

        self.set_archival_file(self.document, 'ARCH TEST')

        browser.open(self.document, view='edit_archival_file')
        remove_radio_button = browser.css(
            '#form-widgets-archival_file-remove').first
        remove_radio_button.checked = 'checked'
        browser.find('Save').click()

        self.assertIsNone(IDocumentMetadata(self.document).archival_file_state)
        self.assertIsNone(IDocumentMetadata(self.document).archival_file)
