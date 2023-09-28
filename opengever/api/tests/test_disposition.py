from datetime import datetime
from ftw.testbrowser import browsing
from ftw.testing import freeze
from opengever.disposition.delivery import DeliveryScheduler
from opengever.disposition.interfaces import IAppraisal
from opengever.disposition.interfaces import IDisposition
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
    def test_includes_translated_sip_delivery_status(self, browser):
        self.login(self.records_manager, browser)

        browser.open(self.disposition_with_sip, method='GET',
                     headers=self.api_headers)
        self.assertEqual([], browser.json['sip_delivery_status'])

        scheduler = DeliveryScheduler(self.disposition_with_sip)
        scheduler.schedule_delivery_with('filesystem')

        browser.open(self.disposition_with_sip, method='GET',
                     headers=self.api_headers)
        self.assertEqual(
            [{u'status': u'Scheduled for delivery', u'name': u'filesystem'}],
            browser.json['sip_delivery_status'])

    @browsing
    def test_includes_has_dossiers_with_pending_permissions_changes(self, browser):
        self.login(self.records_manager, browser)

        browser.open(self.disposition, method='GET', headers=self.api_headers)
        self.assertTrue(browser.json['has_dossiers_with_pending_permissions_changes'])

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

    @browsing
    def test_contains_responses_list_with_additional_dossiers_list(self, browser):
        self.login(self.records_manager, browser)
        browser.open(self.disposition_with_sip,
                     method='GET', headers=self.api_headers)

        self.assertEqual(
            [
                {u'creator': {u'token': u'ramon.flucht', u'title': u'Flucht Ramon'},
                 u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/disposition-2/@responses/1472663373000000',
                 u'created': u'2016-08-31T19:09:33',
                 u'modified': None,
                 u'modifier': None,
                 u'additional_data':{},
                 u'response_id': 1472663373000000,
                 u'response_type': u'added',
                 u'dossiers': [
                     {u'reference_number': u'Client1 1.1 / 13',
                      u'title': u'Dossier for SIP',
                      u'former_state': u'dossier-state-resolved',
                      u'repository_title': u'1.1. Vertr\xe4ge und Vereinbarungen',
                      u'intid': 1019033300,
                      u'appraisal': True}],
                 u'text': u'',
                 u'changes': []},
                {u'creator': {u'token': u'ramon.flucht', u'title': u'Flucht Ramon'},
                 u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/disposition-2/@responses/1472663493000000',
                 u'created': u'2016-08-31T19:11:33',
                 u'modified': None,
                 u'modifier': None,
                 u'additional_data':{},
                 u'response_id': 1472663493000000,
                 u'response_type': u'disposition-transition-dispose',
                 u'dossiers': [
                     {u'reference_number': u'Client1 1.1 / 13',
                      u'title': u'Dossier for SIP',
                      u'former_state': u'dossier-state-resolved',
                      u'repository_title': u'1.1. Vertr\xe4ge und Vereinbarungen',
                      u'intid': 1019033300,
                      u'appraisal': True}],
                 u'text': u'',
                 u'changes': []}],
            browser.json['responses'])


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


class TestDispositionPatch(IntegrationTestCase):

    @browsing
    def test_only_archivist_can_patch_transfer_number(self, browser):
        self.login(self.records_manager, browser)
        self.assertIsNone(IDisposition(self.disposition).transfer_number)
        self.assertEqual('Angebot 31.8.2016', self.disposition.title)

        self.login(self.records_manager, browser)
        data = {'transfer_number': '213',
                'title': 'Angebot neu'}

        browser.open(self.disposition.absolute_url(),
                     method='PATCH', headers=self.api_headers,
                     data=json.dumps(data))

        self.assertEqual(204, browser.status_code)
        self.assertIsNone(IDisposition(self.disposition).transfer_number)
        self.assertEqual('Angebot neu', self.disposition.title)

        self.login(self.archivist, browser)
        data = {'transfer_number': '213',
                'title': 'Angebot neu 2'}

        browser.open(self.disposition.absolute_url(),
                     method='PATCH', headers=self.api_headers,
                     data=json.dumps(data))

        self.assertEqual(204, browser.status_code)
        self.assertEqual('213', IDisposition(self.disposition).transfer_number)
        self.assertEqual('Angebot neu 2', self.disposition.title)


class TestTransferNumberPatch(IntegrationTestCase):

    @browsing
    def test_transfer_number_parameter_is_required(self, browser):
        self.login(self.archivist, browser)

        data = {}
        with browser.expect_http_error(code=400, reason='Bad Request'):
            browser.open(u'{}/@transfer-number'.format(self.disposition.absolute_url()),
                         method='PATCH', headers=self.api_headers,
                         data=json.dumps(data))

        self.assertEqual(
            browser.json,
            {u'additional_metadata': {},
             u'message': u'transfer_number_required',
             u'translated_message': u"Property 'transfer_number' is required",
             u'type': u'BadRequest'})

    @browsing
    def test_archivist_can_update_transfer_number_until_disposition_is_disposed(self, browser):
        self.login(self.archivist, browser)

        self.assertEqual('disposition-state-in-progress',
                         api.content.get_state(self.disposition))
        self.assertIsNone(IDisposition(self.disposition).transfer_number)

        data = {'transfer_number': '213'}
        browser.open(u'{}/@transfer-number'.format(self.disposition.absolute_url()),
                     method='PATCH', headers=self.api_headers,
                     data=json.dumps(data))

        self.assertEqual(204, browser.status_code)
        self.assertEqual('213', IDisposition(self.disposition).transfer_number)

        self.set_workflow_state('disposition-state-appraised', self.disposition)
        data = {'transfer_number': '214'}
        browser.open(u'{}/@transfer-number'.format(self.disposition.absolute_url()),
                     method='PATCH', headers=self.api_headers,
                     data=json.dumps(data))

        self.assertEqual(204, browser.status_code)
        self.assertEqual('214', IDisposition(self.disposition).transfer_number)

        self.set_workflow_state('disposition-state-disposed', self.disposition)
        data = {'transfer_number': '215'}
        with browser.expect_http_error(code=401, reason='Unauthorized'):
            browser.open(u'{}/@transfer-number'.format(self.disposition.absolute_url()),
                         method='PATCH', headers=self.api_headers,
                         data=json.dumps(data))

        self.set_workflow_state('disposition-state-archived', self.disposition)
        with browser.expect_http_error(code=401, reason='Unauthorized'):
            browser.open(u'{}/@transfer-number'.format(self.disposition.absolute_url()),
                         method='PATCH', headers=self.api_headers,
                         data=json.dumps(data))

        self.set_workflow_state('disposition-state-closed', self.disposition)
        with browser.expect_http_error(code=401, reason='Unauthorized'):
            browser.open(u'{}/@transfer-number'.format(self.disposition.absolute_url()),
                         method='PATCH', headers=self.api_headers,
                         data=json.dumps(data))

    @browsing
    def test_records_manager_cannot_update_transfer_number(self, browser):
        self.login(self.records_manager, browser)

        self.assertEqual('disposition-state-in-progress',
                         api.content.get_state(self.disposition))
        self.assertIsNone(IDisposition(self.disposition).transfer_number)

        data = {'transfer_number': '213'}
        with browser.expect_http_error(code=401, reason='Unauthorized'):
            browser.open(u'{}/@transfer-number'.format(self.disposition.absolute_url()),
                         method='PATCH', headers=self.api_headers,
                         data=json.dumps(data))
