from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from opengever.dossier.interfaces import IDossierContainerTypes
from opengever.testing import FunctionalTestCase
from plone import api
from plone.app.testing import TEST_USER_ID
import transaction


class TestConstrainTypeDecider(FunctionalTestCase):

    def setUp(self):
        super(TestConstrainTypeDecider, self).setUp()
        self.dossier = self.create_test_dossier()

    def create_test_dossier(self):
        return create(Builder('dossier')
                      .titled(u'Test Dossier')
                      .having(responsible=TEST_USER_ID))

    @browsing
    def test_subdossier_addable_by_default(self, browser):
        browser.login().open(self.dossier)
        self.assertIn('Subdossier', factoriesmenu.addable_types())

    @browsing
    def test_subdossier_not_addable_if_nesting_level_restricted(self, browser):
        api.portal.set_registry_record(
            'maximum_dossier_depth', 0, interface=IDossierContainerTypes)
        transaction.commit()

        browser.login().open(self.dossier)
        self.assertEquals([
            'Document',
            'document_with_template',
            'Task',
            'Add task from template',
            'Participant'],
            factoriesmenu.addable_types())
