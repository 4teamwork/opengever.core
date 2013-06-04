from opengever.base.behaviors import creator
from plone.dexterity.fti import DexterityFTI
from opengever.testing import FunctionalTestCase
import transaction

class TestCreatorBehavior(FunctionalTestCase):
    """
    The Creator behavior sets the creator an content creation.
    It also adds a creators field with listCreators() and setCreators()
    methods. The field is hidden by default.
    """
    use_browser = True

    def setUp(self):
        super(TestCreatorBehavior, self).setUp()
        self.grant('Contributor')

        fti = DexterityFTI('ReferenceFTI')
        fti.behaviors = ('opengever.base.behaviors.creator.ICreator',)
        self.portal.portal_types._setObject('ReferenceFTI', fti)
        fti.lookupSchema()
        transaction.commit()

    def test_creator(self):
        self.browser.open('http://nohost/plone/folder_factories')
        self.assertPageContains('ReferenceFTI')
        self.browser.getControl('ReferenceFTI').click()
        self.browser.getControl('Add').click()
        self.browser.assert_url('http://nohost/plone/++add++ReferenceFTI')
        self.assertPageContainsNot('creators')
        self.browser.getControl('Title').value = 'Hallo Hugo'
        self.browser.getControl('Save').click()
        self.browser.assert_url('http://nohost/plone/referencefti/view')

        obj = self.portal.get('referencefti')
        self.assertTrue(creator.ICreatorAware.providedBy( obj ))

        self.assertEquals(('test_user_1_',), obj.listCreators())
        self.assertEquals('test_user_1_', obj.Creator())

        obj.setCreators(('foo',))
        self.assertEquals(('foo',), obj.listCreators())

        obj.addCreator('bar')
        self.assertEquals(('foo', 'bar'), obj.listCreators())
