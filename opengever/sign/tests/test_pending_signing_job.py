from datetime import datetime
from ftw.testing import freeze
from opengever.sign.pending_signing_job import PendingSigningJob
from opengever.testing import IntegrationTestCase


FROZEN_NOW = datetime(2024, 2, 18, 15, 45)


class TestPendingSigningJob(IntegrationTestCase):
    def test_create_function_sets_the_creation_date(self):
        with freeze(FROZEN_NOW):
            self.assertEqual(
                FROZEN_NOW,
                PendingSigningJob(userid='foo.bar',
                                  version=0,
                                  signers=[],
                                  job_id='0',
                                  redirect_url='').created
            )

    def test_can_be_serialized(self):
        self.login(self.regular_user)

        metadata = PendingSigningJob(
            created=FROZEN_NOW,
            userid='foo.bar',
            version=1,
            signers=['foo.bar@example.com'],
            job_id='1',
            redirect_url='redirect@example.com')

        self.assertDictEqual(
            {
                'created': u'2024-02-18T15:45:00',
                'userid': 'foo.bar',
                'version': 1,
                'signers': [
                    {
                        'email': 'foo.bar@example.com',
                        'userid': '',
                    }
                ],
                'job_id': '1',
                'redirect_url': 'redirect@example.com'
            }, metadata.serialize())
