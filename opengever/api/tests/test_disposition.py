from datetime import datetime
from ftw.testbrowser import browsing
from ftw.testing import freeze
from opengever.disposition.interfaces import IAppraisal
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
             u'translated_message': u'The dossier Dossier for SIP is already in another offer.',
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


class TestDispositionSerialization(IntegrationTestCase):

    @browsing
    def test_includes_sip_filename(self, browser):
        self.login(self.records_manager, browser)

        with freeze(datetime(2001, 1, 1)):
            browser.open(self.disposition,
                         method='GET', headers=self.api_headers)

        self.assertEqual(u'Angebot 31.8.2016', browser.json['title'])
        self.assertEqual(None, browser.json['transfer_number'])
        self.assertEqual(u'SIP_20010101_PLONE.zip', browser.json['sip_filename'])

    @browsing
    def test_provides_dossier_details(self, browser):
        self.login(self.records_manager, browser)
        browser.open(self.disposition, method='GET', headers=self.api_headers)

        self.assertItemsEqual(['active_dossiers', 'inactive_dossiers'],
                              browser.json['dossier_details'].keys())

        self.assertEqual(
            [
                {u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen',
                 u'@type': u'opengever.repository.repositoryfolder',
                 u'archival_value': {u'title': u'not assessed',
                                     u'token': u'unchecked'},
                 u'description': u'',
                 u'is_leafnode': True,
                 u'review_state': u'repositoryfolder-state-active',
                 u'title': u'1.1. Vertr\xe4ge und Vereinbarungen',
                 u'dossiers': [{u'appraisal': True,
                                u'archival_value': {
                                    u'title': u'archival worthy',
                                    u'token': u'archival worthy'},
                                u'archival_value_annotation': None,
                                u'end': u'2000-01-31',
                                u'former_state': u'dossier-state-resolved',
                                u'intid': 1019013300,
                                u'public_trial': {
                                    u'title': u'not assessed',
                                    u'token': u'unchecked'},
                                u'reference_number': u'Client1 1.1 / 12',
                                u'start': u'2000-01-01',
                                u'title': u'Hannah Baufrau',
                                u'uid': u'createoffereddossiers00000000001',
                                u'url': self.offered_dossier_to_archive.absolute_url()}]
                }],
            browser.json['dossier_details']['active_dossiers'])

        self.assertEqual(
            [
                {u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen',
                 u'@type': u'opengever.repository.repositoryfolder',
                 u'archival_value': {u'title': u'not assessed',
                                     u'token': u'unchecked'},
                 u'description': u'',
                 u'is_leafnode': True,
                 u'review_state': u'repositoryfolder-state-active',
                 u'title': u'1.1. Vertr\xe4ge und Vereinbarungen',
                 u'dossiers': [{u'appraisal': False,
                                u'archival_value': {u'title': u'not archival worthy',
                                                    u'token': u'not archival worthy'},
                                u'archival_value_annotation': None,
                                u'end': u'2000-01-15',
                                u'former_state': u'dossier-state-inactive',
                                u'intid': 1019053300,
                                u'public_trial': {u'title': u'not assessed',
                                                  u'token': u'unchecked'},
                                u'reference_number': u'Client1 1.1 / 14',
                                u'start': u'2000-01-01',
                                u'title': u'Hans Baumann',
                                u'uid': u'createoffereddossiers00000000003',
                                u'url': self.offered_dossier_to_destroy.absolute_url()}],
                }],
            browser.json['dossier_details']['inactive_dossiers'])

    @browsing
    def test_shows_limited_information_for_removed_content(self, browser):
        # close disposition (remove dossiers)
        self.login(self.archivist, browser)
        api.content.transition(self.disposition_with_sip,
                               'disposition-transition-archive')
        self.login(self.records_manager, browser)
        api.content.transition(self.disposition_with_sip,
                               'disposition-transition-close')

        browser.open(self.disposition_with_sip,
                     method='GET', headers=self.api_headers)

        self.assertEqual(
            {
                u'active_dossiers': [
                    {
                        u'title': u'1.1. Vertr\xe4ge und Vereinbarungen',
                        u'dossiers': [
                            {u'appraisal': True,
                             u'archival_value': None,
                             u'archival_value_annotation': None,
                             u'end': None,
                             u'former_state': u'dossier-state-resolved',
                             u'intid': 1019033300,
                             u'public_trial': None,
                             u'reference_number': u'Client1 1.1 / 13',
                             u'start': None,
                             u'title': u'Dossier for SIP',
                             u'uid': None,
                             u'url': None}],
                    }
                ],
                u'inactive_dossiers': []
            },
            browser.json['dossier_details'])


class TestAppraisalUpdate(IntegrationTestCase):

    @browsing
    def test_update_appraisal_for_one_dossier(self, browser):
        self.login(self.records_manager, browser)

        appraisal = IAppraisal(self.disposition)
        self.assertTrue(appraisal.get(self.offered_dossier_to_archive))
        data = {
            self.offered_dossier_to_archive.UID(): False}

        browser.open(u'{}/@appraisal'.format(self.disposition.absolute_url()),
                     method='PATCH', headers=self.api_headers,
                     data=json.dumps(data))

        self.assertFalse(appraisal.get(self.offered_dossier_to_archive))

    @browsing
    def test_update_appraisal_for_multiple_dossier(self, browser):
        self.login(self.records_manager, browser)

        appraisal = IAppraisal(self.disposition)
        self.assertTrue(appraisal.get(self.offered_dossier_to_archive))
        self.assertFalse(appraisal.get(self.offered_dossier_to_destroy))

        data = {
            self.offered_dossier_to_archive.UID(): False,
            self.offered_dossier_to_destroy.UID(): True}

        browser.open(u'{}/@appraisal'.format(self.disposition.absolute_url()),
                     method='PATCH', headers=self.api_headers,
                     data=json.dumps(data))

        self.assertFalse(appraisal.get(self.offered_dossier_to_archive))
        self.assertTrue(appraisal.get(self.offered_dossier_to_destroy))

    @browsing
    def test_notice_the_prefer_header_and_returns_disposition_serialization(self, browser):
        self.login(self.records_manager, browser)

        data = {self.offered_dossier_to_archive.UID(): False}
        headers = self.api_headers.copy()
        headers.update({'Prefer': 'return=representation'})
        browser.open(u'{}/@appraisal'.format(self.disposition.absolute_url()),
                     method='PATCH', headers=headers, data=json.dumps(data))

        self.assertEqual(self.disposition.id, browser.json['id'])
        self.assertEqual(self.disposition.title, browser.json['title'])

        self.assertEqual(
            [{
                u'appraisal': False,
                u'archival_value': {u'title': u'archival worthy',
                                    u'token': u'archival worthy'},
                u'archival_value_annotation': None,
                u'end': u'2000-01-31',
                u'former_state': u'dossier-state-resolved',
                u'intid': 1019013300,
                u'public_trial': {u'title': u'not assessed', u'token': u'unchecked'},
                u'reference_number': u'Client1 1.1 / 12',
                u'start': u'2000-01-01',
                u'title': u'Hannah Baufrau',
                u'uid': u'createoffereddossiers00000000001',
                u'url': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-18'}],
            browser.json['dossier_details']['active_dossiers'][0]['dossiers'])

    @browsing
    def test_raises_if_uid_is_not_part_of_disposition(self, browser):
        self.login(self.records_manager, browser)

        data = {self.dossier.UID(): False}

        with browser.expect_http_error(code=400, reason='Bad Request'):
            browser.open(u'{}/@appraisal'.format(self.disposition.absolute_url()),
                         method='PATCH', headers=self.api_headers,
                         data=json.dumps(data))

        self.assertEquals(
            {'additional_metadata': {},
             'message': 'msg_invalid_uid',
             'translated_message': 'Dossier with the UID '
             'createtreatydossiers000000000001 is not part of the disposition',
             'type': 'BadRequest'},
            browser.json)