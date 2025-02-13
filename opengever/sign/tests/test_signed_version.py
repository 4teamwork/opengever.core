from datetime import datetime
from ftw.testing import freeze
from opengever.sign.signatory import Signatories
from opengever.sign.signatory import Signatory
from opengever.sign.signed_version import SignedVersion
from opengever.sign.signed_version import SignedVersions
from opengever.testing import IntegrationTestCase


FROZEN_NOW = datetime(2024, 2, 18, 15, 45)


class TestSignedVersion(IntegrationTestCase):
    def test_constructor_sets_the_creation_date(self):
        with freeze(FROZEN_NOW):
            self.assertEqual(FROZEN_NOW, SignedVersion().created)

    def test_constructor_sets_a_new_uuid(self):
        self.assertNotEqual(SignedVersion().id_, SignedVersion().id_)

    def test_can_be_serialized(self):
        signatories = Signatories([Signatory(email='foo@example.com',
                                             signed_at='2025-01-28T15:00:00.000Z')])

        signed_version = SignedVersion(
            id_="1",
            created=FROZEN_NOW,
            signatories=signatories,
            version=1)

        self.assertDictEqual(
            {
                'id': signed_version.id_,
                'created': u'2024-02-18T15:45:00',
                'signatories': [
                    {
                        'email': 'foo@example.com',
                        'userid': '',
                        'signed_at': '2025-01-28T15:00:00.000Z',
                    }
                ],
                'version': 1
            }, signed_version.serialize())


class TestSignedVersions(IntegrationTestCase):
    def test_can_be_serialized(self):
        signatories = Signatories([Signatory(email='foo@example.com',
                                             signed_at='2025-01-28T15:00:00.000Z')])

        signed_version_1 = SignedVersion(
            id_=u"1",
            created=FROZEN_NOW,
            signatories=signatories,
            version=1)

        signed_version_2 = SignedVersion(
            id_=u"1",
            created=FROZEN_NOW,
            version=2)

        container = SignedVersions()
        container.add_signed_version(signed_version_1)
        container.add_signed_version(signed_version_2)

        self.assertDictEqual({
            1: {
                u'created': u'2024-02-18T15:45:00',
                u'id': u'1',
                u'signatories': [
                    {
                        u'email': u'foo@example.com',
                        u'userid': u'',
                        u'signed_at': u'2025-01-28T15:00:00.000Z',
                    }
                ],
                u'version': 1
            },
            2: {
                u'created': u'2024-02-18T15:45:00',
                u'id': u'1',
                u'signatories': [],
                u'version': 2
            }
        }, container.serialize())
