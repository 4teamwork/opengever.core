from datetime import datetime
from mock import patch
from opengever.kub.docprops import KuBEntityDocPropertyProvider
from opengever.kub.entity import KuBEntity
from opengever.kub.testing import KUB_RESPONSES
from opengever.kub.testing import KuBIntegrationTestCase
import requests_mock


@requests_mock.Mocker()
class TestKuBEntityDocPropertyProvider(KuBIntegrationTestCase):

    def test_docproperties_for_kub_person(self, mocker):
        self.mock_get_by_id(mocker, self.person_jean)
        entity = KuBEntity(self.person_jean)
        properties = KuBEntityDocPropertyProvider(entity).get_properties()
        self.assertDictEqual(
            {'ogg.address.block': u'Herr\nJean Dupont\nTeststrasse 43\n9999 Bern',
             'ogg.address.city': u'Bern',
             'ogg.address.country': u'Schweiz',
             'ogg.address.extra_line_1': u'',
             'ogg.address.extra_line_2': u'',
             'ogg.address.street': u'Teststrasse 43',
             'ogg.address.zip_code': u'9999',
             'ogg.contact.description': u'',
             'ogg.contact.title': u'Dupont Jean',
             'ogg.email.address': u'Jean.dupon@example.com',
             'ogg.person.academic_title': u'',
             'ogg.person.date_of_birth': datetime(1992, 5, 15, 0, 0),
             'ogg.person.firstname': u'Jean',
             'ogg.person.lastname': u'Dupont',
             'ogg.person.salutation': u'Herr',
             'ogg.person.country': u'schweiz',
             'ogg.person.sex': None,
             'ogg.phone.number': u'666 666 66 66',
             'ogg.url.url': None},
            properties)

        self.mock_get_by_id(mocker, self.person_julie)
        entity = KuBEntity(self.person_julie)
        properties = KuBEntityDocPropertyProvider(entity).get_properties()
        self.assertDictEqual(
            {'ogg.address.block': u'Frau\nJulie Dupont',
             'ogg.address.city': None,
             'ogg.address.country': None,
             'ogg.address.extra_line_1': None,
             'ogg.address.extra_line_2': None,
             'ogg.address.street': u'',
             'ogg.address.zip_code': None,
             'ogg.contact.description': u'',
             'ogg.contact.title': u'Dupont Julie',
             'ogg.email.address': None,
             'ogg.person.academic_title': u'',
             'ogg.person.date_of_birth': None,
             'ogg.person.firstname': u'Julie',
             'ogg.person.lastname': u'Dupont',
             'ogg.person.country': u'',
             'ogg.person.salutation': u'Frau',
             'ogg.person.sex': 2,
             'ogg.phone.number': None,
             'ogg.url.url': None},
            properties)

    @patch('opengever.kub.docprops.get_additional_doc_properties', return_value=['sorgerecht',])
    def test_docproperties_for_kub_person_with_custom_fields(self, mocker, mock_get_additional_doc_properties):
        self.mock_get_by_id(mocker, self.person_jean)
        entity = KuBEntity(self.person_jean)
        properties = KuBEntityDocPropertyProvider(entity).get_properties()

        self.assertIn('ogg.person.sorgerecht', properties)
        self.assertEqual(properties['ogg.person.sorgerecht'], "Geteilt")

    @patch('opengever.kub.docprops.get_additional_doc_properties', return_value=['ort'])
    def test_docproperties_for_kub_organization_with_custom_fields(self, mocker, mock_get_additional_doc_properties):
        self.mock_get_by_id(mocker, self.org_ftw)
        entity = KuBEntity(self.org_ftw)

        properties = KuBEntityDocPropertyProvider(entity).get_properties()

        self.assertIn('ogg.organization.ort', properties)
        self.assertEqual(properties['ogg.organization.ort'], "Bern")

    def test_zip_code_docproperty_is_swiss_or_foreign_zip_code(self, mocker):
        url = self.mock_get_by_id(mocker, self.person_jean)
        entity = KuBEntity(self.person_jean)
        properties = KuBEntityDocPropertyProvider(entity).get_properties()
        self.assertEqual(u'9999', properties['ogg.address.zip_code'])

        KUB_RESPONSES[url]['primaryAddress']['swissZipCode'] = ""
        KUB_RESPONSES[url]['primaryAddress']['foreignZipCode'] = "12345"
        self.mock_get_by_id(mocker, self.person_jean)
        entity = KuBEntity(self.person_jean)
        properties = KuBEntityDocPropertyProvider(entity).get_properties()
        self.assertEqual(u'12345', properties['ogg.address.zip_code'])

    def test_docproperties_for_kub_organization(self, mocker):
        self.mock_get_by_id(mocker, self.org_ftw)
        entity = KuBEntity(self.org_ftw)
        properties = KuBEntityDocPropertyProvider(entity).get_properties()
        self.assertDictEqual(
            {'ogg.address.block': u'4Teamwork\nc/o John Doe\nDammweg 9\n3013 Bern',
             'ogg.address.city': u'Bern',
             'ogg.address.country': u'Schweiz',
             'ogg.address.extra_line_1': u'c/o John Doe',
             'ogg.address.extra_line_2': u'',
             'ogg.address.street': u'Dammweg 9',
             'ogg.address.zip_code': u'3013',
             'ogg.contact.description': u'Web application specialist',
             'ogg.contact.title': u'4Teamwork',
             'ogg.email.address': None,
             'ogg.organization.name': u'4Teamwork',
             'ogg.organization.phone.number': u'111 111 11 11',
             'ogg.phone.number': u'111 111 11 11',
             'ogg.url.url': None},
            properties)

    def test_docproperties_for_kub_membership(self, mocker):
        self.mock_get_by_id(mocker, self.memb_jean_ftw)
        entity = KuBEntity(self.memb_jean_ftw)
        properties = KuBEntityDocPropertyProvider(entity).get_properties()
        self.assertDictEqual(
            {'ogg.address.block': u'4Teamwork\nHerr Jean Dupont\nc/o John Doe\nDammweg 9\n3013 Bern',
             'ogg.address.city': u'Bern',
             'ogg.address.country': u'Schweiz',
             'ogg.address.extra_line_1': u'c/o John Doe',
             'ogg.address.extra_line_2': u'',
             'ogg.address.street': u'Dammweg 9',
             'ogg.address.zip_code': u'3013',
             'ogg.contact.description': u'',
             'ogg.contact.title': u'Dupont Jean - 4Teamwork (CEO)',
             'ogg.email.address': u'Jean.dupon@example.com',
             'ogg.organization.name': u'4Teamwork',
             'ogg.organization.phone.number': u'111 111 11 11',
             'ogg.orgrole.department': u'',
             'ogg.orgrole.description': u'',
             'ogg.orgrole.function': u'CEO',
             'ogg.person.academic_title': u'',
             'ogg.person.date_of_birth': datetime(1992, 5, 15, 0, 0),
             'ogg.person.firstname': u'Jean',
             'ogg.person.lastname': u'Dupont',
             'ogg.person.salutation': u'Herr',
             'ogg.person.country': None,
             'ogg.person.sex': None,
             'ogg.phone.number': u'666 666 66 66',
             'ogg.url.url': None},
            properties)
