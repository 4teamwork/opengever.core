from opengever.core.testing import OPENGEVER_FIXTURE
from plone.app.testing import FunctionalTesting
from plone.app.testing import PloneSandboxLayer
from plone.registry.interfaces import IRegistry
from zope.component import getUtility


class DocumentLayer(PloneSandboxLayer):

    defaultBases = (OPENGEVER_FIXTURE, )

    def setUpPloneSite(self, portal):
        # fix registry
        registry = getUtility(IRegistry)
        registry['ftw.tabbedview.interfaces.ITabbedView.batch_size'] = 50


OPENGEVER_DOCUMENT_FIXTURE = DocumentLayer()
OPENGEVER_DOCUMENT_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(OPENGEVER_DOCUMENT_FIXTURE, ),
    name="OpengeverDocument:Integration")
