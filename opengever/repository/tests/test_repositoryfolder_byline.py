from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
from opengever.testing.pages import byline


class TestRepositoryfolderByline(IntegrationTestCase):

    @browsing
    def test_privacy_layer_is_shown(self, browser):
        browser.login(self.regular_user).open(self.branch_repository)
        # XXX The English transalation of the values are missing.
        self.assertDictContainsSubset(
            {'Privacy layer:': 'privacy_layer_no'},
            byline.text_dict())

    @browsing
    def test_archival_value_is_shown(self, browser):
        browser.login(self.regular_user).open(self.branch_repository)
        self.assertDictContainsSubset(
            {'Archival value:': 'unchecked'},
            byline.text_dict())

    @browsing
    def test_public_trial_is_not_present(self, browser):
        browser.login(self.regular_user).open(self.branch_repository)
        self.assertNotIn(
            'Public Trial:', byline.text_dict(),
            "Public trial must NOT be part of repository byline any more")

    @browsing
    def test_description_is_shown_when_exists(self, browser):
        browser.login(self.regular_user)
        self.assertTrue(self.branch_repository.Description(),
                        'Expected branch_repository to have a description.')
        browser.open(self.branch_repository)
        self.assertEquals(
            [u'Alles zum Thema F\xfchrung.'],
            browser.css('.documentByLine .description').text)

    @browsing
    def test_description_is_not_shown_when_there_is_none(self, browser):
        browser.login(self.regular_user)
        self.assertFalse(self.leaf_repository.Description(),
                        'Expected leaf_repository to have no description.')
        browser.open(self.leaf_repository)
        self.assertFalse(browser.css('.documentByLine .description'))
