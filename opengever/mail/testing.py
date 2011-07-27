from collective.testcaselayer.ptc import BasePTCLayer, ptc_layer
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
        import opengever.dossier
        self.loadZCML('configure.zcml', package=opengever.mail)
        self.loadZCML('configure.zcml', package=opengever.base)
        self.loadZCML('tests.zcml', package=opengever.ogds.base)
        self.loadZCML('configure.zcml', package=opengever.document)
        self.loadZCML('configure.zcml', package=opengever.dossier)

        # Load GS profile
        self.addProfile('opengever.ogds.base:default')
        self.addProfile('opengever.mail:default')
        self.addProfile('opengever.base:default')
        self.addProfile('opengever.document:default')
        self.addProfile('opengever.dossier:default')
        self.addProfile('ftw.tabbedview:default')

        # configure client ID
        registry = getUtility(IRegistry )
        registry['opengever.ogds.base.interfaces.'
                 'IClientConfiguration.client_id'] = u'plone'
        registry['opengever.base.interfaces.IBaseClientID.client_id'] = u'OG'


    def beforeTearDown(self):
        pass

mail_integration_layer = MailIntegrationLayer(bases=[ptc_layer])