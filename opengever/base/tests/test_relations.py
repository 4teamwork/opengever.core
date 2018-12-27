from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
from zc.relation.interfaces import ICatalog
from zope.component import getUtility
from zope.intid.interfaces import IIntIds


class TestRelations(IntegrationTestCase):

    @browsing
    def test_relation_gets_added_in_zc_catalog_when_dossier_is_added(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.leaf_repofolder,
                     view='++add++opengever.dossier.businesscasedossier')
        browser.fill({'Title': 'Dossier B with relations',
                      'Related Dossier': [self.dossier]})
        browser.find('Save').click()

        rel_catalog = getUtility(ICatalog)
        intids = getUtility(IIntIds)
        relations = [rel for rel in rel_catalog.findRelations(
            {'to_id': intids.getId(self.dossier)})]

        self.assertEqual(2, len(relations))
        self.assertIn(intids.getId(self.dossier),
                      [rel.to_id for rel in relations])
        self.assertIn(intids.getId(browser.context),
                      [rel.from_id for rel in relations])

    @browsing
    def test_relation_catalog_gets_upated_when_dossier_is_updated(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.empty_dossier, view='edit')
        browser.fill({'Title': 'Dossier B with relations',
                      'Related Dossier': [self.dossier]})
        browser.find('Save').click()

        rel_catalog = getUtility(ICatalog)
        intids = getUtility(IIntIds)
        relations = [rel for rel in rel_catalog.findRelations(
            {'to_id': intids.getId(self.dossier)})]

        self.assertEqual(2, len(relations))
        self.assertIn(intids.getId(self.dossier),
                      [rel.to_id for rel in relations])
        self.assertIn(intids.getId(self.empty_dossier),
                      [rel.from_id for rel in relations])
