from opengever.testing import FunctionalTestCase
from plone.dexterity.fti import DexterityFTI
import transaction
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu


class TestBaseBehavior(FunctionalTestCase):

    def setUp(self):
        super(TestBaseBehavior, self).setUp()

        fti = DexterityFTI('OpenGeverBaseFTI')
        fti.schema = 'opengever.base.tests.emptyschema.IEmptySchema'
        fti.behaviors = ('opengever.base.behaviors.base.IOpenGeverBase',)
        self.portal.portal_types._setObject('OpenGeverBaseFTI', fti)
        fti.lookupSchema()
        transaction.commit()

    @browsing
    def test_base_behavior(self, browser):
        browser.login().open(self.portal)

        factoriesmenu.add('OpenGeverBaseFTI')
        browser.fill({'Title': 'Foo', 'Description': 'Bar'})
        browser.click_on('Save')

        self.assertEquals(
            'http://nohost/plone/opengeverbasefti/view', browser.url)

        obj = self.portal.opengeverbasefti
        self.assertEquals('Foo', obj.Title())
        self.assertEquals('Bar', obj.Description())

    @browsing
    def test_base_behavior_uses_common_fieldset(self, browser):
        browser.login().open(self.portal)

        factoriesmenu.add('OpenGeverBaseFTI')
        browser.fill({'Title': 'Foo', 'Description': 'Bar'})
        browser.click_on('Save')

        self.assertEquals(['Common'], browser.css('fieldset legend').text)
