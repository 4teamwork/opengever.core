from opengever.testing import FunctionalTestCase
from plone.dexterity.fti import DexterityFTI
import transaction

class TestBaseBehavior(FunctionalTestCase):
    use_browser = True

    def setUp(self):
        super(TestBaseBehavior, self).setUp()
        self.grant('Contributor')

        fti = DexterityFTI('OpenGeverBaseFTI')
        fti.schema = 'opengever.base.tests.emptyschema.IEmptySchema'
        fti.behaviors = ('opengever.base.behaviors.base.IOpenGeverBase',)
        self.portal.portal_types._setObject('OpenGeverBaseFTI', fti)
        fti.lookupSchema()
        transaction.commit()

    def test_base_behavior(self):
        # We can see this type in the addable types at the root of the site:
        self.browser.open('http://nohost/plone/folder_factories')

        self.browser.getControl('OpenGeverBaseFTI').click()
        self.browser.getControl('Add').click()
        self.browser.assert_url('http://nohost/plone/++add++OpenGeverBaseFTI')

        self.browser.getControl(name='form.widgets.IOpenGeverBase.title').value = 'Foo'
        self.browser.getControl(name='form.widgets.IOpenGeverBase.description').value = 'Bar'
        self.browser.getControl('Save').click()
        self.browser.assert_url('http://nohost/plone/opengeverbasefti/view')

        # Get the created object:
        obj = self.portal.opengeverbasefti

        # Title should be set:
        self.assertEquals('Foo', obj.Title())
        self.assertEquals('Bar', obj.Description())

        # We use the "Common" fieldset, not the "Default" fieldset:
        self.browser.open('http://nohost/plone/opengeverbasefti/edit')
        self.assertPageContains('Common')
