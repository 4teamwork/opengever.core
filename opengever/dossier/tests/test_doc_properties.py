from ftw.builder import Builder
from ftw.builder import create
from opengever.dossier.interfaces import IDocProperties
from opengever.dossier.interfaces import IDocPropertyProvider
from opengever.dossier.tests import EXPECTED_USER_DOC_PROPERTIES
from opengever.dossier.tests import OGDS_USER_ATTRIBUTES
from opengever.testing import FunctionalTestCase
from zope.component import getAdapter
from zope.component import getMultiAdapter


class TestDocProperties(FunctionalTestCase):

    expected_dossier_properties = {
        'Dossier.ReferenceNumber': 'Client1 / 1',
        'Dossier.Title': 'My dossier',
    }
    expected_document_properties = {
        'Document.ReferenceNumber': 'Client1 / 1 / 1',
        'Document.SequenceNumber': '1',
    }

    use_default_fixture = False

    def setUp(self):
        super(TestDocProperties, self).setUp()
        user, org_unit, admin_unit = create(
            Builder('fixture')
            .with_all_unit_setup()
            .with_user(**OGDS_USER_ATTRIBUTES))

        self.dossier = create(Builder('dossier').titled(u'My dossier'))
        self.document = create(Builder('document').within(self.dossier))
        self.member = self.login()

    def test_default_doc_properties_adapter(self):
        docprops = getMultiAdapter(
            (self.document, self.portal.REQUEST), IDocProperties)
        properties = docprops.get_properties()
        self.assertItemsEqual(
            dict(EXPECTED_USER_DOC_PROPERTIES.items() +
                 self.expected_dossier_properties.items() +
                 self.expected_document_properties.items()),
            properties
        )

    def test_default_dossier_doc_properties_provider(self):
        dossier_adapter = getAdapter(self.dossier, IDocPropertyProvider)
        self.assertEqual(self.expected_dossier_properties,
                         dossier_adapter.get_properties())

    def test_default_member_doc_properties_provider(self):
        member_adapter = getAdapter(self.member, IDocPropertyProvider)
        self.assertItemsEqual(EXPECTED_USER_DOC_PROPERTIES,
                              member_adapter.get_properties())
