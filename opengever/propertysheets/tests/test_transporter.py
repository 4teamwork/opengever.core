from opengever.base.transport import Transporter
from opengever.document.behaviors.customproperties import IDocumentCustomProperties
from opengever.testing import IntegrationTestCase


class TestTransporterWithCustomProperties(IntegrationTestCase):
    """Test transporter works with custom properties. This guarantees that
    documents with custom properties can be used in tasks and in meeting.
    """
    def test_custom_properties_are_transported(self):
        self.login(self.regular_user)

        properties = {
            "IDocumentMetadata.document_type.question": {
                "textline": u"b\xe4\xe4",
                "iwasremoved": 123,
                "choose": "inolongerexist",
            }
        }

        IDocumentCustomProperties(self.document).custom_properties = properties

        transported_doc = Transporter().transport_from(
            self.empty_dossier, 'plone', '/'.join(self.document.getPhysicalPath()))

        self.assertEqual(
            properties,
            IDocumentCustomProperties(transported_doc).custom_properties,
        )
