from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testing import freeze
from opengever.base.model import create_session
from opengever.dossier.behaviors.participation import IParticipationAware
from opengever.dossiertransfer.interfaces import IDossierTransferSettings
from opengever.dossiertransfer.model import TRANSFER_STATE_COMPLETED
from opengever.kub.testing import KuBIntegrationTestCase
from opengever.ogds.base.utils import get_current_admin_unit
from plone import api
from zExceptions import BadRequest
from zExceptions import Forbidden
import json
import pytz
import requests_mock
import transaction


FROZEN_NOW = datetime(2024, 2, 18, 15, 45, tzinfo=pytz.utc)


METADATA_RESP = {
    u'@id': u'http://nohost/plone/@dossier-transfers/1',
    u'@type': u'virtual.ogds.dossiertransfer',
    u'id': 1,
    u'title': u'Transfer Title',
    u'message': u'Transfer Message',
    u'created': u'2024-02-18T15:45:00+00:00',
    u'expires': u'2024-03-19T15:45:00+00:00',
    u'state': u'pending',
    u'source': {
        u'token': u'plone',
        u'title': u'Hauptmandant',
    },
    u'target': {
        u'token': u'recipient',
        u'title': u'Remote Recipient',
    },
    u'source_user': u'jurgen.konig',
    u'root': u'createresolvabledossier000000001',
    u'documents': [u'createresolvabledossier000000003'],
    u'all_documents': False,
    u'all_participations': False,
    u'content': {
        u'contacts': {
            u'person:9af7d7cc-b948-423f-979f-587158c6bc65': {
                u'type': u'person',
                u'text': u'Dupont Jean',
                u'title': u'',
            },
        },
        u'documents': [{
            "@id": "http://nohost/plone/ordnungssystem/fuehrung/gemeinderecht/dossier-20/dossier-21/document-44",
            "@type": "opengever.document.document",
            "UID": "a663689540a34538b6f408d4b41baee8",
            u'relative_path': u'ordnungssystem/fuehrung/gemeinderecht/dossier-20/dossier-21/document-44',
            u'title': u'Umbau B\xe4rengraben',
            'file': {
                u'content-type': u'plain/text',
                u'download': u'http://nohost/plone/ordnungssystem/fuehrung/gemeinderecht/dossier-20/dossier-21/document-44/@@download/file',  # noqa
                u'filename': u'Foobar.txt',
                u'size': 6,
            },
        }],
        u'dossiers': [{
            "@id": "http://nohost/plone/ordnungssystem/fuehrung/gemeinderecht/dossier-20",
            "@type": "opengever.dossier.businesscasedossier",
            "custom_properties": {
                "IDossier.default": {
                    "fallart": {
                        "title": "Zufall",
                        "token": "Zufall",
                    },
                    "fallnummer": 38493,
                    "location": "Bern",
                },
            },
            'relative_path': u'ordnungssystem/fuehrung/gemeinderecht/dossier-20',
            'title': u'A resolvable main dossier',
            'responsible': u'kathi.barfuss',
            u'participations': [
                [
                    u'person:9af7d7cc-b948-423f-979f-587158c6bc65',
                    [u'participation'],
                ],
            ],
        }, {
            "@id": "http://nohost/plone/ordnungssystem/fuehrung/gemeinderecht/dossier-20/dossier-21",
            "@type": "opengever.dossier.businesscasedossier",
            'relative_path': u'ordnungssystem/fuehrung/gemeinderecht/dossier-20/dossier-21',
            'title': u'Resolvable Subdossier',
            'responsible': u'nicole.kohler',
        }],
    },
}

KUB_LIST_RESP = {
    "count": 1,
    "next": None,
    "previous": None,
    "results": [
        {
            "created": "2024-04-19T17:34:22.542646+02:00",
            "firstName": "Anna",
            "fullName": "Nass Anna",
            "htmlUrl": "http://localhost:3100/people/20e024c9-db20-4ea1-999a-9deaa80413f4",
            "id": "20e024c9-db20-4ea1-999a-9deaa80413f4",
            "isActive": True,
            "modified": "2024-04-19T17:34:22.542653+02:00",
            "officialName": "Anna",
            "personTypeTitle": None,
            "primaryEmail": {
                "id": "66285529-85a5-4a28-9ba7-4c07f8f2b12b",
                "label": "Arbeit",
                "email": "anna.nass@frucht.ch",
                "isDefault": True,
                "thirdPartyId": None,
                "modified": "2024-04-19T17:34:22.554224+02:00",
                "created": "2024-04-19T17:34:22.554211+02:00"
            },
            "salutation": "Frau",
            "tags": [],
            "thirdPartyId": "person:ea18df93-0fe7-4615-a859-cde16cc4dd23",
            "title": "",
            "url": "http://localhost:3100/api/v1/people/20e024c9-db20-4ea1-999a-9deaa80413f4",
            "username": "lpfsdlwp"
        }
    ]
}

KUB_LIST_EMPTY_RESP = {
    "count": 0,
    "next": None,
    "previous": None,
    "results": []
}


class TestPerformDossierTransfer(KuBIntegrationTestCase):

    features = ('dossier-transfers',)

    @browsing
    def test_perform_dossier_transfer_raises_bad_request_if_disabled(self, browser):
        api.portal.set_registry_record(
            'is_feature_enabled', False, interface=IDossierTransferSettings)
        self.login(self.regular_user, browser)

        browser.exception_bubbling = True
        with self.assertRaises(BadRequest):
            browser.open(
                self.leaf_repofolder, view='@perform-dossier-transfer',
                method='POST',
                headers=self.api_headers,
            )

    @browsing
    def test_regular_user_is_not_allowed_to_perform_dossier_transfer(self, browser):
        self.login(self.regular_user, browser)

        browser.exception_bubbling = True
        with self.assertRaises(Forbidden):
            browser.open(
                self.leaf_repofolder, view='@perform-dossier-transfer',
                method='POST',
                headers=self.api_headers,
            )

    @browsing
    def test_raises_bad_request_if_invalid_data(self, browser):
        self.login(self.secretariat_user, browser)

        browser.exception_bubbling = True
        with self.assertRaises(BadRequest):
            browser.open(
                self.leaf_repofolder, view='@perform-dossier-transfer',
                method='POST',
                headers=self.api_headers,
                data='{}',
            )

    @browsing
    def test_raises_bad_request_for_unknown_transfer_id(self, browser):
        self.login(self.secretariat_user, browser)

        browser.exception_bubbling = True
        with self.assertRaises(BadRequest) as exc:
            browser.open(
                self.leaf_repofolder, view='@perform-dossier-transfer',
                method='POST',
                headers=self.api_headers,
                data='{"transfer_id": 4444}',
            )
            self.assertEqual(str(exc), 'Unknown Transfer')

    @requests_mock.Mocker()
    @browsing
    def test_creates_dossiers_and_documents_with_existing_contact(self, mocker, browser):
        self.login(self.secretariat_user, browser)

        with freeze(FROZEN_NOW):
            transfer = create(Builder('dossier_transfer')
                              .with_target(get_current_admin_unit()))
            session = create_session()
            session.add(transfer)
            session.flush()

        url = '{}/@dossier-transfers/{}?full_content=1'.format(
            transfer.source.site_url, transfer.id)
        mocker.get(url, json=METADATA_RESP)

        url = 'http://example.com/@dossier-transfers/1/blob/a663689540a34538b6f408d4b41baee8'
        mocker.get(url, content='foobar')

        url = '{}people?third_party_id={}'.format(
            self.client.kub_api_url, 'person:9af7d7cc-b948-423f-979f-587158c6bc65')
        mocker.get(url, json=KUB_LIST_RESP)

        self.mock_labels(mocker)

        # Disable ftw.testing.TransactionInterceptor for transaction.begin()
        # as this is used in perform-dossier-transfer for syncing the database
        # before writing to it. With ftw.testing.TransactionInterceptor this
        # would rollback the transaction.
        tx_begin = transaction.begin
        transaction.begin = lambda: True

        resp = browser.open(
            self.leaf_repofolder, view='@perform-dossier-transfer',
            method='POST',
            headers=self.api_headers,
            data=json.dumps({"transfer_id": transfer.id}),
        )

        # Reenable begin() of ftw.testing.TransactionInterceptor
        transaction.begin = tx_begin

        # Verify that the expected API calls have been made
        expected_calls = [
            ('GET', 'http://example.com/@dossier-transfers/1?full_content=1'),
            ('GET', 'http://example.com/@dossier-transfers/1/blob/a663689540a34538b6f408d4b41baee8'),
            ('GET', 'http://localhost:8000/api/v2/people?third_party_id=person%3A9af7d7cc-b948-423f-979f-587158c6bc65'),
            ('GET', 'http://localhost:8000/api/v2/labels'),
        ]
        actual_calls = [(m.method, m.url) for m in mocker.request_history]
        self.assertEqual(actual_calls, expected_calls)

        # Verify key propertes of the response
        self.assertDictContainsSubset(
            {
                u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-21',
                u'@type': u'opengever.dossier.businesscasedossier',
                u'custom_properties': {
                    u'IDossier.default': {
                        u'location': 'Bern',
                    },
                },
                u'responsible': {
                    u'title': u'K\xf6nig J\xfcrgen (jurgen.konig)',
                    u'token': u'jurgen.konig',
                },
            },
            resp.json,
        )

        # Verify that participations are correctly set
        dossier = self.leaf_repofolder[resp.json['id']]
        self.assertEqual(
            [(p.contact, p.roles) for p in IParticipationAware(dossier).get_participations()],
            [('person:20e024c9-db20-4ea1-999a-9deaa80413f4', [u'participation'])])

        # Verify that transfer state is set to completed
        self.assertEqual(transfer.state, TRANSFER_STATE_COMPLETED)

    @requests_mock.Mocker()
    @browsing
    def test_creates_dossiers_and_documents_with_new_contacts(self, mocker, browser):
        self.login(self.secretariat_user, browser)

        with freeze(FROZEN_NOW):
            transfer = create(Builder('dossier_transfer')
                              .with_target(get_current_admin_unit()))
            session = create_session()
            session.add(transfer)
            session.flush()

        url = '{}/@dossier-transfers/{}?full_content=1'.format(
            transfer.source.site_url, transfer.id)
        mocker.get(url, json=METADATA_RESP)

        url = 'http://example.com/@dossier-transfers/1/blob/a663689540a34538b6f408d4b41baee8'
        mocker.get(url, content='foobar')

        url = '{}people?third_party_id={}'.format(
            self.client.kub_api_url, 'person:9af7d7cc-b948-423f-979f-587158c6bc65')
        mocker.get(url, json=KUB_LIST_EMPTY_RESP)

        url = '{}people'.format(self.client.kub_api_url)
        mocker.post(url, json={'typeId': 'person:9af7d7cc-b948-423f-979f-587158c6bc65'})

        self.mock_labels(mocker)

        # Disable ftw.testing.TransactionInterceptor for transaction.begin()
        # as this is used in perform-dossier-transfer for syncing the database
        # before writing to it. With ftw.testing.TransactionInterceptor this
        # would rollback the transaction.
        tx_begin = transaction.begin
        transaction.begin = lambda: True

        resp = browser.open(
            self.leaf_repofolder, view='@perform-dossier-transfer',
            method='POST',
            headers=self.api_headers,
            data=json.dumps({"transfer_id": transfer.id}),
        )

        # Reenable begin() of ftw.testing.TransactionInterceptor
        transaction.begin = tx_begin

        # Verify that the expected API calls have been made
        expected_calls = [
            ('GET', 'http://example.com/@dossier-transfers/1?full_content=1'),
            ('GET', 'http://example.com/@dossier-transfers/1/blob/a663689540a34538b6f408d4b41baee8'),
            ('GET', 'http://localhost:8000/api/v2/people?third_party_id=person%3A9af7d7cc-b948-423f-979f-587158c6bc65'),
            ('POST', 'http://localhost:8000/api/v2/people'),
            ('GET', 'http://localhost:8000/api/v2/labels'),
        ]
        actual_calls = [(m.method, m.url) for m in mocker.request_history]
        self.assertEqual(actual_calls, expected_calls)

        # Verify key propertes of the response
        self.assertDictContainsSubset(
            {
                u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-21',
                u'@type': u'opengever.dossier.businesscasedossier',
                u'responsible': {
                    u'title': u'K\xf6nig J\xfcrgen (jurgen.konig)',
                    u'token': u'jurgen.konig',
                },
            },
            resp.json,
        )

        # Verify that participations are set correctly
        dossier = self.leaf_repofolder[resp.json['id']]
        self.assertEqual(
            [(p.contact, p.roles) for p in IParticipationAware(dossier).get_participations()],
            [('person:9af7d7cc-b948-423f-979f-587158c6bc65', [u'participation'])])

        # Verify that transfer state is set to completed
        self.assertEqual(transfer.state, TRANSFER_STATE_COMPLETED)
