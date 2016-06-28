from ftw.builder import Builder
from ftw.builder import create
from opengever.bumblebee.browser.overlay import BumblebeeDocumentVersionOverlay
from opengever.bumblebee.interfaces import IBumblebeeOverlay
from opengever.bumblebee.interfaces import IVersionedContextMarker
from opengever.core.testing import OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER
from opengever.testing import FunctionalTestCase
from zope.component import getMultiAdapter
from zope.interface import alsoProvides
from zope.interface.verify import verifyClass


class TestAdapterRegisteredProperly(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER

    def test_get_overlay_adapter_for_documents(self):
        dossier = create(Builder('dossier'))
        document = create(Builder('document').within(dossier))

        alsoProvides(self.request, IVersionedContextMarker)

        adapter = getMultiAdapter((document, self.request), IBumblebeeOverlay)

        self.assertIsInstance(adapter, BumblebeeDocumentVersionOverlay)

    def test_verify_implemented_interfaces(self):
        verifyClass(IBumblebeeOverlay, BumblebeeDocumentVersionOverlay)
