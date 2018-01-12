from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from opengever.testing import IntegrationTestCase


class TestBaseBehavior(IntegrationTestCase):
    """Test the base behavior with the help of businesscase dossier.
    """

    @browsing
    def test_base_behavior(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.leaf_repofolder)
        factoriesmenu.add(u'Business Case Dossier')
        browser.fill({'Title': 'Foo', 'Description': 'Bar'})
        browser.click_on('Save')

        dossier = browser.context
        self.assertEquals('Foo', dossier.Title())
        self.assertEquals('Bar', dossier.Description())

    @browsing
    def test_base_behavior_uses_common_fieldset(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.leaf_repofolder)
        factoriesmenu.add(u'Business Case Dossier')

        common_fieldset = browser.css('fieldset').first
        self.assertEquals(['Common'], common_fieldset.css('legend').text)
