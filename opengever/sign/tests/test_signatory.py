from opengever.sign.signatory import Signatories
from opengever.sign.signatory import Signatory
from opengever.testing import IntegrationTestCase


class TestSignatory(IntegrationTestCase):
    def test_can_be_serialized(self):
        signatory = Signatory(email='foo@example.com',
                              userid='regular_user',
                              signed_at='2025-01-28T15:00:00.000Z')

        self.assertDictEqual(
            {
                'email': 'foo@example.com',
                'userid': 'regular_user',
                'signed_at': '2025-01-28T15:00:00.000Z',
            }, signatory.serialize())

    def test_can_be_converted_from_json_object_to_json_object(self):
        signatory = Signatory(email='foo@example.com',
                              userid='regular_user',
                              signed_at='2025-01-28T15:00:00.000Z')

        self.assertTrue(
            signatory == Signatory.from_json_object(signatory.to_json_object()))

    def test_does_not_auto_lookup_userid(self):
        signatory = Signatory(email='foo@example.com')

        self.assertDictEqual(
            {
                'email': 'foo@example.com',
                'userid': '',
                'signed_at': None,
            }, signatory.serialize())


class TestSignatories(IntegrationTestCase):
    def test_can_be_serialized(self):
        container = Signatories()
        signatory1 = Signatory(email='foo@example.com')
        signatory2 = Signatory(email='bar@example.com')

        container.append(signatory1)
        container.append(signatory2)

        self.assertEqual(2, len(container.serialize()))
        self.assertItemsEqual([signatory2.email, signatory1.email],
                              [item.get('email') for item in container.serialize()])

    def test_can_be_converted_from_json_object_to_json_object(self):
        container = Signatories([
            Signatory(email='foo@example.com'),
            Signatory(email='foo@example.com')
        ])

        self.assertTrue(
            container == Signatories.from_json_object(container.to_json_object()))
