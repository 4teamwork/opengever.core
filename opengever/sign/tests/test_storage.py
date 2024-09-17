from datetime import datetime
from ftw.testing import freeze
from opengever.sign.storage import MetadataStorage
from opengever.testing import IntegrationTestCase


FROZEN_NOW = datetime(2024, 2, 18, 15, 45)


class TestMetadataStorage(IntegrationTestCase):
    def test_can_store_metadata(self):
        self.login(self.regular_user)
        storage = MetadataStorage(self.document)

        with freeze(FROZEN_NOW):
            storage.store(
                userid='foo.bar',
                version=1,
                signers=['foo.bar@example.com'],
                job_id='123',
                redirect_url='http://example.com/sign-service'
            )

        self.assertDictEqual(
            {
                'created': FROZEN_NOW,
                'job_id': '123',
                'redirect_url': 'http://example.com/sign-service',
                'signers': ['foo.bar@example.com'],
                'userid': 'foo.bar',
                'version': 1
            },
            storage.read())
