from ftw.builder import Builder
from ftw.builder import create
from opengever.dossier.tests import OGDS_USER_ATTRIBUTES
from opengever.testing import FunctionalTestCase


class TestContactDocPropertyProvider(FunctionalTestCase):

    use_default_fixture = False
    maxDiff = None

    def setUp(self):
        super(TestContactDocPropertyProvider, self).setUp()

        user, org_unit, admin_unit = create(
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
