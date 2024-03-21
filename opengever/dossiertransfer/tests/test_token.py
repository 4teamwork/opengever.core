from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testing import freeze
from opengever.base.model import create_session
from opengever.dossiertransfer.model import TRANSFER_STATE_COMPLETED
from opengever.dossiertransfer.model import TRANSFER_STATE_PENDING
from opengever.dossiertransfer.token import InvalidToken
from opengever.dossiertransfer.token import TokenManager
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.testing import IntegrationTestCase
from plone.keyring.interfaces import IKeyManager
from zope.component import getUtility
import jwt
import os
import pytz


FROZEN_NOW = datetime(2024, 2, 18, 15, 45, tzinfo=pytz.utc)


class TestTokenManager(IntegrationTestCase):

    features = ('dossier-transfers', )

    def setUp(self):
        super(TestTokenManager, self).setUp()
        self.token_manager = TokenManager()

    def new_transfer(self):
        with freeze(FROZEN_NOW):
            transfer = create(Builder('dossier_transfer'))
            session = create_session()
            session.add(transfer)
            session.flush()
        return transfer

    def create_claims(self, transfer):
        return {
            'jti': os.urandom(16).encode('hex'),
            'iss': get_current_admin_unit().unit_id,
            'iat': transfer.created,
            'exp': transfer.expires,
            'transfer_id': transfer.id,
            'attributes_hash': transfer.attributes_hash(),
        }

    def create_token(self, claims):
        return jwt.encode(
            claims,
            self.token_manager._signing_secret(),
            algorithm='HS256')

    def test_token_creation(self):
        self.login(self.regular_user)

        transfer = self.new_transfer()

        with freeze(FROZEN_NOW):
            token = self.token_manager.issue_token(transfer)
            claims = self.token_manager._decode_token(token)

        expected = {
            u'iat': 1708271100,
            u'exp': 1710863100,
            u'iss': u'plone',
            u'transfer_id': 1,
            u'attributes_hash': u'59b94dbd6a7f87c1390408b8afab5e80f2c91f0d2ef52b8ae168fb5da5c59dcd',
        }
        self.assertDictContainsSubset(expected, claims)
        self.assertIn(u'jti', claims.keys())

    def test_valid_token_passes_validation(self):
        self.login(self.regular_user)

        transfer = self.new_transfer()
        token = self.token_manager.issue_token(transfer)

        with freeze(FROZEN_NOW):
            self.assertIsNone(self.token_manager.validate_token(transfer, token))

    def test_invalid_token_fails_validation(self):
        self.login(self.regular_user)

        transfer = self.new_transfer()
        with freeze(FROZEN_NOW):
            with self.assertRaises(InvalidToken):
                self.token_manager.validate_token(transfer, 'invalid-token')

    def test_token_with_wrong_issuer_fails_validation(self):
        self.login(self.regular_user)

        transfer = self.new_transfer()

        # Guard assertion
        with freeze(FROZEN_NOW):
            claims = self.create_claims(transfer)
            token = self.create_token(claims)
            transfer.token = token
            self.assertIsNone(self.token_manager.validate_token(transfer, token))

        # Wrong issuer (doesn't match current admin unit)
        claims = self.create_claims(transfer)
        claims['iss'] = 'some_other_admin_unit'
        token = self.create_token(claims)

        with self.assertRaises(InvalidToken):
            self.token_manager.validate_token(transfer, token)

    def test_token_with_wrong_transfer_id_fails_validation(self):
        self.login(self.regular_user)

        transfer = self.new_transfer()

        # Guard assertion
        with freeze(FROZEN_NOW):
            claims = self.create_claims(transfer)
            token = self.create_token(claims)
            transfer.token = token
            self.assertIsNone(self.token_manager.validate_token(transfer, token))

        # Wrong issuer (doesn't match current admin unit)
        claims = self.create_claims(transfer)
        claims['transfer_id'] = 77

        with freeze(FROZEN_NOW):
            token = self.create_token(claims)
            with self.assertRaises(InvalidToken):
                self.token_manager.validate_token(transfer, token)

    def test_decode_token_after_key_rotation(self):
        self.login(self.regular_user)

        transfer = self.new_transfer()
        token = self.token_manager.issue_token(transfer)

        key_manager = getUtility(IKeyManager)
        key_manager.rotate()

        with freeze(FROZEN_NOW):
            claims = self.token_manager._decode_token(token)
        self.assertEqual(transfer.id, claims['transfer_id'])

    def test_tampered_attributes_fail_validation(self):
        self.login(self.regular_user)

        transfer = self.new_transfer()
        token = self.token_manager.issue_token(transfer)

        # Guard assertion
        with freeze(FROZEN_NOW):
            self.assertIsNone(self.token_manager.validate_token(transfer, token))

        # Tampering with 'state'
        transfer = self.new_transfer()
        transfer.state = TRANSFER_STATE_COMPLETED
        token = self.token_manager.issue_token(transfer)
        transfer.state = TRANSFER_STATE_PENDING

        with self.assertRaises(InvalidToken):
            with freeze(FROZEN_NOW):
                self.token_manager.validate_token(transfer, token)

        # Tampering with 'target_id'
        transfer = self.new_transfer()
        token = self.token_manager.issue_token(transfer)
        transfer.target_id = u'plone'

        with self.assertRaises(InvalidToken):
            with freeze(FROZEN_NOW):
                self.token_manager.validate_token(transfer, token)

        # Tampering with 'source_user_id'
        transfer = self.new_transfer()
        token = self.token_manager.issue_token(transfer)
        transfer.source_user_id = u'meeting_user'

        with self.assertRaises(InvalidToken):
            with freeze(FROZEN_NOW):
                self.token_manager.validate_token(transfer, token)

        # Tampering with 'root'
        transfer = self.new_transfer()
        token = self.token_manager.issue_token(transfer)
        transfer.root = self.meeting_dossier.UID()

        with self.assertRaises(InvalidToken):
            with freeze(FROZEN_NOW):
                self.token_manager.validate_token(transfer, token)

        # Tampering with 'documents'
        transfer = self.new_transfer()
        token = self.token_manager.issue_token(transfer)
        transfer.documents = [self.meeting_document.UID()]

        with self.assertRaises(InvalidToken):
            with freeze(FROZEN_NOW):
                self.token_manager.validate_token(transfer, token)

        # Tampering with 'participations'
        transfer = self.new_transfer()
        token = self.token_manager.issue_token(transfer)
        transfer.participations = ['hugo.boss']

        with self.assertRaises(InvalidToken):
            with freeze(FROZEN_NOW):
                self.token_manager.validate_token(transfer, token)

        # Tampering with 'all_documents'
        transfer = self.new_transfer()
        token = self.token_manager.issue_token(transfer)
        transfer.all_documents = True

        with self.assertRaises(InvalidToken):
            with freeze(FROZEN_NOW):
                self.token_manager.validate_token(transfer, token)

        # Tampering with 'all_participations'
        transfer = self.new_transfer()
        token = self.token_manager.issue_token(transfer)
        transfer.all_participations = False

        with self.assertRaises(InvalidToken):
            with freeze(FROZEN_NOW):
                self.token_manager.validate_token(transfer, token)

    def test_token_must_match_token_on_transfer(self):
        self.login(self.regular_user)

        transfer_a = self.new_transfer()
        transfer_b = self.new_transfer()

        with freeze(FROZEN_NOW):
            token_a = self.token_manager.issue_token(transfer_a)
            token_b = self.token_manager.issue_token(transfer_b)

            # Guard assertions
            self.assertIsNone(self.token_manager.validate_token(transfer_a, token_a))
            self.assertIsNone(self.token_manager.validate_token(transfer_b, token_b))

            with self.assertRaises(InvalidToken):
                self.assertIsNone(self.token_manager.validate_token(transfer_a, token_b))

            with self.assertRaises(InvalidToken):
                self.assertIsNone(self.token_manager.validate_token(transfer_b, token_a))
