from opengever.base.behaviors.classification import IClassification
from opengever.ogds.base.interfaces import ITransporter
from opengever.ogds.base.setuphandlers import _create_example_client
from opengever.ogds.base.transport import REQUEST_KEY
from opengever.ogds.base.utils import create_session
from opengever.testing import Builder
from opengever.testing import FunctionalTestCase
from opengever.testing import create_client
from opengever.testing import set_current_client_id
from plone.dexterity.fti import DexterityFTI
from plone.dexterity.utils import createContentInContainer
from zope.component import getUtility
from zope.globalrequest import setRequest


class TestTransporter(FunctionalTestCase):

    # We test the transporter using only one client since the setup is much
    # easier and the remote request are in fact a separate tool.

    def setUp(self):
        super(TestTransporter, self).setUp()
        self.request = self.portal.REQUEST
        self.grant('Manager')

    def test_transport_from(self):
        create_client()
        set_current_client_id(self.portal)
        dossier = Builder("dossier").titled("Dossier").create()
        document = Builder("document").within(dossier).titled(
            'Testdocument').with_dummy_content().with_default_values().create()

        transporter = getUtility(ITransporter)
        transported_doc = transporter.transport_from(
            dossier, 'client1', '/'.join(document.getPhysicalPath()))

        # data
        self.assertEquals(transported_doc.title, document.title)
        self.assertEquals(transported_doc.file.data, document.file.data)
        # behavior data
        self.assertEquals(IClassification(transported_doc).classification,
                          IClassification(document).classification)
        self.assertEquals(IClassification(transported_doc).public_trial,
                          IClassification(document).public_trial)
        # dublin core
        self.assertEquals(transported_doc.created(), document.created())
        self.assertEquals(transported_doc.Creator(), document.Creator())

    def test_transport_to(self):
        create_client()
        set_current_client_id(self.portal)
        source_dossier = Builder("dossier").titled("Source").create()
        target_dossier = Builder("dossier").titled("Target").create()
        document = Builder("document").within(source_dossier).titled(
            u'Fo\xf6').with_dummy_content().with_default_values().create()

        transporter = getUtility(ITransporter)
        data = transporter.transport_to(
            document, 'client1', '/'.join(target_dossier.getPhysicalPath()))
        transported_doc = self.portal.unrestrictedTraverse(
            data.get('path').encode('utf-8'))

        # data
        self.assertEquals(transported_doc.title, document.title)
        self.assertEquals(transported_doc.file.data, document.file.data)
        # behavior data
        self.assertEquals(IClassification(transported_doc).classification,
                          IClassification(document).classification)
        self.assertEquals(IClassification(transported_doc).public_trial,
                          IClassification(document).public_trial)
        # dublin core
        self.assertEquals(transported_doc.created(), document.created())
        self.assertEquals(transported_doc.Creator(), document.Creator())
