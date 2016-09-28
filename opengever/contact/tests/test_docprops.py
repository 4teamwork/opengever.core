from ftw.builder import Builder
from ftw.builder import create
from opengever.contact.ogdsuser import OgdsUserAdapter
from opengever.dossier.tests import OGDS_USER_ATTRIBUTES
from opengever.testing import FunctionalTestCase
from plone.app.testing import TEST_USER_ID


class TestContactDocPropertyProvider(FunctionalTestCase):

    use_default_fixture = False
    maxDiff = None

    def setUp(self):
        super(TestContactDocPropertyProvider, self).setUp()

        self.user, org_unit, admin_unit = create(
            Builder('fixture')
            .with_all_unit_setup()
            .with_user(**OGDS_USER_ATTRIBUTES))

        self.set_docproperty_export_enabled(True)

    def tearDown(self):
        self.set_docproperty_export_enabled(False)
        super(TestContactDocPropertyProvider, self).tearDown()

    def test_person_doc_property_provider(self):
        peter = create(Builder('person')
                       .having(firstname=u'Peter',
                               lastname=u'M\xfcller',
                               salutation='Herr',
                               academic_title='Prof. Dr.',
                               description='blablabla'))
        provider = peter.get_doc_property_provider(prefix='recipient')
        expected_person_properties = {
            'ogg.recipient.contact.title': u'M\xfcller Peter',
            'ogg.recipient.contact.description': 'blablabla',
            'ogg.recipient.person.salutation': 'Herr',
            'ogg.recipient.person.academic_title': 'Prof. Dr.',
            'ogg.recipient.person.firstname': 'Peter',
            'ogg.recipient.person.lastname': u'M\xfcller',
        }
        self.assertItemsEqual(expected_person_properties,
                              provider.get_properties())

    def test_organization_doc_property_provider(self):
        organization = create(Builder('organization')
                              .having(name=u'ACME corp.',
                                      description='blablabla'))
        provider = organization.get_doc_property_provider(prefix='recipient')
        expected_organization_properties = {
            'ogg.recipient.contact.title': u'ACME corp.',
            'ogg.recipient.contact.description': 'blablabla',
            'ogg.recipient.organization.name': u'ACME corp.',
        }
        self.assertItemsEqual(expected_organization_properties,
                              provider.get_properties())

    def test_org_role_doc_property_provider(self):
        peter = create(Builder('person')
                       .having(firstname=u'Peter',
                               lastname=u'M\xfcller',
                               salutation='Herr',
                               academic_title='Prof. Dr.',
                               description='blablabla'))
        organization = create(Builder('organization').having(name=u'Foo'))
        org_role = create(Builder('org_role')
                          .having(organization=organization,
                                  person=peter,
                                  function=u'M\xe4dchen f\xfcr alles',
                                  description='blub'))
        provider = org_role.get_doc_property_provider(prefix='recipient')
        expected_orgrole_properties = {
            'ogg.recipient.orgrole.function': u'M\xe4dchen f\xfcr alles',
            'ogg.recipient.orgrole.description': 'blub',
            'ogg.recipient.contact.title': u'M\xfcller Peter',
            'ogg.recipient.contact.description': 'blablabla',
            'ogg.recipient.person.salutation': 'Herr',
            'ogg.recipient.person.academic_title': 'Prof. Dr.',
            'ogg.recipient.person.firstname': 'Peter',
            'ogg.recipient.person.lastname': u'M\xfcller',
        }
        self.assertItemsEqual(expected_orgrole_properties,
                              provider.get_properties())

    def test_ogds_user_adapter_doc_property_provider(self):
        provider = OgdsUserAdapter(self.user).get_doc_property_provider(
            prefix='recipient')

        expected_ogds_user_properties = {
            'ogg.recipient.contact.title': u'M\xfcller Peter',
            'ogg.recipient.person.salutation': 'Prof. Dr.',
            'ogg.recipient.person.firstname': 'Peter',
            'ogg.recipient.person.lastname': u'M\xfcller',
        }
        self.assertItemsEqual(expected_ogds_user_properties,
                              provider.get_properties())
