from opengever.dossier.interfaces import IDossierArchiver
from opengever.testing import IntegrationTestCase
from plone import api


class TestCatalog(IntegrationTestCase):

    def test_reindex_is_subdossier_index_after_moving_subdossier(self):
        self.login(self.dossier_responsible)
        api.content.move(source=self.subdossier, target=self.leaf_repofolder)
        self.assert_index_value(False, 'is_subdossier', self.subdossier)

    def test_containing_dossier_index_and_metadata(self):
        """The ``containing_dossier`` index contains the title of the main
        dossier if the object is the main dossier or any parent is the main
        dossier.
        """
        self.login(self.regular_user)
        self.assert_index_and_metadata(
            None,
            'containing_dossier',
            self.leaf_repofolder)

        self.assert_index_and_metadata(
            self.dossier.Title(),
            'containing_dossier',
            self.dossier,
            self.document,
            self.subdossier,
            self.subdocument,
            self.task,
            self.subtask,
            self.taskdocument)

    def test_containing_subdossier_index_and_metadata(self):
        """The ``containing_subdossier`` index contains the title of the
        subdossier if a parent of the object is a subdossier.
        """
        self.login(self.regular_user)
        self.assert_index_and_metadata(
            '',
            'containing_subdossier',
            self.leaf_repofolder,
            self.dossier,
            self.subdossier,
            self.document,
            self.task,
            self.subtask,
            self.taskdocument)

        self.assert_index_and_metadata(
            self.subdossier.Title(),
            'containing_subdossier',
            self.subdocument)


class TestFilingCatalog(IntegrationTestCase):
    features = ('filing_number',)

    def test_filing_no_index_and_metadata(self):
        self.login(self.regular_user)
        IDossierArchiver(self.dossier).archive('admin', '2013', 'Foo')
        self.assert_index_and_metadata('Foo', 'filing_no', self.dossier)
        self.assert_index_and_metadata('Foo.1', 'filing_no', self.subdossier)
        self.assert_index_and_metadata('Foo.2', 'filing_no', self.subdossier2)

    def test_searchable_filing_no_index(self):
        self.login(self.regular_user)
        IDossierArchiver(self.dossier).archive('admin', '2013', 'Foo')
        self.assert_index_value(['foo'], 'searchable_filing_no', self.dossier)
        self.assert_index_value(['foo', u'1'], 'searchable_filing_no', self.subdossier)
        self.assert_index_value(['foo', u'2'], 'searchable_filing_no', self.subdossier2)
