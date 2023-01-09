from ftw.builder import Builder
from ftw.builder import create
from opengever.contact.ogdsuser import OgdsUserToContactAdapter
from opengever.dossier.tests import OGDS_USER_ATTRIBUTES
from opengever.testing import FunctionalTestCase


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

    def test_ogds_user_adapter_doc_property_provider(self):
        provider = OgdsUserToContactAdapter(self.user).get_doc_property_provider()

        expected_ogds_user_properties = {
            'ogg.recipient.contact.title': u'M\xfcller Peter',
            'ogg.recipient.contact.description': u'nix',
            'ogg.recipient.person.salutation': 'Prof. Dr.',
            'ogg.recipient.person.academic_title': '',
            'ogg.recipient.person.firstname': 'Peter',
            'ogg.recipient.person.lastname': u'M\xfcller',
        }
        self.assertItemsEqual(expected_ogds_user_properties,
                              provider.get_properties(prefix='recipient'))
