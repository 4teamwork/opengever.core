from datetime import datetime
from ftw.testing import freeze
from opengever.sign.pending_signature import PendingSignature
from opengever.sign.pending_signature import PendingSignatures
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
                                  job_id='0',
                                  redirect_url='').created
            )

    def test_can_be_serialized(self):
        self.login(self.regular_user)

        metadata = PendingSigningJob(
            created=FROZEN_NOW,
            userid='foo.bar',
            version=1,
            editors=['bar.foo@example.com'],
            signatures=PendingSignatures([PendingSignature(email="foo@example.com")]),
            job_id='1',
            redirect_url='redirect@example.com',
            invite_url='redirect@example.com/invite')

        self.assertDictEqual(
            {
                'created': u'2024-02-18T15:45:00',
                'userid': 'foo.bar',
                'version': 1,
                'editors': [
                    {
                        'email': 'bar.foo@example.com',
                        'userid': '',
                    }
                ],
                'signatures': [
                    {
                        'email': 'foo@example.com',
                        'signed_at': '',
                        'status': '',
                        'userid': 'regular_user'
                    }
                ],
                'job_id': '1',
                'redirect_url': 'redirect@example.com',
                'invite_url': 'redirect@example.com/invite',
            }, metadata.serialize())

    def test_can_be_converted_to_a_signed_version(self):
        self.login(self.regular_user)

        PENDING_JOB_CREATION = datetime(2024, 2, 18, 15, 45)
        SIGNED_VERSION_CREATION = datetime(2024, 3, 18, 15, 45)

        pending_signing_job = PendingSigningJob(
            created=PENDING_JOB_CREATION,
            userid='foo.bar',
            version=1,
            signatures=PendingSignatures([
                PendingSignature(
                    email="bar@example.com",
                    signed_at="2025-01-28T15:00:00.000Z",
                ),
                PendingSignature(
                    email="nicole.kohler@gever.local",
                    signed_at="2025-01-30T15:00:00.000Z",
                )
            ]),
            job_id='1',
            redirect_url='redirect@example.com')

        with freeze(SIGNED_VERSION_CREATION):
            data = pending_signing_job.to_signed_version().serialize()

        self.assertDictEqual(
            {
                'id': data.get('id'),
                'created': '2024-03-18T15:45:00',
                'signatories': [
                    {
                        'email': 'bar@example.com',
                        'userid': '',
                        'signed_at': '2025-01-28T15:00:00.000Z'
                    },
                    {
                        'email': 'nicole.kohler@gever.local',
                        'userid': 'nicole.kohler',
                        'signed_at': '2025-01-30T15:00:00.000Z'
                    }
                ],
                'version': 2
            }, data)

    def test_can_update_editors(self):
        self.login(self.regular_user)

        pending_signing_job = PendingSigningJob(editors=[])

        self.assertItemsEqual([], pending_signing_job.serialize().get('editors'))

        pending_signing_job.update(editors=['bar1@example.com'])

        self.assertItemsEqual(
            [{u'userid': u'', u'email': u'bar1@example.com'}],
            pending_signing_job.serialize().get('editors'))

    def test_can_update_signatures(self):
        self.login(self.regular_user)

        pending_signing_job = PendingSigningJob(signatures=PendingSignatures())

        self.assertItemsEqual([], pending_signing_job.serialize().get('signatures'))

        pending_signing_job.update(signatures=['foo1@example.com'])

        self.assertItemsEqual([], pending_signing_job.serialize().get('signatures'))

        pending_signing_job.update(signatures=PendingSignatures([PendingSignature(email="foo@example.com")]))

        self.assertItemsEqual([
            {
                'status': '',
                'signed_at': '',
                'userid': 'regular_user',
                'email': 'foo@example.com'
            }
        ], pending_signing_job.serialize().get('signatures'))
