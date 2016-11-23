from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages import plone
from ftw.testbrowser.pages.statusmessages import warning_messages
from opengever.base.interfaces import IReferenceNumberSettings
from opengever.core.testing import OPENGEVER_FUNCTIONAL_DOSSIER_TEMPLATE_LAYER
from opengever.repository.behaviors.referenceprefix import IReferenceNumberPrefix
from opengever.repository.interfaces import IRepositoryFolderRecords
from opengever.testing import add_languages
from opengever.testing import FunctionalTestCase
from opengever.testing import obj2brain
from opengever.testing import set_preferred_language
from plone import api
from plone.protect import createToken
from plone.registry.interfaces import IRegistry
from zope.component import getUtility


class TestRepositoryFolderTitle(FunctionalTestCase):

    def setUp(self):
        super(TestRepositoryFolderTitle, self).setUp()

        repository_1 = create(Builder('repository'))

        repository_1_1 = create(Builder('repository')
                                .within(repository_1))

        self.repository_folder = create(Builder('repository')
                                        .within(repository_1_1)
                                        .having(title_de=u'F\xfchrung',
                                                title_fr=u'Direction'))

    def test_returns_reference_number_and_title_separated_with_space(self):
        self.assertEquals('1.1.1. F\xc3\xbchrung', self.repository_folder.Title())

    def test_Title_accessor_use_reference_formatters_seperator(self):
        registry = getUtility(IRegistry)
        proxy = registry.forInterface(IReferenceNumberSettings)
        proxy.formatter = 'grouped_by_three'

        self.assertEquals('111 F\xc3\xbchrung', self.repository_folder.Title())

    def test_Title_returns_title_in_current_language(self):
        set_preferred_language(self.portal.REQUEST, 'fr-ch')
        self.assertEquals('1.1.1. Direction', self.repository_folder.Title())

        set_preferred_language(self.portal.REQUEST, 'de-ch')
        self.assertEquals('1.1.1. F\xc3\xbchrung', self.repository_folder.Title())

    def test_title_indexes(self):
        brain = obj2brain(self.repository_folder)
        self.assertEquals(u'1.1.1. Direction', brain.title_fr)
        self.assertEquals(u'1.1.1. F\xfchrung', brain.title_de)


class TestRepositoryFolderWithBrowser(FunctionalTestCase):

    def setUp(self):
        super(TestRepositoryFolderWithBrowser, self).setUp()
        add_languages(['de-ch'])

    @browsing
    def test_repository_folder(self, browser):
        self.grant('Manager')

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

    @browsing
    def test_add_form_shows_warning_message_when_repositoryfolder_contains_dossiers(self, browser):
        self.grant('Manager')

        root = create(Builder('repository_root'))
        branch_node = create(Builder('repository').within(root))
        leaf_node = create(Builder('repository').within(branch_node))
        create(Builder('dossier').within(leaf_node))

        browser.login().open(
            branch_node, view='++add++opengever.repository.repositoryfolder')
        self.assertEquals([], warning_messages())

        browser.login().open(
            leaf_node, view='++add++opengever.repository.repositoryfolder')
        self.assertEquals(
            [u'You are adding a repositoryfolder to a leafnode '
             'which already contains dossiers. This is only '
             'temporarily allowed and all dossiers must be moved into '
             'a new leafnode afterwards.'],
            warning_messages())

    @browsing
    def test_addable_types_on_a_repository_folder_containing_other_repo_folders(self, browser):
        self.grant('Manager')

        root = create(Builder('repository_root'))
        branch_node = create(Builder('repository').within(root))
        leaf_node = create(Builder('repository').within(branch_node))

        browser.login().open(branch_node)

        self.assertEquals(
            ['RepositoryFolder'],
            factoriesmenu.addable_types())

    @browsing
    def test_addable_types_on_a_repository_leaf_folder(self, browser):
        self.grant('Manager')

        api.portal.set_registry_record(
            'maximum_repository_depth', 3,
            interface=IRepositoryFolderRecords)

        root = create(Builder('repository_root'))
        branch_node = create(Builder('repository').within(root))
        leaf_node = create(Builder('repository').within(branch_node))

        browser.login().open(leaf_node)

        self.assertEquals(
            ['Business Case Dossier', 'Disposition', 'RepositoryFolder'],
            factoriesmenu.addable_types())

    @browsing
    def test_addable_types_on_a_repository_leaf_folder_if_max_rep_depth_reached(self, browser):
        self.grant('Manager')

        api.portal.set_registry_record(
            'maximum_repository_depth', 2,
            interface=IRepositoryFolderRecords)

        root = create(Builder('repository_root'))
        branch_node = create(Builder('repository').within(root))
        leaf_node = create(Builder('repository').within(branch_node))

        browser.login().open(leaf_node)

        self.assertEquals(
            ['Business Case Dossier', 'Disposition'],
            factoriesmenu.addable_types())


class TestDossierTemplateFeatureEnabled(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_DOSSIER_TEMPLATE_LAYER

    @browsing
    def test_addable_types_on_a_repository_folder_containing_other_repo_folders(self, browser):
        self.grant('Manager')

        root = create(Builder('repository_root'))
        branch_node = create(Builder('repository').within(root))
        leaf_node = create(Builder('repository').within(branch_node))

        browser.login().open(branch_node)

        self.assertEquals(
            ['RepositoryFolder'],
            factoriesmenu.addable_types())

    @browsing
    def test_addable_types_on_a_repository_leaf_folder(self, browser):
        self.grant('Manager')

        api.portal.set_registry_record(
            'maximum_repository_depth', 3,
            interface=IRepositoryFolderRecords)

        root = create(Builder('repository_root'))
        branch_node = create(Builder('repository').within(root))
        leaf_node = create(Builder('repository').within(branch_node))

        browser.login().open(leaf_node)

        self.assertEquals(
            ['Business Case Dossier', 'Disposition', 'Dossier with template', 'RepositoryFolder'],
            factoriesmenu.addable_types())

    @browsing
    def test_addable_types_on_a_repository_leaf_folder_if_max_rep_depth_reached(self, browser):
        self.grant('Manager')

        api.portal.set_registry_record(
            'maximum_repository_depth', 2,
            interface=IRepositoryFolderRecords)

        root = create(Builder('repository_root'))
        branch_node = create(Builder('repository').within(root))
        leaf_node = create(Builder('repository').within(branch_node))

        browser.login().open(leaf_node)

        self.assertEquals(
            ['Business Case Dossier', 'Disposition', 'Dossier with template'],
            factoriesmenu.addable_types())
