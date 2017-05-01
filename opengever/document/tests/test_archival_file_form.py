from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.document.behaviors.metadata import IDocumentMetadata
from opengever.document.browser.archival_file_form import can_access_archival_file_form
from opengever.testing import FunctionalTestCase
from plone.namedfile.file import NamedBlobFile


class TestEditArchivalFormAccess(FunctionalTestCase):

    def setUp(self):
        super(TestEditArchivalFormAccess, self).setUp()

        dossier = create(Builder('dossier').in_state('dossier-state-resolved'))
        self.document = create(Builder('document')
                               .with_dummy_content()
                               .within(dossier))

    def test_parent_of_content_needs_to_be_a_dossier(self):
        user = self.portal.portal_membership.getAuthenticatedMember()

        self.assertTrue(can_access_archival_file_form(user, self.document))

        with self.assertRaises(AssertionError):
            can_access_archival_file_form(user, self.document.aq_parent)

    def test_one_of_the_parents_needs_to_be_a_dossier(self):
        user = self.portal.portal_membership.getAuthenticatedMember()
        dossier = create(Builder('dossier').in_state('dossier-state-resolved'))
        task = create(Builder('task').within(dossier))
        document = create(Builder('document')
                          .with_dummy_content()
                          .within(task))

        self.assertTrue(can_access_archival_file_form(user, document))

    def test_user_CANNOT_edit_when_parent_dossier_is_inactive(self):
        user = self.portal.portal_membership.getAuthenticatedMember()
        dossier = create(Builder('dossier').in_state('dossier-state-inactive'))
        document = create(Builder('document')
                          .with_dummy_content()
                          .within(dossier))

        self.assertFalse(can_access_archival_file_form(user, document))

    def test_user_WITH_modify_permission_in_open_state_CAN_edit(self):
        user = self.portal.portal_membership.getAuthenticatedMember()

        self.assertTrue(can_access_archival_file_form(user, self.document))

    def test_user_WITHOUT_modify_permission_in_open_state_CANNOT_edit(self):
        user = create(Builder('user').with_roles('Contributor'))
        self.assertFalse(can_access_archival_file_form(user, self.document))

    def test_not_accessible_on_not_basedocumentish_objects(self):
        user = self.portal.portal_membership.getAuthenticatedMember()
        dossier = create(Builder('dossier'))
        subdossier = create(Builder('dossier').within(dossier))

        with self.assertRaises(AssertionError):
            can_access_archival_file_form(user, subdossier)


class TestArchivalFileForm(FunctionalTestCase):

    def setUp(self):
        super(TestArchivalFileForm, self).setUp()

        dossier = create(Builder('dossier').in_state('dossier-state-resolved'))
        self.document = create(Builder('document')
                               .with_dummy_content()
                               .within(dossier))

    @browsing
    def test_raise_unauthorized_if_the_user_CANNOT_modify(self, browser):
        user = create(Builder('user').with_roles('Contributor'))

        with browser.expect_unauthorized():
            browser.login(user.getId()).visit(self.document,
                                              view='edit_archival_file')

    @browsing
    def test_user_CAN_access_edit_form(self, browser):
        browser.login().visit(self.document, view='edit_archival_file')

        self.assertEquals(
            '{0}/edit_archival_file'.format(self.document.absolute_url()),
            browser.url)

        self.assertTrue(browser.css('#formfield-form-widgets-archival_file'),
                        'Archival file field is not available.')

    @browsing
    def test_user_CAN_change_the_archival_file(self, browser):
        browser.login().visit(self.document, view='edit_archival_file')
        browser.fill(
            {'Archival File': ('FILE DATA', 'archival_file.pdf')}).submit()

        archival_file = IDocumentMetadata(self.document).archival_file
        self.assertTrue(isinstance(archival_file, NamedBlobFile))
        self.assertEquals('application/pdf', archival_file.contentType)
        self.assertEquals('FILE DATA', archival_file.data)

    @browsing
    def test_user_submit_cancel_button(self, browser):
        browser.login().visit(self.document, view='edit_archival_file')
        browser.find('Cancel').click()
        self.assertEquals(self.document.absolute_url(), browser.url)
