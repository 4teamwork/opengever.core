from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages.statusmessages import info_messages
from opengever.dossier.behaviors.dossier import IDossier
from opengever.dossier.interfaces import IDossierType
from opengever.testing import IntegrationTestCase
from opengever.testing.helpers import MockDossierTypes
from plone import api


class TestDossierType(IntegrationTestCase):

    @browsing
    def test_field_is_not_available_in_add_form_when_no_dossier_types_active(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.leaf_repofolder)
        factoriesmenu.add('Business Case Dossier')

        self.assertIsNone(browser.forms['form'].find_field('Dossier type'))

        # By default the only type `businesscase` is hidden by registry entry
        api.portal.set_registry_record(
            name='hidden_dossier_types', interface=IDossierType, value=[])

        browser.open(self.leaf_repofolder)
        factoriesmenu.add('Business Case Dossier')
        self.assertIsNotNone(browser.forms['form'].find_field('Dossier type'))

    @browsing
    def test_field_is_not_available_in_edit_form_when_no_dossier_types_active(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.dossier, view='edit')
        self.assertIsNone(browser.forms['form'].find_field('Dossier type'))

        # By default the only type `businesscase` is hidden by registry entry
        api.portal.set_registry_record(
            name='hidden_dossier_types', interface=IDossierType, value=[])

        browser.open(self.dossier, view='edit')
        self.assertIsNotNone(browser.forms['form'].find_field('Dossier type'))

    @browsing
    def test_fill_dossier_type(self, browser):
        self.login(self.regular_user, browser=browser)

        # By default the only type `businesscase` is hidden by registry entry
        api.portal.set_registry_record(
            name='hidden_dossier_types', interface=IDossierType, value=[])
        # Reset cached hidden_terms in the vocabulary
        IDossier['dossier_type'].vocabulary.hidden_terms = []

        browser.open(self.dossier, view='edit')
        browser.fill({'Dossier type': 'businesscase'})
        browser.click_on('Save')

        self.assertEquals(['Changes saved'], info_messages())
        self.assertEquals('businesscase', IDossier(self.dossier).dossier_type)
