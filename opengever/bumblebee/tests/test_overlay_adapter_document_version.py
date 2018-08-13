from opengever.bumblebee.browser.overlay import BumblebeeDocumentVersionOverlay
from opengever.bumblebee.interfaces import IBumblebeeOverlay
from opengever.bumblebee.interfaces import IVersionedContextMarker
from opengever.testing import IntegrationTestCase
from zope.component import getMultiAdapter
from zope.interface import alsoProvides
from zope.interface.verify import verifyClass


class TestAdapterRegisteredProperly(IntegrationTestCase):

    features = (
        'bumblebee',
        )

    def test_get_overlay_adapter_for_documents(self):
        self.login(self.regular_user)
        alsoProvides(self.request, IVersionedContextMarker)
        adapter = getMultiAdapter((self.document, self.request), IBumblebeeOverlay)
        self.assertIsInstance(adapter, BumblebeeDocumentVersionOverlay)

    def test_verify_implemented_interfaces(self):
        verifyClass(IBumblebeeOverlay, BumblebeeDocumentVersionOverlay)
