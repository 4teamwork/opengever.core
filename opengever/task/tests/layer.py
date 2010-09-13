from Products.PloneTestCase import ptc
import collective.testcaselayer.ptc


ptc.setupPloneSite()


class IntegrationTestLayer(collective.testcaselayer.ptc.BasePTCLayer):

    def afterSetUp(self):
        # Install the opengever.task product
        self.addProfile('opengever.task:default')


Layer = IntegrationTestLayer([collective.testcaselayer.ptc.ptc_layer])
