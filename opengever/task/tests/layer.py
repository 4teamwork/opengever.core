from Products.PloneTestCase import ptc
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
import collective.testcaselayer.ptc


ptc.setupPloneSite()


class IntegrationTestLayer(collective.testcaselayer.ptc.BasePTCLayer):

    def afterSetUp(self):
        # Install the opengever.task product
        self.addProfile('opengever.task:default')
        # configure the client id
        registry = getUtility(IRegistry)
        registry['opengever.octopus.tentacle.interfaces.ITentacleRegistry.cid'] = u'm1'


Layer = IntegrationTestLayer([collective.testcaselayer.ptc.ptc_layer])
