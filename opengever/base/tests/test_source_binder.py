from ftw.builder import Builder
from ftw.builder import create
from opengever.base.source import DossierPathSourceBinder
from opengever.base.source import RepositoryPathSourceBinder
from opengever.testing import FunctionalTestCase


class TestRepositoryPathSourceBinder(FunctionalTestCase):

    def setUp(self):
        super(TestRepositoryPathSourceBinder, self).setUp()
        self.grant('Administrator', 'Contributor', 'Editor', 'Reader')

        self.reporoot_1 = create(Builder('repository_root')
                                 .titled(u'Ordnungssystem1'))
        self.repofolder1 = create(Builder('repository')
                                  .within(self.reporoot_1))
        self.repofolder1_1 = create(Builder('repository')
                                    .within(self.repofolder1))

        self.reporoot2 = create(Builder('repository_root')
                                .titled(u'Ordnungssystem2'))
        self.repofolder2 = create(Builder('repository').within(self.reporoot2))

    def test_root_path_is_limited_to_current_repository(self):
        source_binder = RepositoryPathSourceBinder()
        source = source_binder(self.repofolder1_1)
        self.assertEqual('/plone/ordnungssystem1',
                         source.root_path)
        source = source_binder(self.repofolder1)
        self.assertEqual('/plone/ordnungssystem1',
                         source.root_path)


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
