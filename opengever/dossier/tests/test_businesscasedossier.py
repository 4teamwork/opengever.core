from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages import statusmessages
from opengever.dossier.businesscase import IBusinessCaseDossier
from opengever.testing import IntegrationTestCase


class TestBusinessCaseDossierIntegration(IntegrationTestCase):

    @browsing
    def test_add_business_case_dossier(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.leaf_repofolder)
        factoriesmenu.add('Business Case Dossier')
        browser.fill({'Title': u'\xc4s Dossier'}).save()
        statusmessages.assert_no_error_messages()
        statusmessages.assert_message('Item created')

    def test_provides_interface(self):
        self.login(self.dossier_responsible)
        self.assertTrue(IBusinessCaseDossier.providedBy(self.dossier))

    def test_Title_accessor(self):
        self.login(self.dossier_responsible)
        self.assertEquals(
            'Vertr\xc3\xa4ge mit der kantonalen Finanzverwaltung',
            self.dossier.Title())
        self.assertEquals(str, type(self.dossier.Title()))

    def test_Description_accessor(self):
        self.login(self.dossier_responsible)
        self.assertEquals(
            'Alle aktuellen Vertr\xc3\xa4ge mit der kantonalen Finanzverwaltung'
            ' sind hier abzulegen.'
            ' Vertr\xc3\xa4ge vor 2016 geh\xc3\xb6ren ins Archiv.',
            self.dossier.Description())
        self.assertEquals(str, type(self.dossier.Description()))
