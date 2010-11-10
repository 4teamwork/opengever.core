from Products.PloneTestCase import ptc
import collective.testcaselayer.ptc

ptc.setupPloneSite()

class IntegrationTestLayer(collective.testcaselayer.ptc.BasePTCLayer):

    def afterSetUp(self):
        # Install the opengever.document product
        self.addProfile('opengever.base:default')
        self.addProfile('opengever.document:default')
        self.addProfile('opengever.respository:default')
Layer = IntegrationTestLayer([collective.testcaselayer.ptc.ptc_layer])