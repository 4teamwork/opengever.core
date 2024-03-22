from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testing import freeze
from opengever.base.model import create_session
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.testing import IntegrationTestCase
from plone import api
import pytz


FROZEN_NOW = datetime(2024, 2, 18, 15, 45, tzinfo=pytz.utc)


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


class TestDossierTransfersGetFullContent(IntegrationTestCase):

    features = ('dossier-transfers', )

    def create_transfer(self):
        with freeze(FROZEN_NOW):
            transfer = create(
                Builder('dossier_transfer')
                .having(
                    all_documents=True,
                    all_participations=True,
                )
            )
            session = create_session()
            session.add(transfer)
            session.flush()
        return transfer

    def summarize_items(self, items):
        def summarize_item(item):
            keep = ('title', 'relative_path')
            return {key: value for key, value in item.items() if key in keep}

        return [summarize_item(item) for item in items]

    def summarize_content(self, content):
        summary = {}
        for key, value in content.items():
            summary[key] = self.summarize_items(value)

        return summary

    @browsing
    def test_content_structure(self, browser):
        transfer = self.create_transfer()

        headers = self.api_headers.copy()
        headers.update({'X-GEVER-Dossier-Transfer-Token': transfer.token})

        with freeze(FROZEN_NOW):
            browser.open(
                self.portal,
                view='@dossier-transfers/%s/?full_content=1' % transfer.id,
                method='GET', headers=headers)

        self.assertEqual(200, browser.status_code)

        expected_structure = {
            u'contacts': [],
            u'documents': [],
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
    def test_dossier_serialization(self, browser):
        transfer = self.create_transfer()

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
