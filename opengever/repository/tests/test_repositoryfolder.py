from opengever.core.testing import OPENGEVER_INTEGRATION_TESTING
from opengever.repository.repositoryfolder import IRepositoryFolderSchema
from plone.app.testing import setRoles, TEST_USER_ID
from plone.dexterity.interfaces import IDexterityFTI
from zope.component import createObject
from zope.component import queryUtility
import unittest2 as unittest


class TestRepositoryFolderIntegration(unittest.TestCase):

    layer = OPENGEVER_INTEGRATION_TESTING

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

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
