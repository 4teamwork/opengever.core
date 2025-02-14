from opengever.sign.pending_editor import PendingEditor
from opengever.sign.pending_editor import PendingEditors
from opengever.testing import IntegrationTestCase


class TestPendingEditor(IntegrationTestCase):
    def test_can_be_serialized(self):
        signer = PendingEditor(email='foo@example.com')

        self.assertDictEqual(
            {
                'email': 'foo@example.com',
                'userid': 'regular_user'
            }, signer.serialize())

    def test_can_be_converted_from_json_object_to_json_object(self):
        pending_editor = PendingEditor(email='foo@example.com')

        self.assertTrue(
            pending_editor == PendingEditor.from_json_object(pending_editor.to_json_object()))


class TestPendingEditors(IntegrationTestCase):
    def test_can_be_serialized(self):
        container = PendingEditors()
        signer1 = PendingEditor(email='foo@example.com')
        signer2 = PendingEditor(email='bar@example.com')

        container.append(signer1)
        container.append(signer2)

        self.assertEqual(2, len(container.serialize()))
        self.assertItemsEqual([signer2.email, signer1.email],
                              [item.get('email') for item in container.serialize()] )

    def test_can_be_converted_from_json_object_to_json_object(self):
        container = PendingEditors([
            PendingEditor(email='foo@example.com'),
            PendingEditor(email='foo@example.com')
        ])

        self.assertTrue(
            container == PendingEditors.from_json_object(container.to_json_object()))

    def test_can_be_created_from_a_list_of_emails(self):
        container = PendingEditors.from_emails(['foo@example.com', 'bar@example.com'])

        self.assertEqual(2, len(container))
        self.assertTrue(isinstance(container[0], PendingEditor))
        self.assertItemsEqual(['foo@example.com', 'bar@example.com'],
                              [item.get('email') for item in container.serialize()])
