from Products.PloneTestCase import ptc
import collective.testcaselayer.ptc
from plone.directives import form

ptc.setupPloneSite()

class IntegrationTestLayer(collective.testcaselayer.ptc.BasePTCLayer):

    def afterSetUp(self):
        # Install the opengever.document product
        self.addProfile('opengever.base:default')

Layer = IntegrationTestLayer([collective.testcaselayer.ptc.ptc_layer])

class IEmptySchema(form.Schema):
    """an empty schema used or tests"""
