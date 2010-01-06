from Products.PloneTestCase import ptc
import collective.testcaselayer.ptc

ptc.setupPloneSite()

class IntegrationTestLayer(collective.testcaselayer.ptc.BasePTCLayer):

    def afterSetUp(self):
        # Install the example.conference product
        self.addProfile('opengever.repository:default')

Layer = IntegrationTestLayer([collective.testcaselayer.ptc.ptc_layer])