from opengever.dossier.interfaces import IDossierArchiver
from opengever.testing import IntegrationTestCase
from plone import api


class TestCatalog(IntegrationTestCase):

    def test_reindex_is_subdossier_index_after_moving_subdossier(self):
        self.login(self.dossier_responsible)
        api.content.move(source=self.subdossier, target=self.leaf_repofolder)
        self.assert_index_value(False, 'is_subdossier', self.subdossier)


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
