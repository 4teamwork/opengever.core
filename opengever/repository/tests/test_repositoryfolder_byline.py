from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
from opengever.testing.pages import byline


class TestRepositoryfolderByline(IntegrationTestCase):

    @browsing
    def test_privacy_layer_is_shown(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.branch_repofolder)
        # XXX The English transalation of the values are missing.
        self.assertDictContainsSubset(
            {'Privacy protection:': 'no'},
            byline.text_dict())

    @browsing
    def test_archival_value_is_shown(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.branch_repofolder)
        self.assertDictContainsSubset(
            {'Archival value:': 'not assessed'},
            byline.text_dict())

    @browsing
    def test_public_trial_is_not_present(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.branch_repofolder)
        self.assertNotIn(
            'Public Trial:', byline.text_dict(),
            "Public trial must NOT be part of repository byline any more")

    @browsing
    def test_description_is_shown_when_exists(self, browser):
        self.login(self.regular_user, browser)
        self.assertTrue(self.branch_repofolder.Description(),
                        'Expected branch_repofolder to have a description.')
        browser.open(self.branch_repofolder)
        self.assertEquals(
            [u'Alles zum Thema F\xfchrung.'],
            browser.css('.documentByLine .description').text)

    @browsing
    def test_description_is_not_shown_when_there_is_none(self, browser):
        self.login(self.regular_user, browser)
        self.assertFalse(self.leaf_repofolder.Description(),
                        'Expected leaf_repofolder to have no description.')
        browser.open(self.leaf_repofolder)
        self.assertFalse(browser.css('.documentByLine .description'))
