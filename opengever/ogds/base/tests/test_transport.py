from opengever.base.behaviors.classification import IClassification
from opengever.ogds.base.interfaces import ITransporter
from opengever.testing import Builder
from opengever.testing import FunctionalTestCase
from opengever.testing import create
from opengever.testing import create_client
from opengever.testing import set_current_client_id
from zope.component import getUtility


class TestTransporter(FunctionalTestCase):
    """We test the transporter using only one client since the setup is much
    easier and the remote request are in fact a separate tool.
    """

    def setUp(self):
        super(TestTransporter, self).setUp()
        self.request = self.portal.REQUEST
        self.grant('Manager')
        create_client()
        set_current_client_id(self.portal)


    def test_transport_from_copies_the_object_inclusive_metadata_and_dublin_core_data(self):
        dossier = create(Builder("dossier").titled("Dossier"))
        document = create(Builder("document")
                          .within(dossier)
                          .titled('Testdocument')
                          .with_dummy_content()
                          .with_default_values())

        transporter = getUtility(ITransporter)
        transported_doc = transporter.transport_from(
            dossier, 'client1', '/'.join(document.getPhysicalPath()))

        self.assertEquals(transported_doc.title, document.title)
        self.assertEquals(transported_doc.file.data, document.file.data)

        self.assertEquals(IClassification(transported_doc).classification,
                          IClassification(document).classification)
        self.assertEquals(IClassification(transported_doc).public_trial,
                          IClassification(document).public_trial)

        self.assertEquals(transported_doc.created(), document.created())
        self.assertEquals(transported_doc.Creator(), document.Creator())

    def test_transport_to_returns_a_dict_with_the_path_to_the_new_object(self):
        source_dossier = create(Builder("dossier").titled("Source"))
        target_dossier = create(Builder("dossier").titled("Target"))
        document = create(Builder("document")
                          .within(source_dossier)
                          .titled(u'Fo\xf6')
                          .with_dummy_content()
                          .with_default_values())

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
