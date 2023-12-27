from ftw.builder import Builder
from ftw.builder import create
from opengever.base.addressblock.interfaces import IAddressBlockData
from opengever.kub.entity import KuBEntity
from opengever.kub.testing import KuBIntegrationTestCase
from opengever.testing import IntegrationTestCase
import requests_mock


class TestOGDSUserAddressExtraction(IntegrationTestCase):

    def test_ogds_user_address_extraction(self):
        user = create(Builder('ogds_user')
                      .id(u'fridolin.mueller')
                      .having(
                          salutation=u'Herr',
                          firstname=u'Fridolin',
                          lastname=u'M\xfcller',
                          address1=u'Murtenstrasse 42',
                          zip_code=u'3008',
                          city=u'Bern',
                          country=u'Schweiz',
        ))

        block = IAddressBlockData(user)

        expected = {
            'salutation': u'Herr',
            'academic_title': None,
            'first_name': u'Fridolin',
            'last_name': u'M\xfcller',

            'org_name': None,

            'street_and_no': u'Murtenstrasse 42',
            'po_box': None,
            'extra_line_1': None,
            'extra_line_2': None,

            'postal_code': u'3008',
            'city': u'Bern',
            'country': u'Schweiz',
        }
        self.assertEqual(expected, block.__dict__)


@requests_mock.Mocker()
class TestKuBEntityAddressExtraction(KuBIntegrationTestCase):

    def mock_entity(self, mocker, data, **kwargs):
        type_id = ':'.join((data['type'], data['id']))
        url = 'http://localhost:8000/api/v2/resolve/{}'.format(type_id)
        mocker.get(url, json=data, **kwargs)
        return type_id

    def test_kub_person_address_extraction(self, mocker):
        self.mock_get_by_id(mocker, self.person_jean)
        entity = KuBEntity(self.person_jean)

        block = IAddressBlockData(entity)

        expected = {
            'salutation': u'Herr',
            'academic_title': u'',
            'first_name': u'Jean',
            'last_name': u'Dupont',

            'org_name': None,

            'street_and_no': u'Teststrasse 43',
            'po_box': u'',
            'extra_line_1': u'',
            'extra_line_2': u'',

            'postal_code': u'9999',
            'city': u'Bern',
            'country': u'Schweiz',
        }
        self.assertEqual(expected, block.__dict__)

    def test_kub_organization_address_extraction(self, mocker):
        self.mock_get_by_id(mocker, self.org_ftw)
        entity = KuBEntity(self.org_ftw)

        block = IAddressBlockData(entity)

        expected = {
            'salutation': None,
            'academic_title': None,
            'first_name': None,
            'last_name': None,

            'org_name': u'4Teamwork',

            'street_and_no': u'Dammweg 9',
            'po_box': u'',
            'extra_line_1': u'c/o John Doe',
            'extra_line_2': u'',

            'postal_code': u'3013',
            'city': u'Bern',
            'country': u'Schweiz',
        }
        self.assertEqual(expected, block.__dict__)

    def test_kub_membership_address_extraction(self, mocker):
        self.mock_get_by_id(mocker, self.memb_jean_ftw)
        entity = KuBEntity(self.memb_jean_ftw)

        # as the organisation primaryAddress is the same as that of the
        # the membership, we modify the data, so that we can make sure the
        # primaryAddress comes from the membership
        entity.data["primaryAddress"]["addressLine2"] = "membership extra 2"

        block = IAddressBlockData(entity)

        expected = {
            'salutation': u'Herr',
            'academic_title': u'',
            'first_name': u'Jean',
            'last_name': u'Dupont',

            'org_name': u'4Teamwork',

            'street_and_no': u'Dammweg 9',
            'po_box': u'',
            'extra_line_1': u'c/o John Doe',
            'extra_line_2': u'membership extra 2',

            'postal_code': u'3013',
            'city': u'Bern',
            'country': u'Schweiz',
        }
        self.assertEqual(expected, block.__dict__)

    def test_kub_po_box_and_street_both_get_extracted(self, mocker):
        data = {
            'id': '123',
            'type': 'person',
            'primaryAddress': {
                'postOfficeBox': 'Postfach',
                'street': 'Dammweg',
                'houseNumber': '9',
            },
        }
        entity = KuBEntity(self.mock_entity(mocker, data))
        block = IAddressBlockData(entity)

        self.assertEqual('Dammweg 9', block.street_and_no)
        self.assertEqual('Postfach', block.po_box)

    def test_kub_extracts_foreign_zip_code_if_no_swiss_zip_code_found(self, mocker):
        data = {
            'id': '123',
            'type': 'person',
            'primaryAddress': {
                'foreignZipCode': '7777',
                'swissZipCode': None,
            },
        }
        entity = KuBEntity(self.mock_entity(mocker, data))
        block = IAddressBlockData(entity)

        self.assertEqual('7777', block.postal_code)

    def test_kub_entity_extraction_handles_missing_primary_address(self, mocker):
        self.mock_get_by_id(mocker, self.person_julie)
        entity = KuBEntity(self.person_julie)

        self.assertIsNone(entity.get('primaryAddress'))

        block = IAddressBlockData(entity)

        expected = {
            'salutation': u'Frau',
            'academic_title': u'',
            'first_name': u'Julie',
            'last_name': u'Dupont',

            'org_name': None,

            'street_and_no': u'',
            'po_box': None,
            'extra_line_1': None,
            'extra_line_2': None,

            'postal_code': None,
            'city': None,
            'country': None,
        }
        self.assertEqual(expected, block.__dict__)
