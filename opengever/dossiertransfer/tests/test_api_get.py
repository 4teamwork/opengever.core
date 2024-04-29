from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testing import freeze
from opengever.base.model import create_session
from opengever.base.security import elevated_privileges
from opengever.dossier.behaviors.participation import IParticipationAware
from opengever.kub.testing import KuBIntegrationTestCase
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.testing import IntegrationTestCase
from plone import api
import pytz
import requests_mock


FROZEN_NOW = datetime(2024, 2, 18, 15, 45, tzinfo=pytz.utc)

JEAN_PERSON_ID = 'person:9af7d7cc-b948-423f-979f-587158c6bc65'
JEAN_MEMBERSHIP_ID = 'membership:8345fcfe-2d67-4b75-af46-c25b2f387448'
JULIE_PERSON_ID = "person:0e623708-2d0d-436a-82c6-c1a9c27b65dc"


class TestDossierTransfersGet(IntegrationTestCase):

    features = ('dossier-transfers', )

    def get_items(self, browser):
        return [(tf['id'], tf['title']) for tf in browser.json['items']]

    @browsing
    def test_get_dossier_transfer(self, browser):
        self.login(self.secretariat_user, browser=browser)

        with freeze(datetime(2024, 2, 18, 15, 45, tzinfo=pytz.utc)):
            transfer = create(Builder('dossier_transfer'))
            session = create_session()
            session.add(transfer)
            session.flush()

        transfer.all_participations = False
        transfer.participations = ['meeting_user']

        browser.open(self.portal, view='@dossier-transfers/%s' % transfer.id,
                     method='GET', headers=self.api_headers)

        self.assertEqual(200, browser.status_code)

        expected = {
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
            u'participations': [u'meeting_user'],
            u'all_documents': False,
            u'all_participations': False,
        }
        self.assertEqual(expected, browser.json)

    @browsing
    def test_get_dossier_transfer_listing(self, browser):
        self.login(self.secretariat_user, browser=browser)

        with freeze(datetime(2024, 2, 18, 15, 45, tzinfo=pytz.utc)):
            transfer1 = create(Builder('dossier_transfer'))
            transfer2 = create(Builder('dossier_transfer')
                               .having(
                                   title='Transfer 2',
                                   all_participations=False,
                                   participations=['meeting_user']))

            session = create_session()
            session.add(transfer1)
            session.add(transfer2)
            session.flush()

        browser.open(self.portal, view='@dossier-transfers/',
                     method='GET', headers=self.api_headers)

        self.assertEqual(200, browser.status_code)

        expected = {
            u'@id': u'http://nohost/plone/@dossier-transfers',
            u'items': [
                {
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
                    u'participations': None,
                    u'all_documents': False,
                    u'all_participations': True,
                },
                {
                    u'@id': u'http://nohost/plone/@dossier-transfers/2',
                    u'@type': u'virtual.ogds.dossiertransfer',
                    u'id': 2,
                    u'title': u'Transfer 2',
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
                    u'participations': [u'meeting_user'],
                    u'all_documents': False,
                    u'all_participations': False,
                }
            ]
        }
        self.assertEqual(expected, browser.json)

    @browsing
    def test_transfer_listing_ordering(self, browser):
        self.login(self.secretariat_user, browser=browser)

        session = create_session()
        params = [
            ((1995, 1, 1, 12, 30), 'completed', 'Completed old transfer'),
            ((1996, 1, 1, 12, 30), 'pending', 'Pending old transfer'),
            ((1970, 1, 1, 12, 30), 'completed', 'Completed ancient transfer'),
            ((1971, 1, 1, 12, 30), 'pending', 'Pending ancient transfer'),
            ((2023, 1, 1, 12, 30), 'completed', 'Completed recent transfer'),
            ((2024, 1, 1, 12, 30), 'pending', 'Pending recent transfer'),
        ]
        for (created, state, title) in params:
            with freeze(datetime(*created, tzinfo=pytz.utc)):
                transfer = create(Builder('dossier_transfer')
                                  .having(
                                      state=state,
                                      title=title))
                session.add(transfer)
                session.flush()

        browser.open(self.portal, view='@dossier-transfers/',
                     method='GET', headers=self.api_headers)

        self.assertEqual(200, browser.status_code)

        expected = [
            (6, u'Pending recent transfer'),
            (2, u'Pending old transfer'),
            (4, u'Pending ancient transfer'),
            (5, u'Completed recent transfer'),
            (1, u'Completed old transfer'),
            (3, u'Completed ancient transfer'),
        ]
        self.assertEqual(expected, self.get_items(browser))

    @browsing
    def test_transfer_listing_direction_filter(self, browser):
        self.login(self.secretariat_user, browser=browser)
        other_au = create(Builder('admin_unit')
                          .id('other')
                          .having(title='Other AU'))

        session = create_session()
        with freeze(datetime(2024, 2, 18, 15, 45, tzinfo=pytz.utc)):
            outgoing_transfer = create(Builder('dossier_transfer')
                                       .having(title='Outgoing'))
            incoming_transfer = create(Builder('dossier_transfer')
                                       .with_source(other_au)
                                       .with_target(get_current_admin_unit())
                                       .having(title='Incoming'))
            session.add(outgoing_transfer)
            session.add(incoming_transfer)
            session.flush()

        # No direction filter
        browser.open(self.portal, view='@dossier-transfers/',
                     method='GET', headers=self.api_headers)
        expected = [
            (1, u'Outgoing'),
            (2, u'Incoming'),
        ]
        self.assertEqual(expected, self.get_items(browser))

        # Incoming
        browser.open(self.portal, view='@dossier-transfers?direction=incoming',
                     method='GET', headers=self.api_headers)
        expected = [
            (2, u'Incoming'),
        ]
        self.assertEqual(expected, self.get_items(browser))

        # Outgoing
        browser.open(self.portal, view='@dossier-transfers?direction=outgoing',
                     method='GET', headers=self.api_headers)
        expected = [
            (1, u'Outgoing'),
        ]
        self.assertEqual(expected, self.get_items(browser))

    @browsing
    def test_transfer_listing_state_filter(self, browser):
        self.login(self.secretariat_user, browser=browser)

        session = create_session()
        with freeze(datetime(2024, 2, 18, 15, 45, tzinfo=pytz.utc)):
            pending_transfer = create(Builder('dossier_transfer')
                                      .having(
                                          state='pending',
                                          title='Pending'))
            completed_transfer = create(Builder('dossier_transfer')
                                        .having(
                                            state='completed',
                                            title='Completed'))
            unknown_transfer = create(Builder('dossier_transfer')
                                      .having(
                                          state='unknown',
                                          title='Unknown State'))
            session.add(pending_transfer)
            session.add(completed_transfer)
            session.add(unknown_transfer)
            session.flush()

        # No state filter
        browser.open(self.portal, view='@dossier-transfers/',
                     method='GET', headers=self.api_headers)
        expected = [
            (1, u'Pending'),
            (2, u'Completed'),
            (3, u'Unknown State'),
        ]
        self.assertEqual(expected, self.get_items(browser))

        # Pending only
        browser.open(self.portal, view='@dossier-transfers?states:list=pending',
                     method='GET', headers=self.api_headers)
        expected = [
            (1, u'Pending'),
        ]
        self.assertEqual(expected, self.get_items(browser))

        # Completed only
        browser.open(self.portal, view='@dossier-transfers?states:list=completed',
                     method='GET', headers=self.api_headers)
        expected = [
            (2, u'Completed'),
        ]
        self.assertEqual(expected, self.get_items(browser))

        # Pending and completed
        qs = 'states:list=pending&states:list=completed'
        browser.open(self.portal, view='@dossier-transfers?%s' % qs,
                     method='GET', headers=self.api_headers)
        expected = [
            (1, u'Pending'),
            (2, u'Completed'),
        ]
        self.assertEqual(expected, self.get_items(browser))


class TestDossierTransfersGetFullContent(KuBIntegrationTestCase):

    features = ('dossier-transfers', )

    def create_transfer(self, **kwargs):
        default_args = {
            'all_documents': True,
            'all_participations': True,
        }
        default_args.update(kwargs)

        with freeze(FROZEN_NOW):
            transfer = create(
                Builder('dossier_transfer')
                .having(**default_args)
            )
            session = create_session()
            session.add(transfer)
            session.flush()
        return transfer

    def summarize_items(self, items):
        def summarize_item(item):
            keep = ('title', 'relative_path', 'text', 'type')
            return {key: value for key, value in item.items() if key in keep}

        if isinstance(items, list):
            summarized = [summarize_item(item) for item in items]
        elif isinstance(items, dict):
            summarized = {key: summarize_item(value) for key, value in items.items()}

        return summarized

    def summarize_content(self, content):
        summary = {}
        for key, value in content.items():
            summary[key] = self.summarize_items(value)

        return summary

    def add_participation(self, mocker, dossier, kub_id, roles):
        self.mock_get_by_id(mocker, kub_id)
        self.mock_labels(mocker)
        handler = IParticipationAware(dossier)
        handler.add_participation(kub_id, roles)

    @requests_mock.Mocker()
    @browsing
    def test_content_structure(self, mocker, browser):
        transfer = self.create_transfer()

        self.login(self.manager)
        self.add_participation(
            mocker,
            self.resolvable_dossier,
            JEAN_PERSON_ID,
            ['regard', 'participation', 'final-drawing'],
        )
        self.logout()

        headers = self.api_headers.copy()
        headers.update({'X-GEVER-Dossier-Transfer-Token': transfer.token})

        with freeze(FROZEN_NOW):
            browser.open(
                self.portal,
                view='@dossier-transfers/%s/?full_content=1' % transfer.id,
                method='GET', headers=headers)

        self.assertEqual(200, browser.status_code)

        expected_structure = {
            u'contacts': {
                u'person:9af7d7cc-b948-423f-979f-587158c6bc65': {
                    u'type': u'person',
                    u'text': u'Dupont Jean',
                    u'title': u'',
                },
            },
            u'documents': [{
                u'relative_path': u'ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-8/dossier-9/document-28',
                u'title': u'Umbau B\xe4rengraben',
            }],
            u'dossiers': [{
                'relative_path': u'ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-8',
                'title': u'A resolvable main dossier',
            }, {
                'relative_path': u'ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-8/dossier-9',
                'title': u'Resolvable Subdossier',
            }],
        }

        self.assertEqual(
            expected_structure, self.summarize_content(browser.json['content']))

    @browsing
    def test_content_structure_respects_all_documents_flag(self, browser):
        self.login(self.manager)
        selected_document = create(
            Builder('document')
            .within(self.resolvable_subdossier)
        )
        transfer = self.create_transfer(all_documents=False, documents=[selected_document.UID()])

        headers = self.api_headers.copy()
        headers.update({'X-GEVER-Dossier-Transfer-Token': transfer.token})

        with freeze(FROZEN_NOW):
            browser.open(
                self.portal,
                view='@dossier-transfers/%s/?full_content=1' % transfer.id,
                method='GET', headers=headers)

        self.assertEqual(200, browser.status_code)

        expected_structure = {
            u'contacts': {},
            u'documents': [{
                u'relative_path': u'ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-8/dossier-9/document-44',
                u'title': u'Testdokum\xe4nt',
            }],
            u'dossiers': [{
                'relative_path': u'ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-8',
                'title': u'A resolvable main dossier',
            }, {
                'relative_path': u'ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-8/dossier-9',
                'title': u'Resolvable Subdossier',
            }],
        }

        self.assertEqual(
            expected_structure, self.summarize_content(browser.json['content']))

    @requests_mock.Mocker()
    @browsing
    def test_content_structure_respects_all_participations_flag(self, mocker, browser):
        transfer = self.create_transfer(
            all_participations=False,
            participations=[JULIE_PERSON_ID],
        )

        self.login(self.manager)
        self.add_participation(
            mocker,
            self.resolvable_dossier,
            JEAN_PERSON_ID,
            ['regard', 'participation', 'final-drawing'],
        )
        self.add_participation(
            mocker,
            self.resolvable_dossier,
            JULIE_PERSON_ID,
            ['final-drawing'],
        )
        self.logout()

        headers = self.api_headers.copy()
        headers.update({'X-GEVER-Dossier-Transfer-Token': transfer.token})

        with freeze(FROZEN_NOW):
            browser.open(
                self.portal,
                view='@dossier-transfers/%s/?full_content=1' % transfer.id,
                method='GET', headers=headers)

        self.assertEqual(200, browser.status_code)

        expected_structure = {
            u'contacts': {
                u'person:0e623708-2d0d-436a-82c6-c1a9c27b65dc': {
                    u'type': u'person',
                    u'text': u'Dupont Julie',
                    u'title': u'',
                },
                # Jean's contact is omitted, because his participation is not selected
            },
            u'documents': [{
                u'relative_path': u'ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-8/dossier-9/document-28',
                u'title': u'Umbau B\xe4rengraben',
            }],
            u'dossiers': [{
                'relative_path': u'ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-8',
                'title': u'A resolvable main dossier',
            }, {
                'relative_path': u'ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-8/dossier-9',
                'title': u'Resolvable Subdossier',
            }],
        }

        self.assertEqual(
            expected_structure, self.summarize_content(browser.json['content']))

    @requests_mock.Mocker()
    @browsing
    def test_dossier_serialization(self, mocker, browser):
        transfer = self.create_transfer()

        self.login(self.manager)
        self.add_participation(
            mocker,
            self.resolvable_dossier,
            JEAN_PERSON_ID,
            ['regard', 'participation', 'final-drawing'],
        )
        self.logout()

        headers = self.api_headers.copy()
        headers.update({'X-GEVER-Dossier-Transfer-Token': transfer.token})

        with freeze(FROZEN_NOW):
            browser.open(
                self.portal,
                view='@dossier-transfers/%s/?full_content=1' % transfer.id,
                method='GET', headers=headers)

        self.assertEqual(200, browser.status_code)

        expected_dossier = {
            u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-8',
            u'@type': u'opengever.dossier.businesscasedossier',
            u'UID': u'createresolvabledossier000000001',
            u'allow_discussion': False,
            u'archival_value': {
                u'title': u'not assessed',
                u'token': u'unchecked',
            },
            u'archival_value_annotation': None,
            u'back_references_relatedDossier': [],
            u'blocked_local_roles': False,
            u'changed': u'2016-08-31T14:41:33+00:00',
            u'checklist': None,
            u'classification': {
                u'title': u'unprotected',
                u'token': u'unprotected',
            },
            u'container_location': None,
            u'container_type': None,
            u'created': u'2016-08-31T14:41:33+00:00',
            u'custody_period': {
                u'title': u'30',
                u'token': u'30',
            },
            u'custom_properties': None,
            u'date_of_cassation': None,
            u'date_of_submission': None,
            u'description': u'',
            u'dossier_manager': None,
            u'dossier_type': None,
            u'email': u'1014413300@example.org',
            u'end': None,
            u'external_reference': None,
            u'filing_prefix': None,
            u'former_reference_number': None,
            u'has_pending_jobs': False,
            u'id': u'dossier-8',
            u'is_folderish': True,
            u'is_protected': False,
            u'is_subdossier': False,
            u'keywords': [],
            u'layout': u'tabbed_view',
            u'modified': u'2016-08-31T14:43:33+00:00',
            u'number_of_containers': None,
            u'oguid': u'plone:1014413300',
            u'parent': {
                u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen',
                u'@type': u'opengever.repository.repositoryfolder',
                u'UID': u'createrepositorytree000000000003',
                u'description': u'',
                u'is_leafnode': True,
                u'review_state': u'repositoryfolder-state-active',
                u'title': u'1.1. Vertr\xe4ge und Vereinbarungen',
            },
            u'participations': [
                [
                    u'person:9af7d7cc-b948-423f-979f-587158c6bc65',
                    [u'regard', u'participation', u'final-drawing'],
                ],
            ],
            u'privacy_layer': {
                u'title': u'no',
                u'token': u'privacy_layer_no',
            },
            u'public_trial': {
                u'title': u'not assessed',
                u'token': u'unchecked',
            },
            u'public_trial_statement': None,
            u'reading': [],
            u'reading_and_writing': [],
            u'reference_number': u'Client1 1.1 / 5',
            u'relatedDossier': [],
            u'relative_path': u'ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-8',
            u'responses': [],
            u'responsible': {
                u'title': u'Ziegler Robert (robert.ziegler)',
                u'token': u'robert.ziegler',
            },
            u'responsible_actor': {
                u'@id': u'http://nohost/plone/@actors/robert.ziegler',
                u'identifier': u'robert.ziegler',
            },
            u'responsible_fullname': u'Ziegler Robert',
            u'retention_period': {
                u'title': u'15',
                u'token': u'15',
            },
            u'retention_period_annotation': None,
            u'review_state': u'dossier-state-active',
            u'sequence_number': 8,
            u'start': u'2016-01-01',
            u'temporary_former_reference_number': None,
            u'title': u'A resolvable main dossier',
            u'touched': u'2016-08-31',
            u'version': u'current'
        }

        dossiers = browser.json['content']['dossiers']
        self.assertEqual(expected_dossier, dossiers[0])

    @requests_mock.Mocker()
    @browsing
    def test_dossier_serialization_pcp_membership(self, mocker, browser):
        transfer = self.create_transfer()

        self.login(self.manager)
        self.mock_get_by_id(mocker, JEAN_PERSON_ID)
        self.add_participation(
            mocker,
            self.resolvable_dossier,
            JEAN_MEMBERSHIP_ID,
            ['regard', 'participation', 'final-drawing'],
        )
        self.logout()

        headers = self.api_headers.copy()
        headers.update({'X-GEVER-Dossier-Transfer-Token': transfer.token})

        with freeze(FROZEN_NOW):
            browser.open(
                self.portal,
                view='@dossier-transfers/%s/?full_content=1' % transfer.id,
                method='GET', headers=headers)

        self.assertEqual(200, browser.status_code)

        expected_participations = [
            # We're expecting the ID of the referenced person, not the membership
            [
                JEAN_PERSON_ID,
                [u'regard', u'participation', u'final-drawing'],
            ],
        ]

        root_dossier = browser.json['content']['dossiers'][0]
        self.assertEqual(expected_participations, root_dossier['participations'])

    @requests_mock.Mocker()
    @browsing
    def test_dossier_serialization_respects_all_participations_flag(self, mocker, browser):
        transfer = self.create_transfer(
            all_participations=False,
            participations=[JULIE_PERSON_ID],
        )

        self.login(self.manager)
        self.add_participation(
            mocker,
            self.resolvable_dossier,
            JEAN_PERSON_ID,
            ['regard', 'participation', 'final-drawing'],
        )
        self.add_participation(
            mocker,
            self.resolvable_dossier,
            JULIE_PERSON_ID,
            ['final-drawing'],
        )
        self.logout()

        headers = self.api_headers.copy()
        headers.update({'X-GEVER-Dossier-Transfer-Token': transfer.token})

        with freeze(FROZEN_NOW):
            browser.open(
                self.portal,
                view='@dossier-transfers/%s/?full_content=1' % transfer.id,
                method='GET', headers=headers)

        self.assertEqual(200, browser.status_code)

        expected_participations = [
            [
                u'person:0e623708-2d0d-436a-82c6-c1a9c27b65dc',
                [u'final-drawing'],
            ],
            # Jean's participation is omitted, because it wasn't selected
        ]

        root_dossier = browser.json['content']['dossiers'][0]
        self.assertEqual(expected_participations, root_dossier['participations'])

    @browsing
    def test_document_serialization(self, browser):
        transfer = self.create_transfer()

        headers = self.api_headers.copy()
        headers.update({'X-GEVER-Dossier-Transfer-Token': transfer.token})

        with freeze(FROZEN_NOW):
            browser.open(
                self.portal,
                view='@dossier-transfers/%s/?full_content=1' % transfer.id,
                method='GET', headers=headers)

        self.assertEqual(200, browser.status_code)

        expected_document = {
            u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-8/dossier-9/document-28',
            u'@type': u'opengever.document.document',
            u'UID': u'createresolvabledossier000000003',
            u'allow_discussion': False,
            u'archival_file': None,
            u'archival_file_state': None,
            u'back_references_relatedItems': [],
            u'changeNote': u'',
            u'changed': u'2016-08-31T14:45:33+00:00',
            u'checked_out': None,
            u'checked_out_fullname': None,
            u'checkout_collaborators': [],
            u'classification': {
                u'title': u'unprotected',
                u'token': u'unprotected',
            },
            u'containing_dossier': u'A resolvable main dossier',
            u'containing_subdossier': u'Resolvable Subdossier',
            u'containing_subdossier_url': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-8/dossier-9',
            u'created': u'2016-08-31T14:45:33+00:00',
            u'creator': {
                u'@id': u'http://nohost/plone/@actors/robert.ziegler',
                u'identifier': u'robert.ziegler',
            },
            u'current_version_id': 0,
            u'custom_properties': None,
            u'delivery_date': None,
            u'description': u'',
            u'digitally_available': True,
            u'document_author': None,
            u'document_date': u'2010-01-03T00:00:00',
            u'document_type': None,
            u'file': {
                u'content-type': u'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                u'download': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-8/dossier-9/document-28/@@download/file',
                u'filename': u'Umbau Baerengraben.docx',
                u'size': 27413,
            },
            u'file_extension': u'.docx',
            u'foreign_reference': None,
            u'getObjPositionInParent': 0,
            u'gever_url': u'',
            u'id': u'document-28',
            u'is_collaborative_checkout': False,
            u'is_folderish': False,
            u'is_locked': False,
            u'is_shadow_document': False,
            u'keywords': [],
            u'layout': u'tabbed_view',
            u'modified': u'2016-08-31T14:45:33+00:00',
            u'next_item': {},
            u'oguid': u'plone:1014453300',
            u'parent': {
                u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-8/dossier-9',
                u'@type': u'opengever.dossier.businesscasedossier',
                u'UID': u'createresolvabledossier000000002',
                u'description': u'',
                u'dossier_type': None,
                u'is_leafnode': None,
                u'is_subdossier': True,
                u'review_state': u'dossier-state-active',
                u'title': u'Resolvable Subdossier',
            },
            u'preserved_as_paper': True,
            u'preview': None,
            u'previous_item': {},
            u'privacy_layer': {
                u'title': u'no',
                u'token': u'privacy_layer_no',
            },
            u'public_trial': {
                u'title': u'not assessed',
                u'token': u'unchecked',
            },
            u'public_trial_statement': None,
            u'receipt_date': None,
            u'reference_number': u'Client1 1.1 / 5.1 / 28',
            u'relatedItems': [],
            u'relative_path': u'ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-8/dossier-9/document-28',
            u'review_state': u'document-state-draft',
            u'sequence_number': 28,
            u'teamraum_connect_links': {
                u'gever_document': None,
                u'workspace_documents': [],
            },
            u'thumbnail': None,
            u'title': u'Umbau B\xe4rengraben',
            u'trashed': False,
            u'version': u'current',
            u'workspace_document_urls': [],
        }

        documents = browser.json['content']['documents']
        document = documents[0]

        # file_mtime is flaky because it doesn't get frozen with enough precision
        document.pop('file_mtime')

        self.assertEqual(expected_document, document)

    @requests_mock.Mocker()
    @browsing
    def test_contact_person_serialization(self, mocker, browser):
        transfer = self.create_transfer()

        self.login(self.manager)
        self.add_participation(
            mocker,
            self.resolvable_dossier,
            JEAN_PERSON_ID,
            ['regard', 'participation', 'final-drawing'],
        )
        self.logout()

        headers = self.api_headers.copy()
        headers.update({'X-GEVER-Dossier-Transfer-Token': transfer.token})

        with freeze(FROZEN_NOW):
            browser.open(
                self.portal,
                view='@dossier-transfers/%s/?full_content=1' % transfer.id,
                method='GET', headers=headers)

        self.assertEqual(200, browser.status_code)

        expected_contact = {
            u'additional_ui_attributes': [],
            u'addresses': [{
                u'addressLine1': u'',
                u'addressLine2': u'',
                u'countryIdISO2': u'CH',
                u'countryName': u'Schweiz',
                u'created': u'2021-11-18T00:00:00+01:00',
                u'dwellingNumber': u'',
                u'foreignZipCode': u'',
                u'houseNumber': u'43',
                u'id': u'72b3120e-429f-423b-8bb7-31233d89026c',
                u'isDefault': True,
                u'label': u'Home',
                u'locality': u'',
                u'modified': u'2021-11-18T00:00:00+01:00',
                u'organisationName': u'',
                u'organisationNameAddOn1': u'',
                u'organisationNameAddOn2': u'',
                u'postOfficeBox': u'',
                u'street': u'Teststrasse',
                u'swissZipCode': u'9999',
                u'swissZipCodeAddOn': u'',
                u'swissZipCodeId': u'',
                u'thirdPartyId': None,
                u'town': u'Bern',
            }],
            u'country': u'',
            u'countryIdISO2': u'',
            u'created': u'2021-11-17T00:00:00+01:00',
            u'customValues': {},
            u'dateOfBirth': u'1992-05-15',
            u'dateOfDeath': None,
            u'description': u'',
            u'emailAddresses': [{
                u'created': u'2021-11-18T00:00:00+01:00',
                u'email': u'Jean.dupon@example.com',
                u'id': u'3bc940de-ee8a-43b0-b373-3f1640122021',
                u'isDefault': True,
                u'label': u'Private',
                u'modified': u'2021-11-18T00:00:00+01:00',
                u'thirdPartyId': None,
            }],
            u'firstName': u'Jean',
            u'fullName': u'Dupont Jean',
            u'htmlUrl': u'http://localhost:8000/people/9af7d7cc-b948-423f-979f-587158c6bc65',
            u'id': u'9af7d7cc-b948-423f-979f-587158c6bc65',
            u'languageOfCorrespondance': u'fr',
            u'memberships': [{
                u'department': u'',
                u'description': u'',
                u'end': None,
                u'id': u'8345fcfe-2d67-4b75-af46-c25b2f387448',
                u'organization': {
                    u'created': u'2021-11-13T00:00:00+01:00',
                    u'description': u'Web application specialist',
                    u'id': u'30bab83d-300a-4886-97d4-ff592e88a56a',
                    u'memberCount': 1,
                    u'modified': u'2021-11-13T00:00:00+01:00',
                    u'name': u'4Teamwork',
                    u'status': 1,
                    u'thirdPartyId': None,
                },
                u'primaryAddress': {
                    u'addressLine1': u'c/o John Doe',
                    u'addressLine2': u'',
                    u'countryIdISO2': u'CH',
                    u'countryName': u'Schweiz',
                    u'created': u'2021-11-18T00:00:00+01:00',
                    u'dwellingNumber': u'',
                    u'foreignZipCode': u'',
                    u'houseNumber': u'9',
                    u'id': u'ad0de780-3f62-400c-921a-0feb9e79c062',
                    u'isDefault': True,
                    u'label': u'Standort Bern',
                    u'locality': u'',
                    u'modified': u'2021-11-18T00:00:00+01:00',
                    u'organisationName': u'',
                    u'organisationNameAddOn1': u'',
                    u'organisationNameAddOn2': u'',
                    u'postOfficeBox': u'',
                    u'street': u'Dammweg',
                    u'swissZipCode': u'3013',
                    u'swissZipCodeAddOn': u'',
                    u'swissZipCodeId': u'',
                    u'thirdPartyId': None,
                    u'town': u'Bern',
                },
                u'primaryEmail': {
                    u'created': u'2021-11-18T00:00:00+01:00',
                    u'email': u'Jean.dupon@example.com',
                    u'id': u'3bc940de-ee8a-43b0-b373-3f1640122021',
                    u'isDefault': True,
                    u'label': u'Private',
                    u'modified': u'2021-11-18T00:00:00+01:00',
                    u'thirdPartyId': None,
                },
                u'primaryPhoneNumber': {
                    u'created': u'2021-11-18T00:00:00+01:00',
                    u'id': u'e1046ad8-c4d7-4cac-93ac-d7c8298795e5',
                    u'isDefault': True,
                    u'label': u'Mobile',
                    u'modified': u'2021-11-18T00:00:00+01:00',
                    u'otherPhoneCategory': None,
                    u'phoneCategory': 2,
                    u'phoneCategoryText': u'Private Mobilnummer',
                    u'phoneNumber': u'666 666 66 66',
                    u'thirdPartyId': None,
                },
                u'role': u'CEO',
                u'start': u'1990-02-24',
                u'thirdPartyId': None,
            }],
            u'modified': u'2021-11-17T00:00:00+01:00',
            u'officialName': u'Dupont',
            u'organizations': [{
                u'created': u'2021-11-13T00:00:00+01:00',
                u'description': u'Web application specialist',
                u'id': u'30bab83d-300a-4886-97d4-ff592e88a56a',
                u'memberCount': 1,
                u'modified': u'2021-11-13T00:00:00+01:00',
                u'name': u'4Teamwork',
                u'status': 1,
                u'thirdPartyId': None,
            }],
            u'personType': None,
            u'personTypeTitle': None,
            u'phoneNumbers': [{
                u'created': u'2021-11-18T00:00:00+01:00',
                u'id': u'e1046ad8-c4d7-4cac-93ac-d7c8298795e5',
                u'isDefault': True,
                u'label': u'Mobile',
                u'modified': u'2021-11-18T00:00:00+01:00',
                u'otherPhoneCategory': None,
                u'phoneCategory': 2,
                u'phoneCategoryText': u'Private Mobilnummer',
                u'phoneNumber': u'666 666 66 66',
                u'thirdPartyId': None,
            }, {
                u'created': u'2021-11-18T00:00:00+01:00',
                u'id': u'c62732e1-114e-4de7-a0b7-842c325bb068',
                u'isDefault': False,
                u'label': u'Work',
                u'modified': u'2021-11-18T00:00:00+01:00',
                u'otherPhoneCategory': None,
                u'phoneCategory': 7,
                u'phoneCategoryText': u'Gesch\xe4ftliche Mobilnummer',
                u'phoneNumber': u'999 999 99 99',
                u'thirdPartyId': None,
            }],
            u'primaryAddress': {
                u'addressLine1': u'',
                u'addressLine2': u'',
                u'countryIdISO2': u'CH',
                u'countryName': u'Schweiz',
                u'created': u'2021-11-18T00:00:00+01:00',
                u'dwellingNumber': u'',
                u'foreignZipCode': u'',
                u'houseNumber': u'43',
                u'id': u'72b3120e-429f-423b-8bb7-31233d89026c',
                u'isDefault': True,
                u'label': u'Home',
                u'locality': u'',
                u'modified': u'2021-11-18T00:00:00+01:00',
                u'organisationName': u'',
                u'organisationNameAddOn1': u'',
                u'organisationNameAddOn2': u'',
                u'postOfficeBox': u'',
                u'street': u'Teststrasse',
                u'swissZipCode': u'9999',
                u'swissZipCodeAddOn': u'',
                u'swissZipCodeId': u'',
                u'thirdPartyId': None,
                u'town': u'Bern',
            },
            u'primaryEmail': {
                u'created': u'2021-11-18T00:00:00+01:00',
                u'email': u'Jean.dupon@example.com',
                u'id': u'3bc940de-ee8a-43b0-b373-3f1640122021',
                u'isDefault': True,
                u'label': u'Private',
                u'modified': u'2021-11-18T00:00:00+01:00',
                u'thirdPartyId': None,
            },
            u'primaryPhoneNumber': {
                u'created': u'2021-11-18T00:00:00+01:00',
                u'id': u'e1046ad8-c4d7-4cac-93ac-d7c8298795e5',
                u'isDefault': True,
                u'label': u'Mobile',
                u'modified': u'2021-11-18T00:00:00+01:00',
                u'otherPhoneCategory': None,
                u'phoneCategory': 2,
                u'phoneCategoryText': u'Private Mobilnummer',
                u'phoneNumber': u'666 666 66 66',
                u'thirdPartyId': None,
            },
            u'primaryUrl': None,
            u'readableAge': u'30 Jahre und 6 Monate',
            u'salutation': u'Herr',
            u'sex': None,
            u'status': 1,
            u'tags': [],
            u'text': u'Dupont Jean',
            u'thirdPartyId': None,
            u'title': u'',
            u'type': u'person',
            u'typedId': u'person:9af7d7cc-b948-423f-979f-587158c6bc65',
            u'url': u'http://localhost:8000/api/v2/people/9af7d7cc-b948-423f-979f-587158c6bc65',
            u'urls': [],
            u'username': None,
        }

        contacts = browser.json['content']['contacts']
        self.assertEqual(expected_contact, contacts[JEAN_PERSON_ID])

    @requests_mock.Mocker()
    @browsing
    def test_contact_membership_serialization(self, mocker, browser):
        transfer = self.create_transfer()

        self.login(self.manager)
        self.mock_get_by_id(mocker, JEAN_PERSON_ID)
        self.add_participation(
            mocker,
            self.resolvable_dossier,
            JEAN_MEMBERSHIP_ID,
            ['regard', 'participation', 'final-drawing'],
        )
        self.logout()

        headers = self.api_headers.copy()
        headers.update({'X-GEVER-Dossier-Transfer-Token': transfer.token})

        with freeze(FROZEN_NOW):
            browser.open(
                self.portal,
                view='@dossier-transfers/%s/?full_content=1' % transfer.id,
                method='GET', headers=headers)

        self.assertEqual(200, browser.status_code)

        contacts = browser.json['content']['contacts']
        contact = contacts[JEAN_PERSON_ID]

        expected_contact = {
            u'type': u'person',
            u'typedId': u'person:9af7d7cc-b948-423f-979f-587158c6bc65',
            u'text': u'Dupont Jean',
            # ...
            # (same as a serialized person, even though it's a membership)
        }

        self.assertDictContainsSubset(expected_contact, contact)

    @browsing
    def test_document_blob_download(self, browser):
        transfer = self.create_transfer()

        headers = self.api_headers.copy()
        headers.update({'X-GEVER-Dossier-Transfer-Token': transfer.token})

        with elevated_privileges():
            doc = self.resolvable_document
            doc_uid = doc.UID()
            filename = doc.file.filename
            filesize = doc.file.getSize()
            filedata = doc.file.data

        with freeze(FROZEN_NOW):
            browser.open(
                self.portal,
                view='@dossier-transfers/%s/blob/%s' % (transfer.id, doc_uid),
                method='GET', headers=headers)

        self.assertEqual(200, browser.status_code)

        expected_headers = {
            'content-disposition': 'attachment; filename="%s"' % filename,
            'content-length': str(filesize),
            'content-type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        }
        self.assertDictContainsSubset(expected_headers, browser.headers)
        self.assertEqual(filesize, len(browser.contents))
        self.assertEqual(filedata, browser.contents)

    @browsing
    def test_document_blob_download_requires_token(self, browser):
        transfer = self.create_transfer()

        with elevated_privileges():
            doc_uid = self.resolvable_document.UID()

        with freeze(FROZEN_NOW):
            with browser.expect_http_error(code=401):
                browser.open(
                    self.portal,
                    view='@dossier-transfers/%s/blob/%s' % (transfer.id, doc_uid),
                    method='GET', headers=self.api_headers)

    @browsing
    def test_document_blob_download_returns_404_for_nonexistent_doc(self, browser):
        transfer = self.create_transfer()

        headers = self.api_headers.copy()
        headers.update({'X-GEVER-Dossier-Transfer-Token': transfer.token})

        doc_uid = '404-doesnt-exist'
        with freeze(FROZEN_NOW):
            with browser.expect_http_error(code=404):
                browser.open(
                    self.portal,
                    view='@dossier-transfers/%s/blob/%s' % (transfer.id, doc_uid),
                    method='GET', headers=headers)

    @browsing
    def test_document_blob_download_returns_unauthorized_for_unselected_doc(self, browser):
        transfer = self.create_transfer(all_documents=False, documents=[])

        headers = self.api_headers.copy()
        headers.update({'X-GEVER-Dossier-Transfer-Token': transfer.token})

        with elevated_privileges():
            doc_uid = self.resolvable_document.UID()

        with freeze(FROZEN_NOW):
            with browser.expect_http_error(code=401):
                browser.open(
                    self.portal,
                    view='@dossier-transfers/%s/blob/%s' % (transfer.id, doc_uid),
                    method='GET', headers=headers)


class TestDossierTransfersGetPermissionsBase(IntegrationTestCase):

    features = ('dossier-transfers', )

    def create_transfers(self):
        with freeze(FROZEN_NOW):
            session = create_session()

            self.login(self.secretariat_user)

            transfer = create(Builder('dossier_transfer')
                              .having(
                                  title='Transfer owned by secretariat_user'))
            session.add(transfer)
            session.flush()
            self.transfer_owned_by_secretariat = transfer

            self.login(self.dossier_responsible)

            transfer = create(Builder('dossier_transfer')
                              .having(
                                  title='Transfer owned by dossier_responsible'))
            session.add(transfer)
            session.flush()
            self.transfer_owned_by_responsible = transfer

            self.login(self.manager)

            create(Builder('admin_unit')
                   .id('other1')
                   .having(title='Other AU 1'))

            create(Builder('admin_unit')
                   .id('other2')
                   .having(title='Other AU 2'))

            transfer = create(Builder('dossier_transfer')
                              .having(
                                  title='Transfer between other admin units',
                                  source_id='other1',
                                  target_id='other2'))
            session.add(transfer)
            session.flush()
            self.transfer_between_other_units = transfer

    def fetch_transfer(self, transfer, browser, headers=None, qs=None):
        request_headers = self.api_headers.copy()
        if headers:
            request_headers.update(headers)

        view = '@dossier-transfers/%s' % transfer.id
        if qs:
            view = '?'.join((view, qs))

        browser.open(self.portal, view=view,
                     method='GET', headers=request_headers)


class TestDossierTransfersGetPermissions(TestDossierTransfersGetPermissionsBase):

    @browsing
    def test_fetch_permissions(self, browser):
        self.create_transfers()

        expected = {
            # User in inbox group
            self.secretariat_user.id: [
                (self.transfer_owned_by_secretariat, 200),
                (self.transfer_owned_by_responsible, 200),
                (self.transfer_between_other_units, 401),
            ],
            # User owning one of the transfers
            self.dossier_responsible.id: [
                (self.transfer_owned_by_secretariat, 401),
                (self.transfer_owned_by_responsible, 200),
                (self.transfer_between_other_units, 401),
            ],
            # User not in inbox group and not owning any transfers
            self.regular_user.id: [
                (self.transfer_owned_by_secretariat, 401),
                (self.transfer_owned_by_responsible, 401),
                (self.transfer_between_other_units, 401),
            ],
        }

        browser.raise_http_errors = False
        for user_id, expectations in expected.items():
            user = api.user.get(userid=user_id)
            self.login(user, browser=browser)

            for transfer, expected_status in expectations:
                self.fetch_transfer(transfer, browser)
                self.assertEqual(
                    expected_status,
                    browser.status_code,
                    'Expected HTTP status %s for request by user %s on '
                    'transfer %r (%s)' % (
                        expected_status, user, transfer, transfer.title))

    @browsing
    def test_listing_permissions(self, browser):
        self.create_transfers()

        expected = {
            # User in inbox group
            self.secretariat_user.id: [
                (1, u'Transfer owned by secretariat_user'),
                (2, u'Transfer owned by dossier_responsible'),
            ],
            # User owning one of the transfers
            self.dossier_responsible.id: [
                (2, u'Transfer owned by dossier_responsible'),
            ],
            # User not in inbox group and not owning any transfers
            self.regular_user.id: [],
        }

        results = {}

        for user_id, expectations in expected.items():
            user = api.user.get(userid=user_id)
            self.login(user, browser=browser)

            browser.open(self.portal, view='@dossier-transfers/',
                         method='GET', headers=self.api_headers)

            items = [(tf['id'], tf['title']) for tf in browser.json['items']]
            results[user_id] = items

        self.assertEqual(expected, results)

    @browsing
    def test_listing_permissions_for_manager(self, browser):
        self.create_transfers()

        expected = [
            (1, u'Transfer owned by secretariat_user'),
            (2, u'Transfer owned by dossier_responsible'),
            (3, u'Transfer between other admin units'),
        ]

        self.login(self.manager, browser=browser)
        browser.open(self.portal, view='@dossier-transfers/',
                     method='GET', headers=self.api_headers)

        items = [(tf['id'], tf['title']) for tf in browser.json['items']]
        self.assertEqual(expected, items)


class TestDossierTransfersGetFullContentsPermissions(TestDossierTransfersGetPermissionsBase):

    @browsing
    def test_authorizes_anonymous_requests_with_valid_token(self, browser):
        self.create_transfers()

        expected = [
            (self.transfer_owned_by_secretariat, 200),
            (self.transfer_owned_by_responsible, 200),
            (self.transfer_between_other_units, 401),
        ]

        browser.raise_http_errors = False

        # Guard assertion - anonymous request without token authoring the request
        # would normally be rejected with 401 Unauthorized.
        self.fetch_transfer(self.transfer_owned_by_secretariat, browser)
        self.assertEqual(401, browser.status_code)

        for transfer, expected_status in expected:
            headers = {'X-GEVER-Dossier-Transfer-Token': transfer.token}

            with freeze(FROZEN_NOW):
                self.fetch_transfer(transfer, browser, headers=headers)

            self.assertEqual(
                expected_status,
                browser.status_code,
                'Expected HTTP status %s for request by Anonymous user '
                'authorized via token on transfer %r (%s)' % (
                    expected_status, transfer, transfer.title))

    @browsing
    def test_fetching_full_content_requires_valid_token(self, browser):
        self.create_transfers()

        browser.raise_http_errors = False
        transfer = self.transfer_owned_by_responsible

        # Guard assertion - owner of transfer may fetch a regular GET
        # representation of the transfer *without* full_content
        self.login(self.dossier_responsible, browser=browser)
        self.fetch_transfer(transfer, browser)
        self.assertEqual(200, browser.status_code)

        with freeze(FROZEN_NOW):
            self.fetch_transfer(
                transfer, browser, qs='full_content=1')
            self.assertEqual(401, browser.status_code)

            headers = {'X-GEVER-Dossier-Transfer-Token': transfer.token}
            self.fetch_transfer(
                transfer, browser, headers=headers, qs='full_content=1')
            self.assertEqual(200, browser.status_code)

            self.assertIn('content', browser.json)
            self.assertIn('dossiers', browser.json['content'])
            self.assertIn('documents', browser.json['content'])
            self.assertIn('contacts', browser.json['content'])
