from ftw.tabbedview.interfaces import ITabbedView
from plone.registry.interfaces import IRegistry
from Products.PloneTestCase import ptc
from zope.component import getUtility
import collective.testcaselayer.ptc

ptc.setupPloneSite()


class IntegrationTestLayer(collective.testcaselayer.ptc.BasePTCLayer):

    def afterSetUp(self):

        from opengever import task
        self.loadZCML('configure.zcml', package=task)
        from opengever import document
        self.loadZCML('configure.zcml', package=document)
        from ftw import tabbedview
        self.loadZCML('configure.zcml', package=tabbedview)
        
        # Install the opengever.task product
        self.addProfile('opengever.task:default')

        self.addProfile('ftw.tabbedview:default')
        self.addProfile('opengever.document:default')

        # configure client ID
        registry = getUtility(IRegistry, context=self.portal)
        tab_reg = registry.forInterface(ITabbedView)
        tab_reg.batch_size = 5

Layer = IntegrationTestLayer([collective.testcaselayer.ptc.ptc_layer])
