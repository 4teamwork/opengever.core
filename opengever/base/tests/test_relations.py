from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.testing import FunctionalTestCase
from plone.app.testing import TEST_USER_ID
from zc.relation.interfaces import ICatalog
from zope.component import getUtility
from zope.intid.interfaces import IIntIds


class TestRelations(FunctionalTestCase):

    def setUp(self):
        super(TestRelations, self).setUp()
        self.dossier_a = create(Builder('dossier').titled(u'Dossier A'))

    @browsing
    def test_relation_gets_added_in_zc_catalog_when_dossier_is_added(self, browser):
        browser.login().open(self.portal,
                             view='++add++opengever.dossier.businesscasedossier')
        browser.fill({'Title': 'Dossier B with relations',
                      'Responsible': TEST_USER_ID,
                      'Related Dossier': [self.dossier_a]})
        browser.find('Save').click()

        rel_catalog = getUtility(ICatalog)
        intids = getUtility(IIntIds)
        relations = [rel for rel in rel_catalog.findRelations(
            {'to_id': intids.getId(self.dossier_a)})]

        self.assertEqual(1, len(relations))
        self.assertEqual(intids.getId(self.dossier_a), relations[0].to_id)
        self.assertEqual(intids.getId(browser.context), relations[0].from_id)

    @browsing
    def test_relation_catalog_gets_upated_when_dossier_is_updated(self, browser):
        self.dossier_b = create(Builder('dossier')
                                .having(responsible=TEST_USER_ID)
                                .titled(u'Dossier B'))
        browser.login().open(self.dossier_b, view='edit')
        browser.fill({'Title': 'Dossier B with relations',
                      'Responsible': TEST_USER_ID,
                      'Related Dossier': [self.dossier_a]})
        browser.find('Save').click()

        rel_catalog = getUtility(ICatalog)
        intids = getUtility(IIntIds)
        relations = [rel for rel in rel_catalog.findRelations(
            {'to_id': intids.getId(self.dossier_a)})]

        self.assertEqual(1, len(relations))
        self.assertEqual(intids.getId(self.dossier_a), relations[0].to_id)
        self.assertEqual(intids.getId(self.dossier_b), relations[0].from_id)
