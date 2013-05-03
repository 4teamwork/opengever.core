from Products.CMFCore.utils import getToolByName
from opengever.core.testing import OPENGEVER_FUNCTIONAL_TESTING
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.app.testing import setRoles
from plone.testing.z2 import Browser
import transaction
import unittest2 as unittest

class TestContact(unittest.TestCase):

    layer = OPENGEVER_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.browser = Browser(self.app)
        self.browser.handleErrors = False
        setRoles(self.portal, TEST_USER_ID, ['Member', 'Contributor', 'Manager'])
        transaction.commit()

    def obj2brain(self, obj):
        catalog = getToolByName(obj, 'portal_catalog')
        query = {'path': {'query': '/'.join(obj.getPhysicalPath()),
                          'depth': 0}}
        brains = catalog(query)
        if len(brains) == 0:
            raise Exception('Not in catalog: %s' % obj)
        else:
            return brains[0]

    def getSearchableText(self, obj):
        brain = self.obj2brain(obj)
        catalog = getToolByName(obj, 'portal_catalog')
        data = catalog.getIndexDataForRID(brain.getRID())
        return data['SearchableText']

    def test_browser(self):
        self.browser.addHeader('Authorization', 'Basic %s:%s' % (TEST_USER_NAME, TEST_USER_PASSWORD,))
        self.browser.open(self.portal.portal_url())
        self.assertIn('test_user_1', self.browser.contents)

        # create a contact folder
        self.browser.open('http://nohost/plone/folder_factories')
        self.browser.getControl('ContactFolder').click()
        self.browser.getControl('Add').click()
        self.assertEquals('http://nohost/plone/++add++opengever.contact.contactfolder',
                          self.browser.url)
        self.browser.getControl('Title').value='Foobar'
        self.browser.getControl('Description').value='Lorem Ipsum'
        self.browser.getControl('Save').click()

        # create a contact:
        self.browser.open('http://nohost/plone/foobar/folder_factories')
        self.browser.getControl('Contact').click()
        self.browser.getControl('Add').click()

        self.assertEquals('http://nohost/plone/foobar/++add++opengever.contact.contact',
                          self.browser.url)
        self.browser.getControl('Firstname').value = 'lorem'
        self.browser.getControl('Save').click()

        self.assertEquals('http://nohost/plone/foobar/++add++opengever.contact.contact',
                          self.browser.url)

        self.browser.getControl('Firstname').value = 'Hanspeter'
        self.browser.getControl('Lastname').value = 'Walter'
        self.browser.getControl('Description').value = 'Lorem ipsum, bla bla'
        self.browser.getControl('Save').click()
        self.assertEquals('http://nohost/plone/foobar/walter-hanspeter/contact_view',
                          self.browser.url)

        # test searchabelText indexing
        obj = self.portal.get('foobar').get('walter-hanspeter')
        self.assertEquals(['walter', 'hanspeter'], self.getSearchableText(obj))

        folder = self.portal.get('foobar')
        self.assertEquals('Foobar', folder.Title())
        self.assertEquals('Lorem Ipsum', folder.Description())

        contact = folder.get('walter-hanspeter')
        self.assertEquals('Walter Hanspeter', contact.Title())
        self.assertEquals('Lorem ipsum, bla bla', contact.Description())
