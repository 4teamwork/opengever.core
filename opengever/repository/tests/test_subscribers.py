from Acquisition import aq_inner
from Acquisition import aq_parent
from ftw.testbrowser import browsing
from opengever.testing import obj2brain
from opengever.testing import solr_data_for
from opengever.testing import SolrIntegrationTestCase
from opengever.trash.remover import Remover


class TestReferencePrefixUpdating(SolrIntegrationTestCase):

    @browsing
    def test_reference_number_is_updated_in_catalog(self, browser):
        self.login(self.administrator, browser)
        self.assertEquals('Client1 1.1', obj2brain(self.leaf_repofolder).reference)

        browser.open(self.leaf_repofolder, view='edit')
        browser.fill({'Repository number': u'7'}).save()
        self.commit_solr()

        self.assertEquals('Client1 1.7', obj2brain(self.leaf_repofolder).reference)
        self.assertEquals(u'client00000001 00000001.00000007',
                          solr_data_for(self.leaf_repofolder, 'sortable_reference'))

    @browsing
    def test_reference_number_of_children_is_updated_in_catalog(self, browser):
        self.login(self.administrator, browser)
        self.assertEqual(
            self.leaf_repofolder,
            aq_parent(aq_inner(self.dossier)),
            'Fixture: expected self.dossier to be within self.leaf_repofolder')
        self.assertEquals('Client1 1.1 / 1', obj2brain(self.dossier).reference)
        self.assertEquals(u'client00000001 00000001.00000001 / 00000001',
                          solr_data_for(self.dossier, 'sortable_reference'))

        browser.open(self.leaf_repofolder, view='edit')
        browser.fill({'Repository number': u'7'}).save()
        self.commit_solr()

        self.assertEquals('Client1 1.7 / 1', obj2brain(self.dossier).reference)
        self.assertEquals(u'client00000001 00000001.00000007 / 00000001',
                          solr_data_for(self.dossier, 'sortable_reference'))

    @browsing
    def test_reference_number_in_searchableText_gets_updated(self, browser):
        self.login(self.administrator, browser)

        self.assertIn('Client1 1.1 / 1',
                      solr_data_for(self.dossier, 'SearchableText'))
        self.assertIn('Client1 1.1 / 1 / 14',
                      solr_data_for(self.document, 'metadata'))

        browser.open(self.leaf_repofolder, view='edit')
        browser.fill({'Repository number': u'7'}).save()
        self.commit_solr()

        self.assertIn('Client1 1.7 / 1',
                      solr_data_for(self.dossier, 'SearchableText'))
        self.assertIn('Client1 1.7 / 1 / 14',
                      solr_data_for(self.document, 'metadata'))

    @browsing
    def test_reference_number_of_deleted_document_gets_updated(self, browser):
        self.login(self.manager, browser)

        self.assertEquals('Client1 1.1 / 1.1 / 24',
                          solr_data_for(self.empty_document, 'reference'))
        self.trash_documents(self.empty_document)
        Remover([self.empty_document]).remove()

        self.login(self.administrator, browser)

        browser.open(self.leaf_repofolder, view='edit')
        browser.fill({'Repository number': u'7'}).save()
        self.commit_solr()

        self.login(self.manager, browser)
        self.assertEquals('Client1 1.7 / 1.1 / 24',
                          solr_data_for(self.empty_document, 'reference'))

    @browsing
    def test_reference_number_in_repositoryfolder_titles_gets_updated(self, browser):
        self.login(self.administrator, browser)

        self.assertEquals(
            u'1.1. Vertr\xe4ge und Vereinbarungen',
            solr_data_for(self.leaf_repofolder, 'Title'))
        self.assertEquals(
            u'0001.0001. vertrage und vereinbarungen',
            solr_data_for(self.leaf_repofolder, 'sortable_title'))
        self.assertEquals(
            u'1.1. Vertr\xe4ge und Vereinbarungen',
            solr_data_for(self.leaf_repofolder, 'title_de'))
        self.assertEquals(
            u'1.1. Contrats et accords',
            solr_data_for(self.leaf_repofolder, 'title_fr'))
        self.assertEquals(
            u'1.1. Vertr\xe4ge und Vereinbarungen',
            solr_data_for(self.leaf_repofolder, 'title_en'))

        browser.open(self.branch_repofolder, view='edit')
        browser.fill({'Repository number': u'8'}).save()
        self.commit_solr()

        self.login(self.manager, browser)

        self.assertEquals(
            u'8.1. Vertr\xe4ge und Vereinbarungen',
            solr_data_for(self.leaf_repofolder, 'Title'))
        self.assertEquals(
            u'0008.0001. vertrage und vereinbarungen',
            solr_data_for(self.leaf_repofolder, 'sortable_title'))
        self.assertEquals(
            u'8.1. Vertr\xe4ge und Vereinbarungen',
            solr_data_for(self.leaf_repofolder, 'title_de'))
        self.assertEquals(
            u'8.1. Contrats et accords',
            solr_data_for(self.leaf_repofolder, 'title_fr'))
        self.assertEquals(
            u'8.1. Vertr\xe4ge und Vereinbarungen',
            solr_data_for(self.leaf_repofolder, 'title_en'))
