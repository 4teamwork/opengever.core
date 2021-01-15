from Acquisition import aq_parent
from ftw.testbrowser import browsing
from opengever.document.behaviors.metadata import IDocumentMetadata
from opengever.document.browser.archival_file_form import can_access_archival_file_form
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.testing import IntegrationTestCase
from plone.namedfile.file import NamedBlobFile


class TestEditArchivalFormAccess(IntegrationTestCase):

    def test_one_of_the_parents_of_content_needs_to_be_a_dossier(self):
        self.login(self.regular_user)
        self.assertTrue(IDossierMarker.providedBy(aq_parent(self.document)))
        self.assertTrue(can_access_archival_file_form(self.regular_user, self.document))

        self.assertFalse(IDossierMarker.providedBy(aq_parent(self.taskdocument)))
        self.assertTrue(can_access_archival_file_form(self.regular_user, self.taskdocument))

        self.login(self.administrator)
        self.assertFalse(can_access_archival_file_form(self.administrator, self.inbox_document))

    def test_user_cannot_edit_when_parent_dossier_is_inactive(self):
        self.login(self.regular_user)
        self.assertFalse(can_access_archival_file_form(self.regular_user, self.inactive_document))

    def test_user_needs_modify_permission_in_open_state_to_edit(self):
        self.login(self.regular_user)
        self.assertTrue(can_access_archival_file_form(self.regular_user, self.document))
        self.dossier.__ac_local_roles_block__ = True
        self.dossier.reindexObjectSecurity()
        self.assertFalse(can_access_archival_file_form(self.regular_user, self.document))

    def test_not_accessible_on_not_basedocumentish_objects(self):
        self.login(self.regular_user)
        with self.assertRaises(AssertionError):
            can_access_archival_file_form(self.regular_user, self.subdossier)


class TestArchivalFileForm(IntegrationTestCase):

    @browsing
    def test_raise_unauthorized_if_the_user_cannot_modify(self, browser):
        self.login(self.regular_user, browser=browser)
        self.dossier.__ac_local_roles_block__ = True
        self.dossier.reindexObjectSecurity()
        with browser.expect_unauthorized():
            browser.visit(self.document, view='edit_archival_file')

    @browsing
    def test_user_can_access_edit_form(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.visit(self.document, view='edit_archival_file')

        self.assertEquals(
            '{0}/edit_archival_file'.format(self.document.absolute_url()),
            browser.url)

        self.assertTrue(browser.css('#formfield-form-widgets-archival_file'),
                        'Archival file field is not available.')

    @browsing
    def test_user_can_change_the_archival_file(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.visit(self.document, view='edit_archival_file')
        browser.fill(
            {'Archival file': ('FILE DATA', 'archival_file.pdf')}).submit()

        archival_file = IDocumentMetadata(self.document).archival_file
        self.assertTrue(isinstance(archival_file, NamedBlobFile))
        self.assertEquals('application/pdf', archival_file.contentType)
        self.assertEquals('FILE DATA', archival_file.data)

    @browsing
    def test_user_submit_cancel_button(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.visit(self.document, view='edit_archival_file')
        browser.find('Cancel').click()
        self.assertEquals(self.document.absolute_url(), browser.url)

