from opengever.sign.storage import PendingSigningJobStorage
from opengever.testing import IntegrationTestCase


class TestPendingSigningJobStorage(IntegrationTestCase):
    def test_can_store_and_load_data(self):
        self.login(self.regular_user)
        storage = PendingSigningJobStorage(self.document)
        storage.store({'userid': 'foo.bar'})

        self.assertDictEqual({'userid': 'foo.bar'}, storage.load())

    def test_data_is_stored_on_the_context(self):
        self.login(self.regular_user)
        PendingSigningJobStorage(self.subdocument).store({'userid': 'foo.bar'})

        self.assertIsNone(PendingSigningJobStorage(self.document).load())
