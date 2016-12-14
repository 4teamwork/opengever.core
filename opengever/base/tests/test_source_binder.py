from ftw.builder import Builder
from ftw.builder import create
from opengever.base.source import DossierPathSourceBinder
from opengever.base.source import RepositoryPathSourceBinder
from opengever.testing import FunctionalTestCase


class TestSourceBinder(FunctionalTestCase):

    def setUp(self):
        super(TestSourceBinder, self).setUp()
        self.grant('Administrator', 'Contributor', 'Editor', 'Reader')

        # Repository 1
        reporoot1 = create(Builder('repository_root').titled('Ordnungssystem1'))
        repofolder1 = create(Builder('repository').within(reporoot1))
        repofolder2 = create(Builder('repository').within(repofolder1))
        create(Builder('repository').within(reporoot1))
        self.repofolder2_1 = create(Builder('repository').within(repofolder2))
        # Repository 2
        reporoot2 = create(Builder('repository_root').titled('Ordnungssystem2'))
        for index in range(3):
            create(Builder('repository').within(reporoot2))

    def test_sourcebinder(self):
        """
        Check if SourceBinder works correctly without a querymodificator
        """
        query = RepositoryPathSourceBinder()(self.repofolder2_1)
        self.assertEqual(
            {'query': '/plone/ordnungssystem1'},
            query.navigation_tree_query['path'])
        self.assertEqual(
            5,
            len(query.catalog.searchResults(query.navigation_tree_query)))


class TestDossierSourceBinder(FunctionalTestCase):

    def test_only_objects_inside_the_maindossier_are_selectable(self):
        dossier_1 = create(Builder('dossier'))
        sub = create(Builder('dossier').within(dossier_1))
        dossier_2 = create(Builder('dossier'))
        create(Builder('document').titled(u'Test 1').within(dossier_1))
        create(Builder('document').titled(u'Test 2').within(dossier_2))

        source_binder = DossierPathSourceBinder(
            portal_type=("opengever.document.document", "ftw.mail.mail"),
            navigation_tree_query={
                'object_provides':
                ['opengever.dossier.behaviors.dossier.IDossierMarker',
                 'opengever.document.document.IDocumentSchema',
                 'opengever.task.task.ITask',
                 'ftw.mail.mail.IMail']}
        )

        source = source_binder(dossier_1)
        self.assertEqual(
            ['Test 1'], [term.title for term in source.search('Test')])

        source = source_binder(sub)
        self.assertEqual(
            ['Test 1'], [term.title for term in source.search('Test')])
