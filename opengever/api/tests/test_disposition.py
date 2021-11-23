from datetime import datetime
from ftw.testbrowser import browsing
from ftw.testing import freeze
from opengever.testing import IntegrationTestCase
from plone import api
import json


class TestDispositionPost(IntegrationTestCase):

    @browsing
    def test_check_for_already_offered_dossiers(self, browser):
        self.login(self.records_manager, browser)

        data = {
            "@type": "opengever.disposition.disposition",
            "title": "Angebot XY",
            "dossiers": [self.offered_dossier_for_sip.absolute_url()]}

        with browser.expect_http_error(code=400, reason='Bad Request'):
            browser.open(self.repository_root, data=json.dumps(data),
                         method='POST', headers=self.api_headers)

        self.assertEqual(
            {u'type': u'BadRequest',
             u'additional_metadata': {},
             u'translated_message': u'The dossier Dossier for SIP is already offered in a different disposition.',
             u'message': u'error_offered_in_a_different_disposition'},
            browser.json)

    @browsing
    def test_check_for_retention_period(self, browser):
        self.login(self.records_manager, browser)

        data = {
            "@type": "opengever.disposition.disposition",
            "title": "Angebot XY",
            "dossiers": [self.closed_meeting_dossier.absolute_url()]}

        with freeze(datetime(2001, 1, 1)):
            with browser.expect_http_error(code=400, reason='Bad Request'):
                browser.open(self.repository_root, data=json.dumps(data),
                             method='POST', headers=self.api_headers)

        self.assertEqual(
            {u'type': u'BadRequest',
             u'additional_metadata': {},
             u'translated_message': u'The dossier Sitzungsdossier 7/2017 is still active.',
             u'message': u'error_dossier_is_active'},
            browser.json)

    @browsing
    def test_check_open_dossiers(self, browser):
        self.login(self.records_manager, browser)

        data = {
            "@type": "opengever.disposition.disposition",
            "title": "Angebot XY",
            "dossiers": [self.dossier.absolute_url()]}

        with freeze(datetime(2001, 1, 1)):
            with browser.expect_http_error(code=400, reason='Bad Request'):
                browser.open(self.repository_root, data=json.dumps(data),
                             method='POST', headers=self.api_headers)

        self.assertEqual(
            {u'type': u'BadRequest',
             u'additional_metadata': {},
             u'translated_message': u'The dossier Vertr\xe4ge mit der kantonalen Finanzverwaltung is still active.',
             u'message': u'error_dossier_is_active'},
            browser.json)

    @browsing
    def test_successfull_post(self, browser):
        self.login(self.records_manager, browser)

        data = {
            "@type": "opengever.disposition.disposition",
            "title": "Angebot XY",
            "dossiers": [self.expired_dossier.absolute_url()]}

        with self.observe_children(self.repository_root) as children:
            browser.open(self.repository_root, data=json.dumps(data),
                         method='POST', headers=self.api_headers)

        disposition, = children['added']

        self.assertEqual('Angebot XY', disposition.title)
        self.assertEqual('dossier-state-offered',
                         api.content.get_state(self.expired_dossier))


class TestDispositionSeriaization(IntegrationTestCase):

    @browsing
    def test_includes_sip_filename(self, browser):
        self.login(self.records_manager, browser)

        with freeze(datetime(2001, 1, 1)):
            browser.open(self.disposition,
                         method='GET', headers=self.api_headers)

        self.assertEqual(u'Angebot 31.8.2016', browser.json['title'])
        self.assertEqual(None, browser.json['transfer_number'])
        self.assertEqual(u'SIP_20010101_PLONE.zip', browser.json['sip_filename'])
