from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.base.source import DossierPathSourceBinder
from opengever.base.source import RepositoryPathSourceBinder
from opengever.repository.browser.primary_repository_root import PrimaryRepositoryRoot
from opengever.testing import IntegrationTestCase
from opengever.testing import SolrIntegrationTestCase


class TestRepositoryPathSourceBinderSolr(SolrIntegrationTestCase):

    def test_navigation_tree_query_is_limited_to_current_repository(self):
        self.login(self.regular_user)

        source_binder = RepositoryPathSourceBinder()

        source = source_binder(self.branch_repofolder)
        self.assertEqual({'query': '/plone/ordnungssystem'},
                         source.navigation_tree_query['path'])

        source = source_binder(self.leaf_repofolder)
        self.assertEqual({'query': '/plone/ordnungssystem'},
                         source.navigation_tree_query['path'])

    def test_query_is_limited_to_current_repository(self):
        self.login(self.manager)

        source_binder = RepositoryPathSourceBinder()
        source = source_binder(self.branch_repofolder)

        self.document.title = 'source test document'
        self.document.reindexObject()

        self.proposaldocument.title = 'source test proposal document'
        self.proposaldocument.reindexObject()

        self.inbox_document.title = 'source test inbox document'
        self.inbox_document.reindexObject()

        self.private_document.title = 'source test private document'
        self.private_document.reindexObject()
        self.commit_solr()

        self.assertItemsEqual(
            ['source test document', 'source test proposal document'],
            [term.title for term in source.search("source")])

    def test_query_returns_all_reporoots_if_context_is_within_old_reporoot(self):
        self.login(self.manager)

        root_new = create(Builder('repository_root').having(title_en=u'source new repository'))
        root_new.reindexObject()

        branch_new = create(Builder('repository').within(root_new).having(title_en=u'source branch new'))
        branch_new.reindexObject()

        self.repository_root.title_en = u'source old repository'
        self.repository_root.reindexObject()

        self.document.title = u'source test document'
        self.document.reindexObject()

        self.proposaldocument.title = u'source test proposal document'
        self.proposaldocument.reindexObject()

        self.inbox_document.title = u'source test inbox document'
        self.inbox_document.reindexObject()

        self.private_document.title = u'source test private document'
        self.private_document.reindexObject()
        self.commit_solr()

        source_binder = RepositoryPathSourceBinder()
        source = source_binder(self.branch_repofolder)

        self.assertEqual(
            root_new,
            PrimaryRepositoryRoot(self.branch_repofolder, self.request).get_primary_repository_root(),
            "root_new should be the primary repository root")

        self.assertItemsEqual(
            [
                'source old repository', 'source new repository', 'source test document',
                '1. source branch new', 'source test inbox document',
                'source test private document', 'source test proposal document'
            ],
            [term.title for term in source.search("source")])

    def test_query_returns_only_primary_root_if_context_is_within_new_reporoot(self):
        self.login(self.manager)

        root_new = create(Builder('repository_root').having(title_en=u'source new repository'))
        root_new.reindexObject()

        branch_new = create(Builder('repository').within(root_new).having(title_en=u'source branch new'))
        branch_new.reindexObject()

        self.repository_root.title_en = u'source old repository'
        self.repository_root.reindexObject()

        self.document.title = u'source test document'
        self.document.reindexObject()

        self.proposaldocument.title = u'source test proposal document'
        self.proposaldocument.reindexObject()

        self.inbox_document.title = u'source test inbox document'
        self.inbox_document.reindexObject()

        self.private_document.title = u'source test private document'
        self.private_document.reindexObject()
        self.commit_solr()

        source_binder = RepositoryPathSourceBinder()
        source = source_binder(branch_new)

        self.assertEqual(
            root_new,
            PrimaryRepositoryRoot(self.branch_repofolder, self.request).get_primary_repository_root(),
            "root_new should be the primary repository root")

        self.assertItemsEqual(
            ['source new repository', '1. source branch new'],
            [term.title for term in source.search("source")])


class TestDossierSourceBinder(SolrIntegrationTestCase):

    def test_only_objects_inside_the_maindossier_are_selectable(self):
        self.login(self.regular_user)

        self.document.title = 'Test open'
        self.subdocument.title = 'Test sub'
        self.inactive_document.title = 'Test inactive'
        [obj.reindexObject() for obj in
         (self.document, self.subdocument, self.inactive_document)]
        self.commit_solr()

        source_binder = DossierPathSourceBinder(
            portal_type=("opengever.document.document", "ftw.mail.mail"),
            navigation_tree_query={
                'object_provides':
                ['opengever.dossier.behaviors.dossier.IDossierMarker',
                 'opengever.document.document.IDocumentSchema',
                 'opengever.task.task.ITask',
                 'ftw.mail.mail.IMail']}
        )

        source = source_binder(self.dossier)
        self.assertItemsEqual(['Test sub', 'Test open'],
                              [term.title for term in source.search('title:Test')])

        source = source_binder(self.subdossier)
        self.assertItemsEqual(['Test sub', 'Test open'],
                              [term.title for term in source.search('title:Test')])

        source = source_binder(self.inactive_dossier)
        self.assertEqual(['Test inactive'],
                         [term.title for term in source.search('title:Test')])


class TestRelatedDossierAutocomplete(IntegrationTestCase):

    @browsing
    def test_related_dossier_autocomplete_uses_solr(self, browser):
        self.login(self.dossier_responsible, browser)
        with self.mock_solr('solr_autocomplete_dossier.json') as solr:
            browser.open(
                self.dossier,
                view='@@edit/++widget++form.widgets.IDossier.relatedDossier/@@autocomplete-search?q=empty'
            )
            self.assertEqual(
                '/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-7|An empty dossier',
                browser.contents
            )
            self.assert_solr_called(
                solr, 'empty', rows=20, fl=['path'],
                filters=[u'object_provides:opengever.dossier.behaviors.dossier.IDossierMarker',
                        u'path_parent:\\/plone\\/ordnungssystem']
            )


class TestAddableDossierTemplatesAutocomplete(IntegrationTestCase):

    @browsing
    def test_addable_dossier_autocomplete_uses_solr_when_feature_enabled(self, browser):
        self.login(self.administrator, browser)
        with self.mock_solr('solr_autocomplete_dossiertemplate.json') as solr:
            browser.open(
                self.empty_repofolder,
                view=''
                '@@edit/++widget++form.widgets.IRestrictAddableDossierTemplates.addable_dossier_templates/'
                '@@autocomplete-search?q=Bauvorhaben'
            )
            self.assertEqual(
                '/plone/vorlagen/dossiertemplate-1|Bauvorhaben klein',
                browser.contents
            )
            self.assert_solr_called(
                solr, 'Bauvorhaben', rows=20, fl=['path'],
                filters=[u'portal_type:opengever.dossier.dossiertemplate',
                        u'is_subdossier:false']
            )

    @browsing
    def test_addable_dossier_autocomplete_uses_catalog_when_solr_disabled(self, browser):
        self.deactivate_feature('solr')
        self.login(self.administrator, browser)
        browser.open(
            self.empty_repofolder,
            view=''
            '@@edit/++widget++form.widgets.IRestrictAddableDossierTemplates.addable_dossier_templates/'
            '@@autocomplete-search?q=Bauvorhaben'
        )
        self.assertEqual(
            '/plone/vorlagen/dossiertemplate-1|Bauvorhaben klein',
            browser.contents
        )
