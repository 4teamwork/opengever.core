from Products.PloneTestCase import ptc
import collective.testcaselayer.ptc

ptc.setupPloneSite()

class IntegrationTestLayer(collective.testcaselayer.ptc.BasePTCLayer):

    def afterSetUp(self):
        
        from opengever import inbox
        self.loadZCML('configure.zcml', package=inbox)
        # Install the opengever.inbox product
        self.addProfile('opengever.inbox:default')

Layer = IntegrationTestLayer([collective.testcaselayer.ptc.ptc_layer])