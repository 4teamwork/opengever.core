import OFS.CopySupport
from Products.CMFCore.utils import getToolByName
from opengever.testing import FunctionalTestCase
from plone.dexterity.fti import DexterityFTI
from plone.dexterity.utils import createContentInContainer

class TestCopyItems(FunctionalTestCase):

    def setUp(self):
        super(TestCopyItems, self).setUp()
        self.grant('Contributor')
    
        self.request = self.layer.get('request')
        self.ptool = getToolByName(self.portal, 'plone_utils')

    def test_copy_items(self):
        # create test container and object fti:
        container = DexterityFTI('OpenGeverBaseContainer',
                                 klass="plone.dexterity.content.Container",
                                 global_allow=True, filter_content_types=False)
        self.portal.portal_types._setObject('OpenGeverBaseContainer', container)
        fti = DexterityFTI('OpenGeverBaseFTI2')
        fti.schema = 'opengever.base.tests.emptyschema.IEmptySchema'
        fti.behaviors = ('opengever.base.behaviors.base.IOpenGeverBase',)
        self.portal.portal_types._setObject('OpenGeverBaseFTI2', fti)

        # create test objects:
        createContentInContainer(self.portal, 'OpenGeverBaseContainer', title=u'container')
        folder = self.portal['opengeverbasecontainer']
        createContentInContainer(folder, 'OpenGeverBaseFTI2', title=u'doc')
        doc = folder['opengeverbasefti2']

        # test copy_items view:
        # we have to fake the request since copy_items view will redirect to the orig_template
        self.request.form['orig_template'] = folder.absolute_url()

        # should select any items
        self.assertEquals('http://nohost/plone/opengeverbasecontainer',
                          folder.restrictedTraverse('copy_items')())
        self.assertEquals(u'You have not selected any Items',
                          self.ptool.showPortalMessages()[-1].message)
        

        # Fake Itemselection
        self.portal.REQUEST['paths'] = ['/'.join(doc.getPhysicalPath())]
        self.assertEquals('http://nohost/plone/opengeverbasecontainer',
                          folder.restrictedTraverse('copy_items')())
        self.assertIn('__cp', self.portal.REQUEST.keys())

        # Check if Item has been saved to REQUEST
        self.assertEquals((0, [('', 'plone', 'opengeverbasecontainer', 'opengeverbasefti2')]),
                          OFS.CopySupport._cb_decode(self.portal.REQUEST['__cp']))
        
        # Add Second Item to test with multiple Items Selected
        createContentInContainer(folder, 'OpenGeverBaseFTI2', title=u'doc2')
        doc2 = folder['opengeverbasefti2-1']

        # Add Item to Paths
        self.portal.REQUEST['paths'].append('/'.join(doc2.getPhysicalPath()))
        self.assertEquals('http://nohost/plone/opengeverbasecontainer',
                          folder.restrictedTraverse('copy_items')())
        self.assertIn('__cp', self.portal.REQUEST.keys())

        # Test if they were copied correctly
        copiedItems = self.portal.REQUEST['__cp'].split(':')
        self.assertEquals((0, [('', 'plone', 'opengeverbasecontainer', 'opengeverbasefti2')]),
                          OFS.CopySupport._cb_decode(copiedItems[0]))
        
        self.assertEquals((0, [('', 'plone', 'opengeverbasecontainer', 'opengeverbasefti2-1')]),
                          OFS.CopySupport._cb_decode(copiedItems[1]))
        
        # Take away Copy permission
        doc.manage_permission('Copy or Move', [], acquire=False)
        self.assertEquals('http://nohost/plone/opengeverbasecontainer',
                          folder.restrictedTraverse('copy_items')())
        
        # Should not be able to copy the file
        self.assertEquals(u'The item you selected cannot be copied',
                          self.ptool.showPortalMessages()[-1].message)
