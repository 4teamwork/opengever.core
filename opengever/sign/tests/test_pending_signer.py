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

    def test_can_be_converted_to_a_signatory(self):
        signer = PendingSigner(email='foo@example.com')

        self.assertDictEqual(
            {
                'email': 'foo@example.com',
                'userid': 'regular_user',
            }, signer.to_signatory().serialize())


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

    def test_can_be_converted_to_signatories(self):
        container = PendingSigners()

        container.append(PendingSigner())
        container.append(PendingSigner())

        self.assertEqual(2, len(container.to_signatories()))

    def test_can_be_created_from_a_list_of_emails(self):
        container = PendingSigners.from_emails(['foo@example.com', 'bar@example.com'])

        self.assertEqual(2, len(container))
        self.assertTrue(isinstance(container[0], PendingSigner))
        self.assertItemsEqual(['foo@example.com', 'bar@example.com'],
                              [item.get('email') for item in container.serialize()])
