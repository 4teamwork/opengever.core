from Products.PloneTestCase import ptc
import collective.testcaselayer.ptc

ptc.setupPloneSite()

class IntegrationTestLayer(collective.testcaselayer.ptc.BasePTCLayer):

    def afterSetUp(self):
        # Install the ftw.task product
        self.addProfile('opengever.inbox:default')

Layer = IntegrationTestLayer([collective.testcaselayer.ptc.ptc_layer])