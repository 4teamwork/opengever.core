from opengever.sign.pending_signer import PendingSigner
from opengever.sign.pending_signer import PendingSigners
from opengever.testing import IntegrationTestCase


class TestPendingSigner(IntegrationTestCase):
    def test_can_be_serialized(self):
        signer = PendingSigner(email='foo@example.com')

        self.assertDictEqual(
            {
                'email': 'foo@example.com',
                'userid': 'regular_user'
            }, signer.serialize())


class TestPendingSigners(IntegrationTestCase):
    def test_can_be_serialized(self):
        container = PendingSigners()
        signer1 = PendingSigner(email='foo@example.com')
        signer2 = PendingSigner(email='bar@example.com')

        container.append(signer1)
        container.append(signer2)

        self.assertEqual(2, len(container.serialize()))
        self.assertItemsEqual([signer2.email, signer1.email],
                              [item.get('email') for item in container.serialize()])
