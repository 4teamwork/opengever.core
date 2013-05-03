from opengever.repository.repositoryroot import IRepositoryRoot
from opengever.testing import FunctionalTestCase
from plone.dexterity.interfaces import IDexterityFTI
from zope.component import createObject
from zope.component import queryUtility


class TestRepositoryRootIntegration(FunctionalTestCase):

    def test_adding(self):
        self.grant('Reviewer', 'Manager')
        self.portal.invokeFactory('opengever.repository.repositoryroot', 'repository1')
        r1 = self.portal['repository1']
        self.failUnless(IRepositoryRoot.providedBy(r1))

    def test_fti(self):
        fti = queryUtility(IDexterityFTI, name='opengever.repository.repositoryroot')
        self.assertNotEquals(None, fti)

    def test_schema(self):
        fti = queryUtility(IDexterityFTI, name='opengever.repository.repositoryroot')
        schema = fti.lookupSchema()
        self.assertEquals(IRepositoryRoot, schema)

    def test_factory(self):
        fti = queryUtility(IDexterityFTI, name='opengever.repository.repositoryroot')
        factory = fti.factory
        new_object = createObject(factory)
        self.failUnless(IRepositoryRoot.providedBy(new_object))
