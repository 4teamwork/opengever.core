from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testing import freeze
from opengever.base.model import create_session
from opengever.testing import IntegrationTestCase
from plone import api
import pytz


class TestDossierTransfersGet(IntegrationTestCase):

    features = ('dossier-transfers', )

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

        items = [(tf['id'], tf['title']) for tf in browser.json['items']]
        expected = [
            (6, u'Pending recent transfer'),
            (2, u'Pending old transfer'),
            (4, u'Pending ancient transfer'),
            (5, u'Completed recent transfer'),
            (1, u'Completed old transfer'),
            (3, u'Completed ancient transfer'),
        ]
        self.assertEqual(expected, items)


class TestDossierTransfersGetPermissions(IntegrationTestCase):

    features = ('dossier-transfers', )

    def create_transfers(self):
        with freeze(datetime(2024, 2, 18, 15, 45, tzinfo=pytz.utc)):
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

    def fetch_transfer(self, transfer, browser):
        browser.open(self.portal, view='@dossier-transfers/%s' % transfer.id,
                     method='GET', headers=self.api_headers)

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
