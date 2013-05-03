from opengever.core.testing import OPENGEVER_FUNCTIONAL_TESTING
from opengever.repository.behaviors.referenceprefix import IReferenceNumberPrefix
from opengever.repository.repositoryfolder import IRepositoryFolderSchema
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME, TEST_USER_PASSWORD
from plone.app.testing import setRoles
from plone.dexterity.interfaces import IDexterityFTI
from plone.testing.z2 import Browser
from zope.component import createObject
from zope.component import queryUtility
import transaction
import unittest2 as unittest


class TestRepositoryFolder(unittest.TestCase):
    layer = OPENGEVER_FUNCTIONAL_TESTING

    def test_adding(self):
        portal = self.layer['portal']
        setRoles(portal, TEST_USER_ID, ['Reviewer', 'Manager'])
        portal.invokeFactory('opengever.repository.repositoryfolder', 'repository1')
        r1 = portal['repository1']
        self.failUnless(IRepositoryFolderSchema.providedBy(r1))

    def test_fti(self):
        fti = queryUtility(IDexterityFTI, name='opengever.repository.repositoryfolder')
        self.assertNotEquals(None, fti)

    def test_schema(self):
        fti = queryUtility(IDexterityFTI, name='opengever.repository.repositoryfolder')
        schema = fti.lookupSchema()
        self.assertEquals(IRepositoryFolderSchema, schema)

    def test_factory(self):
        fti = queryUtility(IDexterityFTI, name='opengever.repository.repositoryfolder')
        factory = fti.factory
        new_object = createObject(factory)
        self.failUnless(IRepositoryFolderSchema.providedBy(new_object))


class TestRepositoryFolderWithBrowser(unittest.TestCase):
    layer = OPENGEVER_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.app = self.layer['app']
        self.request = self.layer['request']

        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        transaction.commit()

        # Since the Generic Setup profile was imported,
        # we should have a some FTIs registered::
        pt = self.portal.portal_types
        pt.get('opengever.repository.repositoryfolder', None)
        pt.get('opengever.repository.repositoryroot', None)

        # For surfing we need a Browser::
        self.browser = Browser(self.app)
        self.browser.handleErrors = False
        self.browser.addHeader('Authorization', 'Basic %s:%s' % (TEST_USER_NAME, TEST_USER_PASSWORD,))

    def test_repository_folder(self):
        # So, lets create the repository-root::
        self.browser.open('http://nohost/plone/folder_factories')
        self.assertIn('opengever.repository.repositoryroot', self.browser.contents)
        self.browser.getControl('RepositoryRoot').click()
        self.browser.getControl('Add').click()
        self.browser.getControl('Title').value = 'Registraturplan'
        self.browser.getControl('Description').value = ''
        self.browser.getControl('Save').click()
        self.assertEquals('http://nohost/plone/registraturplan/tabbed_view', self.browser.url)

        # Now, create our first repository folder::
        self.browser.open('./folder_factories')
        self.assertIn('opengever.repository.repositoryfolder', self.browser.contents)
        self.browser.getControl('RepositoryFolder').click()
        self.browser.getControl('Add').click()
        self.browser.getControl('Title').value = 'Accounting'
        self.browser.getControl('Save').click()
        self.assertEquals('http://nohost/plone/registraturplan/accounting/tabbed_view', self.browser.url)

        # Check some stuff::
        obj = self.portal.get('registraturplan').get('accounting')
        self.assertEquals(u'1', IReferenceNumberPrefix(obj).reference_number_prefix)
        self.assertEquals(('test_user_1_',), obj.listCreators())

        # Add another one::
        self.browser.open('http://nohost/plone/registraturplan/++add++opengever.repository.repositoryfolder')
        self.browser.getControl('Title').value = 'Custody'
        self.browser.getControl('Save').click()
        self.assertEquals(self.browser.url, 'http://nohost/plone/registraturplan/custody/tabbed_view')

        obj = self.portal.get('registraturplan').get('custody')
        self.assertEquals(u'2', IReferenceNumberPrefix(obj).reference_number_prefix)
