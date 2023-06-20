from ftw.testbrowser import browsing
from opengever.dossier.interfaces import IDossierParticipants
from opengever.testing import IntegrationTestCase
from plone import api


class TestSystemInformation(IntegrationTestCase):

    @browsing
    def test_provided_information(self, browser):
        self.login(self.manager, browser)
        api.portal.set_registry_record('primary_participation_roles', ['regard'], IDossierParticipants)

        self.login(self.regular_user, browser)
        browser.open(self.portal.absolute_url() + '/@system-information', headers=self.api_headers)

        self.assertEqual(browser.status_code, 200)
        self.assertEqual({}, browser.json)
