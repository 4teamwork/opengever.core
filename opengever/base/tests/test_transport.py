from datetime import date
from datetime import datetime
from opengever.base.behaviors.classification import IClassification
from opengever.base.interfaces import IDataCollector
from opengever.base.transport import Transporter
from opengever.task.reminder import ReminderOnDate
from opengever.testing import IntegrationTestCase
from zExceptions import Unauthorized
from zope.component import getAdapters
import json


class TestTransporter(IntegrationTestCase):
    """We test the transporter using only one client since the setup is much
    easier and the remote request are in fact a separate tool.
    """

    def setUp(self):
        super(TestTransporter, self).setUp()
        self.request = self.portal.REQUEST

    def test_all_data_collectors_extract_json_compatible_data(self):
        self.login(self.regular_user)

        self.task.set_reminder(ReminderOnDate({'date': date(2019, 12, 30)}))
        objects_to_test = [self.task]

        for obj in objects_to_test:
            adapters = getAdapters((self.task,), IDataCollector)
            for name, adapter in adapters:
                data = adapter.extract()
                try:
                    json.dumps(data)
                except TypeError:
                    self.fail("Extracted data from IDataCollector adapter "
                              "%r (%r) is not JSON serializable: "
                              "%r" % (name, adapter, data))

    def test_transport_from_copies_the_object_inclusive_metadata_and_dublin_core_data(self):
        self.login(self.regular_user)

        transported_doc = Transporter().transport_from(
            self.empty_dossier, 'plone', '/'.join(self.document.getPhysicalPath()))

        self.assertEquals(self.document.title, transported_doc.title)
        self.assertEquals(self.document.file.data, transported_doc.file.data)

        self.assertEquals(u'unprotected',
                          IClassification(transported_doc).classification)
        self.assertEquals(u'unchecked',
                          IClassification(transported_doc).public_trial)

        self.assertEquals(self.document.created(), transported_doc.created())
        self.assertEquals(self.document.Creator(), transported_doc.Creator())

    def test_transport_to_returns_a_dict_with_the_path_to_the_new_object(self):
        self.login(self.regular_user)

        data = Transporter().transport_to(
            self.document, 'plone', '/'.join(self.empty_dossier.getPhysicalPath()))

        transported_doc = self.portal.unrestrictedTraverse(data.get('path').encode('utf-8'))

        # data
        self.assertEquals(self.document.title, transported_doc.title)
        self.assertEquals(self.document.file.data, transported_doc.file.data)

        # behavior data
        self.assertEquals(u'unprotected',
                          IClassification(transported_doc).classification)
        self.assertEquals(u'unchecked',
                          IClassification(transported_doc).public_trial)

        # dublin core
        self.assertEquals(self.document.created(), transported_doc.created())
        self.assertEquals(self.document.Creator(), transported_doc.Creator())

    def test_transports_tasks_correctly(self):
        self.login(self.regular_user)

        Transporter().transport_from(
            self.empty_dossier, 'plone', '/'.join(self.subtask.getPhysicalPath()))

        new_task, = self.empty_dossier.objectValues()

        self.assertEquals(self.task.title, self.task.title)
        self.assertEquals(self.task.responsible, new_task.responsible)
        self.assertEquals(self.task.issuer, new_task.issuer)

    def test_transport_to_with_elevated_privileges(self):
        self.login(self.administrator)
        target_path = '/'.join(self.protected_dossier.getPhysicalPath())

        self.login(self.regular_user)
        with self.assertRaises(Unauthorized):
            Transporter().transport_to(self.task, 'plone', target_path)

        self.login(self.regular_user)
        Transporter().transport_to(
            self.task, 'plone', target_path,
            view='transporter-privileged-receive-object')

    def test_transport_to_does_not_break_deadline_datatype(self):
        self.login(self.regular_user)

        Transporter().transport_to(self.task, 'plone', '/'.join(self.empty_dossier.getPhysicalPath()))

        new_task, = self.empty_dossier.objectValues()
        self.assertFalse(isinstance(new_task.deadline, datetime))
