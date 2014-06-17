from ftw.builder import Builder
from ftw.builder import create
from opengever.base.behaviors.classification import IClassification
from opengever.ogds.base.interfaces import ITransporter
from opengever.testing import FunctionalTestCase
from plone.app.testing import TEST_USER_ID
from zope.component import getUtility


class TestTransporter(FunctionalTestCase):
    """We test the transporter using only one client since the setup is much
    easier and the remote request are in fact a separate tool.
    """

    def setUp(self):
        super(TestTransporter, self).setUp()
        self.request = self.portal.REQUEST
        self.grant('Manager')

        self.user, self.org_unit, self.admin_unit = create(
            Builder('fixture').with_all_unit_setup())

    def test_transport_from_copies_the_object_inclusive_metadata_and_dublin_core_data(self):
        dossier = create(Builder("dossier").titled(u"Dossier"))
        document = create(Builder("document")
                          .within(dossier)
                          .titled(u'Testdocument')
                          .with_dummy_content())

        transporter = getUtility(ITransporter)
        transported_doc = transporter.transport_from(
            dossier, 'client1', '/'.join(document.getPhysicalPath()))

        self.assertEquals('Testdocument', transported_doc.title)
        self.assertEquals('Test data', transported_doc.file.data)

        self.assertEquals(u'unprotected',
                          IClassification(transported_doc).classification)
        self.assertEquals(u'unchecked',
                          IClassification(transported_doc).public_trial)

        self.assertEquals(document.created(), transported_doc.created())
        self.assertEquals(TEST_USER_ID, transported_doc.Creator())

    def test_transport_to_returns_a_dict_with_the_path_to_the_new_object(self):
        source_dossier = create(Builder("dossier").titled(u"Source"))
        target_dossier = create(Builder("dossier").titled(u"Target"))
        document = create(Builder("document")
                          .within(source_dossier)
                          .titled(u'Fo\xf6')
                          .with_dummy_content())

        transporter = getUtility(ITransporter)
        data = transporter.transport_to(
            document, 'client1', '/'.join(target_dossier.getPhysicalPath()))
        transported_doc = self.portal.unrestrictedTraverse(
            data.get('path').encode('utf-8'))

        # data
        self.assertEquals(u'Fo\xf6', transported_doc.title)
        self.assertEquals('Test data', transported_doc.file.data)

        # behavior data
        self.assertEquals(u'unprotected',
                          IClassification(transported_doc).classification)
        self.assertEquals(u'unchecked',
                          IClassification(transported_doc).public_trial)

        # dublin core
        self.assertEquals(document.created(), transported_doc.created())
        self.assertEquals(TEST_USER_ID, transported_doc.Creator())
