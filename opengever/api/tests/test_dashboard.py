from ftw.testbrowser import browsing
from opengever.base.interfaces import DEFAULT_DASHBOARD_CARDS
from opengever.base.interfaces import IGeverUI
from opengever.testing import IntegrationTestCase
from plone import api
import json


class TestDashboardSettings(IntegrationTestCase):

    @browsing
    def test_returns_default_dashboard_cards(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.portal.absolute_url() + '/@dashboard-settings',
                     method='GET', headers=self.api_headers)

        self.assertEquals([card.get('id') for card in DEFAULT_DASHBOARD_CARDS],
                          [card.get('id') for card in browser.json['cards']])

    @browsing
    def test_returns_customized_dashboard_card_list(self, browser):
        self.login(self.regular_user, browser=browser)

        custom_dashboard_list = [
            {'componentName': 'NewestGeverNotificationsCard'},
            {'componentName': 'RecentlyTouchedItemsCard'},
            {'componentName': 'DossiersCard',
             'title': 'Falldossiers',
             'filters': {
                 'dossierType': 'Falldossier'}}
        ]

        api.portal.set_registry_record(
            interface=IGeverUI, name='custom_dashboard_cards',
            value=json.dumps(custom_dashboard_list).decode('utf-8'))

        browser.open(self.portal.absolute_url() + '/@dashboard-settings',
                     method='GET', headers=self.api_headers)

        self.assertEquals(custom_dashboard_list, browser.json['cards'])

    @browsing
    def test_returns_localized_titles(self, browser):
        self.login(self.regular_user, browser=browser)

        custom_dashboard_list = [
            {'title': 'Falldossier'},
            {'title_de': 'DE project dossier', 'title_en': 'EN project dossier'}
        ]

        api.portal.set_registry_record(
            interface=IGeverUI, name='custom_dashboard_cards',
            value=json.dumps(custom_dashboard_list).decode('utf-8'))

        browser.open(self.portal.absolute_url() + '/@dashboard-settings',
                     method='GET', headers=self.api_headers)

        self.assertEquals(['Falldossier', 'EN project dossier'], [card.get('title') for card in browser.json['cards']])

        german_headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Accept-Language': 'de-ch'}

        browser.open(self.portal.absolute_url() + '/@dashboard-settings',
                     method='GET', headers=german_headers)

        self.assertEquals(['Falldossier', 'DE project dossier'], [card.get('title') for card in browser.json['cards']])
