from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from opengever.base.behaviors.base import IOpenGeverBase
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

    def test_set_bytestring_for_descriptions_will_convert_it_to_unicode(self):
        self.login(self.regular_user)
        IOpenGeverBase(self.dossier).description = ''
        self.assertIsInstance(IOpenGeverBase(self.dossier).description, unicode)

    def test_set_bytestring_for_title_will_raise_an_error(self):
        self.login(self.regular_user)
        with self.assertRaises(ValueError):
            IOpenGeverBase(self.dossier).title = ''
