from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.core.testing import OPENGEVER_FUNCTIONAL_TESTING
from opengever.document.checkout.manager import CHECKIN_CHECKOUT_ANNOTATIONS_KEY
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.testing import create_ogds_user
from opengever.testing import FunctionalTestCase
from plone.app.testing import login
from plone.app.testing import logout
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.locking.interfaces import IRefreshableLockable
from zope.annotation.interfaces import IAnnotations
from zope.component import queryMultiAdapter
import transaction


class TestDocumentOverview(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_TESTING

    def setUp(self):
        super(TestDocumentOverview, self).setUp()
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)

        create_ogds_user(TEST_USER_ID)
        self.document = create(Builder('document').with_dummy_content())

        transaction.commit()

    def tearDown(self):
        setRoles(self.portal, TEST_USER_ID, ['Member'])
        super(TestDocumentOverview, self).tearDown()

    @browsing
    def test_overview_has_edit_link(self, browser):

        browser.login().open(self.document, view='tabbedview_view-overview')
        self.assertEquals('Edit Document',
                          browser.css('a.function-edit').first.text)
        self.assertEquals(
            '{0}/editing_document'.format(
                self.document.absolute_url()),
            browser.css('a.function-edit').first.attrib['href'])

    @browsing
    def test_overview_has_creator_link(self, browser):

        browser.login().open(self.document, view='tabbedview_view-overview')
        self.assertEquals('Boss Hugo (test_user_1_)',
                          browser.css('td [href*="user-details"]').first.text)
        self.assertEquals(
            '{0}/@@user-details/test_user_1_'.format(
                self.portal.absolute_url()),
            browser.css('td [href*="user-details"]').first.attrib['href'])

    @browsing
    def test_overview_has_copy_link(self, browser):

        browser.login().open(self.document, view='tabbedview_view-overview')
        self.assertEquals('Download copy',
                          browser.css('a.function-download-copy').first.text)
        self.assertEquals(
            '{0}/file_download_confirmation'.format(
                self.document.absolute_url()),
            browser.css('a.function-download-copy').first.attrib['href'])

    @browsing
    def test_overview_self_checked_out(self, browser):
        """Check the document overview when the document is checked out,
        by your self (TEST_USER_ID):
         - checked out by information
         - edit link is still available"""

        document = create(Builder('document').with_dummy_content())
        manager = queryMultiAdapter(
            (document, self.portal.REQUEST), ICheckinCheckoutManager)
        manager.checkout()

        browser.login().visit(document, view='tabbedview_view-overview')

        self.assertEquals('Boss Hugo (test_user_1_)',
                          browser.css('[href*="user-details"]').first.text)
        self.assertEquals('Edit Document',
                          browser.css('a.function-edit').first.text)

        self.assertEquals('Download copy',
                          browser.css('a.function-download-copy').first.text)

    @browsing
    def test_inactive_links_if_document_is_checked_out(self, browser):
        """Check the document overview when the document is checked out,
        by another user:
         - checked out information
         - edit link is inactive"""

        document = create(Builder('document').with_dummy_content())
        IAnnotations(document)[
            CHECKIN_CHECKOUT_ANNOTATIONS_KEY] = 'hugo.boss'

        transaction.commit()

        browser.login().visit(document, view='tabbedview_view-overview')

        self.assertEquals('Edit Document',
                          browser.css('.function-edit-inactive').first.text)
        self.assertEquals(
            'Download copy',
            browser.css('.function-download-copy-inactive').first.text)

    @browsing
    def test_checkout_not_possible_if_locked_by_another_user(self, browser):
        second_user = create(Builder('user').with_roles('Member'))
        document = create(Builder('document').with_dummy_content())

        login(self.portal, second_user.getId())
        lockable = IRefreshableLockable(document)
        lockable.lock()

        logout()
        login(self.portal, TEST_USER_NAME)
        transaction.commit()

        browser.login().visit(document, view='tabbedview_view-overview')
        self.assertFalse(browser.css('a.function-edit'),
                         'There should be no edit link')

    @browsing
    def test_classification_fields_are_shown(self, browser):

        document = create(Builder('document'))
        browser.login().visit(document, view='tabbedview_view-overview')

        self.assertEquals(
            'unprotected',
            browser.css(
                '#form-widgets-IClassification-classification').first.text)

        self.assertEquals(
            'privacy_layer_no',
            browser.css(
                '#form-widgets-IClassification-privacy_layer').first.text)

        self.assertEquals(
            'unchecked',
            browser.css(
                '#form-widgets-IClassification-public_trial').first.text)

        self.assertEquals(
            '',
            browser.css(
                '#form-widgets-IClassification-public_trial_statement').first.text)

    @browsing
    def test_modify_public_trial_link_NOT_shown_on_open_dossier(self, browser):
        dossier = create(Builder('dossier'))
        document = create(Builder('document')
                          .within(dossier)
                          .with_dummy_content())
        browser.login().visit(document, view='tabbedview_view-overview')

        self.assertFalse(
            browser.css(
                '#form-widgets-IClassification-public_trial-edit-link'),
            'Public trial edit link should not be visible.')

    @browsing
    def test_modify_public_trial_is_visible_on_closed_dossier(self, browser):
        dossier = create(Builder('dossier').in_state('dossier-state-resolved'))
        document = create(Builder('document')
                          .within(dossier)
                          .with_dummy_content())
        browser.login().visit(document, view='tabbedview_view-overview')

        self.assertTrue(
            browser.css(
                '#form-widgets-IClassification-public_trial-edit-link'),
            'Public trial edit link should be visible.')
