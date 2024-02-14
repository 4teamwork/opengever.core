from datetime import datetime
from datetime import timedelta
from ftw.builder import Builder
from ftw.builder import create
from ftw.testing import freeze
from opengever.base.model import create_session
from opengever.ogds.models.service import ogds_service
from opengever.testing import IntegrationTestCase
from plone.restapi.interfaces import ISerializeToJson
from zope.component import getMultiAdapter
from zope.globalrequest import getRequest
import pytz


class TestDossierTransferSerializer(IntegrationTestCase):

    features = ('dossier-transfers', )

    def test_dossier_transfer_serializer(self):
        self.login(self.regular_user)

        src_user = ogds_service().fetch_user(self.regular_user.id)

        now = datetime(2024, 2, 18, 15, 45, tzinfo=pytz.utc)
        with freeze(now):
            transfer = create(Builder('dossier_transfer'))
            session = create_session()
            session.add(transfer)
            session.flush()

        transfer.all_participations = False
        transfer.participations = ['meeting_user']

        expected = {
            '@id': 'http://nohost/plone/@dossier-transfers/1',
            '@type': 'virtual.ogds.dossiertransfer',
            'id': 1,
            'title': 'Transfer Title',
            'message': 'Transfer Message',
            'created': now.isoformat(),
            'expires': (now + timedelta(days=30)).isoformat(),
            'state': 'pending',
            'source': {
                'token': 'plone',
                'title': 'Hauptmandant',
            },
            'target': {
                'token': 'recipient',
                'title': 'Remote Recipient',
            },
            'source_user': src_user.userid,
            'root': self.resolvable_dossier.UID(),
            'documents': [self.resolvable_document.UID()],
            'participations': ['meeting_user'],
            'all_documents': False,
            'all_participations': False,
        }

        serializer = getMultiAdapter((transfer, getRequest()), ISerializeToJson)
        self.assertEqual(expected, serializer())
