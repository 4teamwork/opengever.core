from datetime import datetime
from datetime import timedelta
from ftw.builder import Builder
from ftw.builder import create
from ftw.testing import freeze
from opengever.base.model import create_session
from opengever.dossiertransfer.model import DossierTransfer
from opengever.dossiertransfer.model import TRANSFER_STATE_PENDING
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.ogds.models.service import ogds_service
from opengever.testing import IntegrationTestCase
import pytz


class TestDossierTransferModel(IntegrationTestCase):

    features = ('dossier-transfers', )

    def test_dossier_transfer_creation(self):
        self.login(self.regular_user)

        src_user = ogds_service().fetch_user(self.regular_user.id)
        recipient = create(Builder('admin_unit')
                           .id('recipient')
                           .having(title='Remote Recipient'))

        now = datetime(2024, 2, 18, 15, 45, tzinfo=pytz.utc)
        with freeze(now):
            transfer = DossierTransfer(
                title=u'Transfer Title',
                message=u'Transfer Message',
                state=TRANSFER_STATE_PENDING,
                source=get_current_admin_unit(),
                target=recipient,
                source_user=src_user,
                root=self.dossier.UID(),
                documents=[self.document.UID()],
                participations=['participation1'],
                all_documents=False,
                all_participations=False,
            )
            session = create_session()
            session.add(transfer)
            session.flush()

        self.assertEqual(1, transfer.id)
        self.assertEqual(u'Transfer Title', transfer.title)
        self.assertEqual(u'Transfer Message', transfer.message)
        self.assertEqual(now, transfer.created)
        self.assertEqual(now + timedelta(days=30), transfer.expires)
        self.assertEqual(TRANSFER_STATE_PENDING, transfer.state)

        self.assertEqual(get_current_admin_unit(), transfer.source)
        self.assertEqual(get_current_admin_unit().unit_id, transfer.source_id)

        self.assertEqual(recipient, transfer.target)
        self.assertEqual(recipient.unit_id, transfer.target_id)

        self.assertEqual(src_user, transfer.source_user)
        self.assertEqual(src_user.userid, transfer.source_user_id)

        self.assertEqual(self.dossier.UID(), transfer.root)
        self.assertEqual([self.document.UID()], transfer.documents)
        self.assertEqual(['participation1'], transfer.participations)

        self.assertFalse(transfer.all_documents)
        self.assertFalse(transfer.all_participations)
