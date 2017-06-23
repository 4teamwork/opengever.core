from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages import plone
from ftw.testbrowser.pages import statusmessages
from opengever.base.behaviors.lifecycle import ARCHIVAL_VALUE_UNCHECKED
from opengever.base.interfaces import IReferenceNumberSettings
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.repository.behaviors.referenceprefix import IReferenceNumberPrefix
from opengever.repository.interfaces import IRepositoryFolder
from opengever.repository.interfaces import IRepositoryFolderRecords
from opengever.testing import IntegrationTestCase
from opengever.testing import obj2brain
from opengever.testing import set_preferred_language
from plone import api
from plone.registry.interfaces import IRegistry
from zope.component import getUtility


class TestRepositoryFolder(IntegrationTestCase):

    def test_Title_is_prefixed_with_reference_number(self):
        self.assertEquals('1.1. Vertr\xc3\xa4ge und Vereinbarungen',
                          self.leaf_repository.Title())

    def test_Title_accessor_use_reference_formatters_seperator(self):
        registry = getUtility(IRegistry)
        proxy = registry.forInterface(IReferenceNumberSettings)
        proxy.formatter = 'grouped_by_three'
        self.assertEquals('11 Vertr\xc3\xa4ge und Vereinbarungen',
                          self.leaf_repository.Title())

    def test_Title_returns_title_in_current_language(self):
        set_preferred_language(self.portal.REQUEST, 'fr-ch')
        self.assertEquals('1.1. Contrats et accords', self.leaf_repository.Title())

        set_preferred_language(self.portal.REQUEST, 'de-ch')
        self.assertEquals('1.1. Vertr\xc3\xa4ge und Vereinbarungen',
                          self.leaf_repository.Title())

    def test_title_indexes(self):
        brain = obj2brain(self.leaf_repository)
        self.assertEquals(u'1.1. Contrats et accords', brain.title_fr)
        self.assertEquals(u'1.1. Vertr\xe4ge und Vereinbarungen', brain.title_de)

    def test_get_archival_value(self):
        self.assertEquals(ARCHIVAL_VALUE_UNCHECKED,
                          self.leaf_repository.get_archival_value())

    @browsing
    def test_create_repository_folder(self, browser):
        self.login(self.administrator)
        browser.login(self.administrator).open(self.branch_repository)
        factoriesmenu.add('RepositoryFolder')
        browser.fill({'Title': 'Custody'}).save()
        statusmessages.assert_no_error_messages()
        self.assertEquals(('tabbed_view', 'opengever-repository-repositoryfolder'),
                          plone.view_and_portal_type())
        custody = browser.context
        self.assertEquals(u'2', IReferenceNumberPrefix(custody).reference_number_prefix)

    @browsing
    def test_warn_when_adding_repo_to_repo_with_dossier(self, browser):
        """A repository folder should not contain other repository folders AND
        dossiers at the same time.
        But in order to migrate from "contains dossiers" to "contains folders"
        we need to allow creating repositories within repositories which already
        contain dossiers.
        But a warning message should be displayed in this situation.
        """
        self.login(self.administrator)
        browser.login(self.administrator)

        warning = u'You are adding a repositoryfolder to a leafnode ' \
                  u'which already contains dossiers. This is only ' \
                  u'temporarily allowed and all dossiers must be moved into ' \
                  u'a new leafnode afterwards.'

        self.assertTrue(any(filter(IDossierMarker.providedBy,
                                   self.leaf_repository.objectValues())),
                        'Expected at least one dossier within leaf_repository.')
        browser.open(self.leaf_repository)
        factoriesmenu.add('RepositoryFolder')
        statusmessages.assert_message(warning)

        self.assertFalse(any(filter(IDossierMarker.providedBy,
                                    self.branch_repository.objectValues())),
                         'Expected no dossiers within branch_repository.')
        browser.open(self.branch_repository)
        factoriesmenu.add('RepositoryFolder')
        statusmessages.assert_no_messages()

        self.assertFalse(any(filter(IDossierMarker.providedBy,
                                    self.empty_repository.objectValues())),
                         'Expected no dossiers within empty_repository.')
        browser.open(self.empty_repository)
        factoriesmenu.add('RepositoryFolder')
        statusmessages.assert_no_messages()

    @browsing
    def test_only_repository_addable_when_already_contains_repositories(self, browser):
        """A repository folder should not contain other repository folders AND
        dossiers at the same time.
        Therefore dossiers should not be addable in branch repository folders.
        """
        self.login(self.administrator)
        browser.login(self.administrator)

        self.assertTrue(any(filter(IRepositoryFolder.providedBy,
                                   self.branch_repository.objectValues())),
                        'Expected repositories within branch_repository.')
        browser.open(self.branch_repository)
        self.assertEquals(
            ['RepositoryFolder'],
            factoriesmenu.addable_types())

    @browsing
    def test_dossiers_addable_in_empty_repository_folder(self, browser):
        """A repository folder should not contain other repository folders AND
        dossiers at the same time.
        Therefore dossiers should be addable in empty repository folders.
        """
        self.login(self.administrator)
        browser.login(self.administrator)

        self.assertFalse(any(filter(IRepositoryFolder.providedBy,
                                    self.empty_repository.objectValues())),
                         'Expected no repositories within empty_repository.')
        browser.open(self.empty_repository)
        self.assertEquals(
            ['Business Case Dossier', 'RepositoryFolder'],
            factoriesmenu.addable_types())

    @browsing
    def test_max_depth_causes_repositories_to_not_be_addable(self, browser):
        self.login(self.administrator)
        browser.login(self.administrator)

        browser.open(self.leaf_repository)
        self.assertIn('RepositoryFolder', factoriesmenu.addable_types())

        api.portal.set_registry_record(
            'maximum_repository_depth', 1,
            interface=IRepositoryFolderRecords)
        browser.reload()
        self.assertNotIn('RepositoryFolder', factoriesmenu.addable_types())


class TestDossierTemplateFactoryMenu(IntegrationTestCase):

    features = ('dossiertemplate',)

    def setUp(self):
        super(TestDossierTemplateFactoryMenu, self).setUp()
        self.factory_label = 'Dossier with template'

    @browsing
    def test_adding_from_template_allowed_on_leaf_nodes(self, browser):
        self.login(self.administrator)
        browser.login(self.administrator).open(self.leaf_repository)
        self.assertIn(self.factory_label, factoriesmenu.addable_types())

    @browsing
    def test_adding_from_template_not_allowed_on_branch_nodes(self, browser):
        self.login(self.administrator)
        browser.login(self.administrator).open(self.branch_repository)
        self.assertNotIn(self.factory_label, factoriesmenu.addable_types())
