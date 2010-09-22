from Products.PloneTestCase import ptc
import collective.testcaselayer.ptc

ptc.setupPloneSite()

class IntegrationTestLayer(collective.testcaselayer.ptc.BasePTCLayer):

    def afterSetUp(self):
        
        from opengever.dossier import tests
        self.loadZCML('testing.zcml', package=tests)
        
        # Install the example.conference product
        self.addProfile('opengever.dossier:default')
        self.addProfile('opengever.workflows:default')

Layer = IntegrationTestLayer([collective.testcaselayer.ptc.ptc_layer])