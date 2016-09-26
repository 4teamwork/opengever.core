from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from opengever.dossier.interfaces import IDocProperties
from opengever.dossier.interfaces import IDocPropertyProvider
from opengever.dossier.tests import EXPECTED_DOC_PROPERTIES
from opengever.dossier.tests import EXPECTED_DOCUMENT_PROPERTIES
from opengever.dossier.tests import EXPECTED_DOSSIER_PROPERTIES
from opengever.dossier.tests import EXPECTED_USER_DOC_PROPERTIES
from opengever.dossier.tests import OGDS_USER_ATTRIBUTES
from opengever.testing import FunctionalTestCase
from plone.app.testing import TEST_USER_ID
from zope.component import getAdapter
from zope.component import getMultiAdapter


class TestDocProperties(FunctionalTestCase):

    use_default_fixture = False

    def setUp(self):
        super(TestDocProperties, self).setUp()
        user, org_unit, admin_unit = create(
            Builder('fixture')
            .with_all_unit_setup()
            .with_user(**OGDS_USER_ATTRIBUTES))

        self.dossier = create(Builder('dossier').titled(u'My dossier'))
        self.document = create(
            Builder('document')
            .within(self.dossier)
            .titled("My Document")
            .having(document_date=datetime(2010, 1, 3),
                    document_author=TEST_USER_ID,
                    receipt_date=datetime(2010, 1, 3),
                    delivery_date=datetime(2010, 1, 3))
            .with_asset_file('with_gever_properties.docx'))

        self.member = self.login()

    def test_default_doc_properties_adapter(self):
        docprops = getMultiAdapter(
            (self.document, self.portal.REQUEST), IDocProperties)
        all_properties = docprops.get_properties()
        self.assertItemsEqual(EXPECTED_DOC_PROPERTIES, all_properties)

    def test_default_dossier_doc_properties_provider(self):
        dossier_adapter = getAdapter(self.dossier, IDocPropertyProvider)
        self.assertItemsEqual(EXPECTED_DOSSIER_PROPERTIES,
                              dossier_adapter.get_properties())

    def test_default_member_doc_properties_provider(self):
        member_adapter = getAdapter(self.member, IDocPropertyProvider)
        self.assertItemsEqual(EXPECTED_USER_DOC_PROPERTIES,
                              member_adapter.get_properties())

    def test_default_document_doc_properties_provider(self):
        document_adapter = getAdapter(self.document, IDocPropertyProvider)
        self.assertItemsEqual(EXPECTED_DOCUMENT_PROPERTIES,
                              document_adapter.get_properties())
