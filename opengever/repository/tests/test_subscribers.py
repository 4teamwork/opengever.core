from Acquisition import aq_inner
from Acquisition import aq_parent
from ftw.testbrowser import browsing
from opengever.testing import obj2brain
from opengever.testing import solr_data_for
from opengever.testing import SolrIntegrationTestCase


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
