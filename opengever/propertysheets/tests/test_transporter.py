from datetime import date
from opengever.base.transport import Transporter
from opengever.document.behaviors.customproperties import IDocumentCustomProperties
from opengever.testing import IntegrationTestCase


class TestTransporterWithCustomProperties(IntegrationTestCase):
    """Test that custom properties don't break transporter.

    This guarantees that documents with custom properties can be used in
    tasks and in meeting without causing issues for the transporter.

    They will NOT be transported however, because we can't know what custom
    propertysheets exist on the other side. Fields might be missing, or even
    exist with a different type.

    Also, since document_types and dossier_types are customizable, the other
    side might not even have the same assignment slots available.
    """
    def test_custom_properties_dont_break_transporter(self):
        self.login(self.regular_user)

        properties = {
            "IDocumentMetadata.document_type.question": {
                "textline": u"b\xe4\xe4",
                "iwasremoved": 123,
                "choose": "inolongerexist",
                "birthday": date(2022, 1, 30),
            }
        }

        IDocumentCustomProperties(self.document).custom_properties = properties

        transported_doc = Transporter().transport_from(
            self.empty_dossier, 'plone', '/'.join(self.document.getPhysicalPath()))

        self.assertIsNone(
            IDocumentCustomProperties(transported_doc).custom_properties,
        )
