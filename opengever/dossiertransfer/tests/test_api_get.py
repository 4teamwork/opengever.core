from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testing import freeze
from opengever.base.model import create_session
from opengever.testing import IntegrationTestCase
import pytz


class TestDossierTransfersGet(IntegrationTestCase):

    features = ('dossier-transfers', )

    @browsing
    def test_get_dossier_transfer(self, browser):
        self.login(self.manager, browser=browser)

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
            u'source_user': u'regular_user',
            u'root': u'createresolvabledossier000000001',
            u'documents': [u'createresolvabledossier000000003'],
            u'participations': [u'meeting_user'],
            u'all_documents': False,
            u'all_participations': False,
        }
        self.assertEqual(expected, browser.json)

    @browsing
    def test_get_dossier_transfer_listing(self, browser):
        self.login(self.manager, browser=browser)

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
                    u'source_user': u'regular_user',
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
                    u'source_user': u'regular_user',
                    u'root': u'createresolvabledossier000000001',
                    u'documents': [u'createresolvabledossier000000003'],
                    u'participations': [u'meeting_user'],
                    u'all_documents': False,
                    u'all_participations': False,
                }
            ]
        }
        self.assertEqual(expected, browser.json)
