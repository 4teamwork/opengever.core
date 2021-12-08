from opengever.kub.docprops import KuBEntityDocPropertyProvider
from opengever.kub.entity import KuBEntity
from opengever.kub.testing import KuBIntegrationTestCase
import requests_mock


@requests_mock.Mocker()
class TestKuBEntityDocPropertyProvider(KuBIntegrationTestCase):

    def test_docproperties_for_kub_person(self, mocker):
        self.mock_get_full_entity_by_id(mocker, self.person_julie)
        entity = KuBEntity(self.person_julie, full=True)
        properties = KuBEntityDocPropertyProvider(entity).get_properties()
        self.assertDictEqual(
            {'ogg.address.city': None,
             'ogg.address.country': None,
             'ogg.address.street': None,
             'ogg.address.zip_code': None,
             'ogg.contact.description': u'',
             'ogg.contact.title': None,
             'ogg.email.address': None,
             'ogg.person.academic_title': u'',
             'ogg.person.firstname': u'Julie',
             'ogg.person.lastname': u'Dupont',
             'ogg.person.salutation': u'Frau',
             'ogg.phone.number': None,
             'ogg.url.url': None},
            properties)

    def test_docproperties_for_kub_organization(self, mocker):
        self.mock_get_full_entity_by_id(mocker, self.org_ftw)
        entity = KuBEntity(self.org_ftw, full=True)
        properties = KuBEntityDocPropertyProvider(entity).get_properties()
        self.assertDictEqual(
            {'ogg.address.city': None,
             'ogg.address.country': None,
             'ogg.address.street': None,
             'ogg.address.zip_code': None,
             'ogg.contact.description': u'Web application specialist',
             'ogg.contact.title': None,
             'ogg.email.address': None,
             'ogg.organization.name': u'4Teamwork',
             'ogg.phone.number': None,
             'ogg.url.url': None},
            properties)

    def test_docproperties_for_kub_membership(self, mocker):
        self.mock_get_full_entity_by_id(mocker, self.memb_jean_ftw)
        self.mock_get_full_entity_by_id(mocker, self.org_ftw)
        self.mock_get_full_entity_by_id(mocker, self.person_jean)
        entity = KuBEntity(self.memb_jean_ftw, full=True)
        properties = KuBEntityDocPropertyProvider(entity).get_properties()
        self.assertDictEqual(
            {'ogg.address.city': None,
             'ogg.address.country': None,
             'ogg.address.street': None,
             'ogg.address.zip_code': None,
             'ogg.contact.description': u'',
             'ogg.contact.title': None,
             'ogg.email.address': u'Jean.dupon@example.com',
             'ogg.organization.name': u'4Teamwork',
             'ogg.orgrole.department': u'',
             'ogg.orgrole.description': u'',
             'ogg.orgrole.function': u'CEO',
             'ogg.person.academic_title': u'',
             'ogg.person.firstname': u'Jean',
             'ogg.person.lastname': u'Dupont',
             'ogg.person.salutation': u'Herr',
             'ogg.phone.number': u'666 666 66 66',
             'ogg.url.url': None},
            properties)
