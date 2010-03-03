from Products.PloneTestCase import ptc
import collective.testcaselayer.ptc

ptc.setupPloneSite()

class IntegrationTestLayer(collective.testcaselayer.ptc.BasePTCLayer):

    def afterSetUp(self):
        # Install the opengever.document product
        self.addProfile('opengever.document:default')

Layer = IntegrationTestLayer([collective.testcaselayer.ptc.ptc_layer])

class CheckoutTestLayer(collective.testcaselayer.ptc.BasePTCLayer):

    def afterSetUp(self):
        from Products.Five import zcml
        import opengever.document
        zcml.load_config('tests.zcml', opengever.document)
        # Install the opengever.document product
        self.addProfile('opengever.dossier:default')
        self.addProfile('opengever.document:default')
        self.addProfile('opengever.document:tests')
        import opengever.base
        zcml.load_config('configure.zcml', opengever.base)

CLayer = CheckoutTestLayer([collective.testcaselayer.ptc.ptc_layer])
