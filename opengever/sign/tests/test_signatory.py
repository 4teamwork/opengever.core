from opengever.sign.signatory import Signatories
from opengever.sign.signatory import Signatory
from opengever.testing import IntegrationTestCase


class TestSignatory(IntegrationTestCase):
    def test_can_be_serialized(self):
        signatory = Signatory(email='foo@example.com', userid='regular_user')

        self.assertDictEqual(
            {
                'email': 'foo@example.com',
                'userid': 'regular_user'
            }, signatory.serialize())

    def test_does_not_auto_lookup_userid(self):
        signatory = Signatory(email='foo@example.com')

        self.assertDictEqual(
            {
                'email': 'foo@example.com',
                'userid': '',
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
