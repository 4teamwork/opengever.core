from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages import plone
from opengever.base.adapters import ReferenceNumberPrefixAdpater
from opengever.base.interfaces import IReferenceNumberSettings
from opengever.repository.behaviors.referenceprefix import IReferenceNumberPrefix
from opengever.repository.repositoryfolder import IRepositoryFolderSchema
from opengever.testing import FunctionalTestCase
from plone.dexterity.interfaces import IDexterityFTI
from plone.protect import createToken
from plone.registry.interfaces import IRegistry
from zope.component import createObject
from zope.component import getUtility
from zope.component import queryUtility
import transaction


class TestRepositoryFolder(FunctionalTestCase):

    def test_adding(self):
        self.grant('Reviewer', 'Manager')
        self.portal.invokeFactory('opengever.repository.repositoryfolder', 'repository1')
        r1 = self.portal['repository1']
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


class TestRepositoryFolderTitleAccessor(FunctionalTestCase):

    def setUp(self):
        super(TestRepositoryFolderTitleAccessor, self).setUp()

        repository_1 = create(Builder('repository'))

        repository_1_1 = create(Builder('repository')
                                .within(repository_1))

        self.repository_folder = create(Builder('repository')
                                  .within(repository_1_1)
                                  .titled(u'Repositoryfolder XY'))

    def test_returns_reference_number_and_title_seperatoded_with_space(self):
        self.assertEquals(
            '1.1.1. Repositoryfolder XY',
            self.repository_folder.Title())

    def test_Title_accessor_use_reference_formatters_seperator(self):
        registry = getUtility(IRegistry)
        proxy = registry.forInterface(IReferenceNumberSettings)
        proxy.formatter = 'grouped_by_three'

        self.assertEquals(
            '111 Repositoryfolder XY',
            self.repository_folder.Title())


class TestRepositoryFolderWithBrowser(FunctionalTestCase):

    def setUp(self):
        super(TestRepositoryFolderWithBrowser, self).setUp()
        self.grant('Manager')

    @browsing
    def test_repository_folder(self, browser):
        browser.login().open()
        factoriesmenu.add('RepositoryRoot')
        browser.fill({'Title': 'Registraturplan'}).save()
        self.assertEquals(('tabbed_view', 'opengever-repository-repositoryroot'),
                          plone.view_and_portal_type())
        registraturplan = browser.context

        # This will cause a WRITE to registraturplan the first time it is accessed.
        browser.open(registraturplan, view='++add++opengever.repository.repositoryfolder',
                     data={'_authenticator': createToken()})
        browser.fill({'Title': 'Accounting'}).save()
        self.assertEquals(('tabbed_view', 'opengever-repository-repositoryfolder'),
                          plone.view_and_portal_type())
        accounting = browser.context
        self.assertEquals(u'1', IReferenceNumberPrefix(accounting).reference_number_prefix)
        self.assertEquals(('test_user_1_',), accounting.listCreators())

        browser.open(registraturplan)
        factoriesmenu.add('RepositoryFolder')
        browser.fill({'Title': 'Custody'}).save()
        self.assertEquals(('tabbed_view', 'opengever-repository-repositoryfolder'),
                          plone.view_and_portal_type())
        custody = browser.context
        self.assertEquals(u'2', IReferenceNumberPrefix(custody).reference_number_prefix)
