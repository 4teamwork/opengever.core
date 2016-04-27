from datetime import date
from ftw.builder import Builder
from ftw.builder import create
from opengever.base.behaviors.classification import IClassification
from opengever.base.transport import Transporter
from opengever.testing import FunctionalTestCase
from plone import api
from plone.app.testing import TEST_USER_ID
from zExceptions import Unauthorized


class TestTransporter(FunctionalTestCase):
    """We test the transporter using only one client since the setup is much
    easier and the remote request are in fact a separate tool.
    """

    def setUp(self):
        super(TestTransporter, self).setUp()
        self.request = self.portal.REQUEST

    def test_transport_from_copies_the_object_inclusive_metadata_and_dublin_core_data(self):
        dossier = create(Builder("dossier").titled(u"Dossier"))
        document = create(Builder("document")
                          .within(dossier)
                          .titled(u'Testdocument')
                          .with_dummy_content())

        transported_doc = Transporter().transport_from(
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

        data = Transporter().transport_to(
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

    def test_transports_tasks_correctly(self):
        source_dossier = create(Builder("dossier").titled(u"Source"))
        target_dossier = create(Builder("dossier").titled(u"Target"))
        task = create(Builder("task")
                      .within(source_dossier)
                      .titled(u'Fo\xf6')
                      .having(deadline=date(2014, 7, 1)))

        transported_task = Transporter().transport_from(
            source_dossier, 'client1', '/'.join(task.getPhysicalPath()))

    def test_transport_to_with_elevated_privileges(self):
        source = create(Builder("dossier").titled(u"Source"))
        target = create(Builder("dossier").titled(u"Target"))
        target_path = '/'.join(target.getPhysicalPath())
        task = create(Builder("task")
                      .within(source)
                      .titled(u'Fo\xf6')
                      .having(deadline=date(2014, 7, 1)))

        create(Builder('user').named('Hugo', 'Boss'))
        api.user.grant_roles(username=u'hugo.boss',
                             obj=source,
                             roles=['Contributor', 'Editor', 'Reader'])
        self.login(u'hugo.boss')

        with self.assertRaises(Unauthorized):
            Transporter().transport_to(task, 'client1', target_path)

        Transporter().transport_to_with_elevated_privileges(
            task, 'client1', target_path)

    def test_keyword_argument_view_is_not_allowed_when_transporting_with_elevated_privileges_(self):

        with self.assertRaises(ValueError) as cm:
            Transporter().transport_to_with_elevated_privileges(
                object(), 'client1', '/ordnungssytem', view='submit-proposal')

        self.assertEquals('Keyword argument `view` not allowed.',
                          str(cm.exception))
