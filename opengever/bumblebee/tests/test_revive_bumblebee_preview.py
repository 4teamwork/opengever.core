from ftw.bumblebee.interfaces import IBumblebeeable
from ftw.bumblebee.interfaces import IBumblebeeDocument
from ftw.bumblebee.tests.helpers import get_queue
from ftw.bumblebee.tests.helpers import reset_queue
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import statusmessages
from opengever.testing import IntegrationTestCase
from plone.namedfile.file import NamedBlobFile


class TestReviveBumblebeePreviewWithDisabledFeature(IntegrationTestCase):

    @browsing
    def test_action_is_disabled_if_bumblebee_feature_is_disabled(self, browser):
        self.login(self.administrator, browser)

        browser.visit(self.document)

        self.assertTrue(IBumblebeeable.providedBy(self.document))
        self.assertNotIn(
            'Regenerate PDF preview',
            browser.css('.actionMenuContent li').text)


class TestReviveBumblebeePreview(IntegrationTestCase):

    features = ('bumblebee', )

    @browsing
    def test_action_is_disabled_if_not_on_a_bumblebee_document(self, browser):
        self.login(self.administrator, browser)

        browser.visit(self.task)

        self.assertFalse(IBumblebeeable.providedBy(self.task))
        self.assertNotIn(
            'Regenerate PDF preview',
            browser.css('.actionMenuContent li').text)

    @browsing
    def test_action_is_enabled_for_admin_on_bumblebee_document(self, browser):
        self.login(self.administrator, browser)
        browser.visit(self.document)

        self.assertTrue(IBumblebeeable.providedBy(self.document))
        self.assertIn(
            'Regenerate PDF preview',
            browser.css('.actionMenuContent li').text)

    @browsing
    def test_action_is_enabled_for_reader_on_bumblebee_document(self, browser):
        self.login(self.regular_user, browser)
        browser.visit(self.document)

        self.assertTrue(IBumblebeeable.providedBy(self.document))
        self.assertIn(
            'Regenerate PDF preview',
            browser.css('.actionMenuContent li').text)

    @browsing
    def test_show_status_message_after_reviving(self, browser):
        self.login(self.administrator, browser)

        browser.visit(self.document)
        browser.css('.actionMenuContent li').find('Regenerate PDF preview').first.click()

        statusmessages.assert_message('Preview was revived and will be available soon.')

    @browsing
    def test_update_checksum_on_reviving(self, browser):
        self.login(self.administrator, browser)

        browser.visit(self.document)
        self.document.file = NamedBlobFile(data='some other text', filename=u'foo.pdf')
        checksum_before_reviving = IBumblebeeDocument(self.document).get_checksum()
        browser.css('.actionMenuContent li').find('Regenerate PDF preview').first.click()
        checksum_after_reviving = IBumblebeeDocument(self.document).get_checksum()

        self.assertNotEqual(checksum_before_reviving, checksum_after_reviving)

    @browsing
    def test_queue_storing_on_reviving(self, browser):
        self.login(self.administrator, browser)

        browser.visit(self.document)
        reset_queue()

        self.assertEquals(0, len(get_queue()))

        browser.css('.actionMenuContent li').find('Regenerate PDF preview').first.click()

        self.assertEquals(1, len(get_queue()))
