from opengever.document.docprops import DocPropertyCollector
from opengever.dossier.interfaces import IDocPropertyProvider
from opengever.dossier.tests import EXPECTED_DOC_PROPERTIES
from opengever.dossier.tests import EXPECTED_DOCUMENT_PROPERTIES
from opengever.dossier.tests import EXPECTED_DOSSIER_PROPERTIES
from opengever.dossier.tests import EXPECTED_PROPOSALDOC_PROPERTIES
from opengever.dossier.tests import EXPECTED_TASKDOC_PROPERTIES
from opengever.dossier.tests import EXPECTED_USER_DOC_PROPERTIES
from opengever.testing import IntegrationTestCase
from zope.component import getAdapter


class TestDocProperties(IntegrationTestCase):

    maxDiff = None

    def test_default_doc_properties_adapter(self):
        self.login(self.regular_user)

        all_properties = DocPropertyCollector(self.document).get_properties()
        self.assertEqual(EXPECTED_DOC_PROPERTIES, all_properties)

    def test_default_doc_properties_adapter_for_taskdocument(self):
        self.login(self.regular_user)

        all_properties = DocPropertyCollector(self.document).get_properties()
        self.assertEqual(EXPECTED_TASKDOC_PROPERTIES, all_properties)

    def test_default_doc_properties_adapter_for_proposaldocument(self):
        self.login(self.regular_user)

        all_properties = DocPropertyCollector(self.document).get_properties()
        self.assertEqual(EXPECTED_PROPOSALDOC_PROPERTIES, all_properties)

    def test_default_document_doc_properties_provider(self):
        self.login(self.regular_user)

        document_adapter = getAdapter(self.document, IDocPropertyProvider)
        self.assertEqual(EXPECTED_DOCUMENT_PROPERTIES,
                         document_adapter.get_properties())

    def test_default_dossier_doc_properties_provider(self):
        self.login(self.regular_user)

        dossier_adapter = getAdapter(self.dossier, IDocPropertyProvider)
        self.assertEqual(EXPECTED_DOSSIER_PROPERTIES,
                         dossier_adapter.get_properties())

    def test_default_member_doc_properties_provider(self):
        self.login(self.regular_user)

        member_adapter = getAdapter(self.regular_user, IDocPropertyProvider)
        self.assertEqual(EXPECTED_USER_DOC_PROPERTIES,
                         member_adapter.get_properties())
