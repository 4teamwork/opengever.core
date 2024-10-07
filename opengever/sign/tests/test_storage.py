from opengever.sign.signed_version import SignedVersion
from opengever.sign.storage import PendingSigningJobStorage
from opengever.sign.storage import SignedVersionsStorage
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


class TestSignedVersionStorage(IntegrationTestCase):
    def test_can_load_and_persist_data(self):
        self.login(self.regular_user)

        SignedVersionsStorage(self.document).load().add_signed_version(SignedVersion(id_=1, version=5))
        SignedVersionsStorage(self.document).load().add_signed_version(SignedVersion(id_=2, version=6))

        signed_versions = SignedVersionsStorage(self.document).load().serialize()
        self.assertEqual([5, 6], signed_versions.keys())
