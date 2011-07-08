from ftw.tabbedview.interfaces import ITabbedView
from plone.registry.interfaces import IRegistry
from Products.PloneTestCase import ptc
from zope.component import getUtility
import collective.testcaselayer.ptc

ptc.setupPloneSite()


class IntegrationTestLayer(collective.testcaselayer.ptc.BasePTCLayer):

    def afterSetUp(self):
        # Install the opengever.task product
        self.addProfile('opengever.task:default')

        self.addProfile('ftw.tabbedview:default')
        self.addProfile('opengever.document:default')

        # configure client ID
        registry = getUtility(IRegistry, context=self.portal)
        tab_reg = registry.forInterface(ITabbedView)
        tab_reg.batch_size = 5

Layer = IntegrationTestLayer([collective.testcaselayer.ptc.ptc_layer])
