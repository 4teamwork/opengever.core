from Products.PloneTestCase import ptc
from opengever.octopus.tentacle.communicator import CortexCommunicator
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
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
        self.addProfile('opengever.octopus.tentacle:default')
        self.addProfile('opengever.document:default')
        self.addProfile('opengever.document:tests')
        import opengever.base
        zcml.load_config('configure.zcml', opengever.base)
        # fix registry
        registry = getUtility(IRegistry)
        registry['opengever.octopus.tentacle.interfaces.'
                 'ITentacleRegistry.cid'] = u'm1'

        # mock tentacle communicator
        CortexCommunicator.__ori_list_tentacles = \
            CortexCommunicator.list_tentacles
        CortexCommunicator.list_tentacles = lambda s: [
            {u'cid': u'm1',
             u'title': u'Mandant 1',
             u'enabled': True,
             u'public_url': 'http://nohost/plone',
             u'site_url': 'http://nohost/plone',
             u'ip_address': u'127.0.0.1',
             u'groups': []}]

    def beforeTearDown(self):
        # unmock tentacle communicator
        CortexCommunicator.list_tentacles = \
            CortexCommunicator.__ori_list_tentacles
        try:
            delattr(CortexCommunicator, '__ori_list_tentacles')
        except AttributeError:
            pass


CLayer = CheckoutTestLayer([collective.testcaselayer.ptc.ptc_layer])
