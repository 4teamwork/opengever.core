from collective.testcaselayer.ptc import BasePTCLayer, ptc_layer
from opengever.ogds.base.interfaces import IClientConfiguration
from plone.registry.interfaces import IRegistry
from zope.component import getUtility


class MailIntegrationLayer(BasePTCLayer):
    """Layer for integration tests."""

    def afterSetUp(self):

        # Load testing zcml (optional)
        import opengever.mail
        import opengever.base
        import opengever.ogds.base
        import opengever.document
        self.loadZCML('configure.zcml', package=opengever.mail)
        self.loadZCML('configure.zcml', package=opengever.base)
        self.loadZCML('tests.zcml', package=opengever.ogds.base)
        self.loadZCML('configure.zcml', package=opengever.document)

        # Load GS profile
        self.addProfile('opengever.ogds.base:default')
        self.addProfile('opengever.mail:default')
        self.addProfile('opengever.base:default')
        self.addProfile('opengever.document:default')

        # configure client ID
        registry = getUtility(IRegistry, context=self.portal)
        client = registry.forInterface(IClientConfiguration)
        client.client_id = u'plone'

        from opengever.base.interfaces import IBaseClientID
        baseclientid = registry.forInterface(IBaseClientID)
        baseclientid.client_id = u'OG'

    def beforeTearDown(self):
        pass

mail_integration_layer = MailIntegrationLayer(bases=[ptc_layer])