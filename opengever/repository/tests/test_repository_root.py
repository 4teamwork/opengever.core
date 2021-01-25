from ftw.testbrowser import browsing
from ftw.testbrowser.pages import statusmessages
from opengever.repository.repositoryroot import IRepositoryRoot
from opengever.testing import IntegrationTestCase


class TestRepositoryRoot(IntegrationTestCase):

    @browsing
    def test_adding(self, browser):
        self.login(self.manager, browser)
        browser.open(view='++add++opengever.repository.repositoryroot')
        browser.fill({'Title (English)': u'Foob\xe4r',
                      'Title (German)': u'Foob\xe4r'}).save()
        statusmessages.assert_no_error_messages()
        self.assertTrue(IRepositoryRoot.providedBy(browser.context))
        self.assertEqual('foobar', browser.context.getId())

    @browsing
    def test_is_not_addable_by_administrator(self, browser):
        self.login(self.administrator, browser)
        with browser.expect_unauthorized():
            browser.open(view='++add++opengever.repository.repositoryroot')
