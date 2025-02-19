from opengever.sign.pending_signature import PendingSignature
from opengever.sign.pending_signature import PendingSignatures
from opengever.testing import IntegrationTestCase


class TestPendingSignature(IntegrationTestCase):
    def test_can_be_serialized(self):
        signature = PendingSignature(email='foo@example.com',
                                     status="signed",
                                     signed_at='2025-01-28T15:00:00.000Z')

        self.assertDictEqual(
            {
                'email': 'foo@example.com',
                'signed_at': '2025-01-28T15:00:00.000Z',
                'status': 'signed',
                'userid': 'regular_user'
            }, signature.serialize())

    def test_can_be_converted_to_a_signatory(self):
        signature = PendingSignature(email='foo@example.com',
                                     status="signed",
                                     signed_at='2025-01-28T15:00:00.000Z')

        self.assertDictEqual(
            {
                'email': 'foo@example.com',
                'userid': 'regular_user',
                'signed_at': '2025-01-28T15:00:00.000Z',
            }, signature.to_signatory().serialize())


class TestPendingSignatures(IntegrationTestCase):
    def test_can_be_serialized(self):
        container = PendingSignatures()
        signature1 = PendingSignature(email='foo@example.com')
        signature2 = PendingSignature(email='bar@example.com')

        container.append(signature1)
        container.append(signature2)

        self.assertEqual(2, len(container.serialize()))
        self.assertItemsEqual([signature2.email, signature1.email],
                              [item.get('email') for item in container.serialize()])

    def test_can_be_converted_to_signatories(self):
        container = PendingSignatures()

        container.append(PendingSignature())
        container.append(PendingSignature())

        self.assertEqual(2, len(container.to_signatories()))
