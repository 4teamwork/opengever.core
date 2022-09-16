from datetime import datetime
from ftw.testing import freeze
from opengever.document.interfaces import IDocumentSettings
from opengever.document.versioner import Versioner
from opengever.task.interfaces import ITaskDocumentsTransporter
from opengever.task.task import ITask
from opengever.testing import IntegrationTestCase
from plone import api
from z3c.relationfield.relation import RelationValue
from zope.component import getUtility
from zope.intid.interfaces import IIntIds
import pytz


class TestTransporter(IntegrationTestCase):

    def test_documents_task_transport(self):
        self.login(self.regular_user)

        self.assertItemsEqual([], self.seq_subtask_1.getFolderContents())

        doc_transporter = getUtility(ITaskDocumentsTransporter)
        doc_transporter.copy_documents_from_remote_task(
            self.task.get_sql_object(), self.seq_subtask_1)

        self.assertItemsEqual(
            [self.taskdocument.Title(), self.document.Title()],
            [aa.Title for aa in self.seq_subtask_1.getFolderContents()])

    def test_documents_task_transport_selected_docs(self):
        self.login(self.regular_user)
        intids = getUtility(IIntIds)

        ITask(self.task).relatedItems = [
             RelationValue(intids.getId(self.document)),
             RelationValue(intids.getId(self.subdocument))]

        self.assertItemsEqual([], self.seq_subtask_1.getFolderContents())

        doc_transporter = getUtility(ITaskDocumentsTransporter)
        ids = [intids.getId(self.subdocument), intids.getId(self.taskdocument)]
        intids_mapping = doc_transporter.copy_documents_from_remote_task(
            self.task.get_sql_object(), self.seq_subtask_1, documents=ids)

        self.assertItemsEqual(
            [self.subdocument.Title(), self.taskdocument.Title()],
            [aa.Title for aa in self.seq_subtask_1.getFolderContents()],
            )

        pair1, pair2 = intids_mapping.items()

        self.assertEquals(
            intids.getObject(pair1[0]).Title(),
            intids.getObject(pair1[1]).Title()
            )

        self.assertEquals(
            intids.getObject(pair2[0]).Title(),
            intids.getObject(pair2[1]).Title()
            )

    def test_documents_with_custom_comment(self):
        self.login(self.regular_user)
        doc_transporter = getUtility(ITaskDocumentsTransporter)
        doc_transporter.copy_documents_from_remote_task(
            self.task.get_sql_object(),
            self.seq_subtask_1,
            comment=u'Custom initial version')

        for brain in self.seq_subtask_1.getFolderContents():
            doc = brain.getObject()
            self.assertEquals(
                u'Custom initial version',
                Versioner(doc).get_custom_initial_version_comment())

    def test_documents_task_transport_does_not_set_dublin_core_fields(self):
        self.login(self.regular_user)
        intids = getUtility(IIntIds)
        ids = [intids.getId(self.document)]

        self.assertEqual(self.dossier_responsible.getId(),
                         self.document.Creator())

        with freeze(datetime(2017, 10, 16, 0, 0, tzinfo=pytz.utc)):
            doc_transporter = getUtility(ITaskDocumentsTransporter)
            doc_transporter.copy_documents_from_remote_task(
                self.task.get_sql_object(), self.seq_subtask_1, documents=ids)

        doc = self.seq_subtask_1.getFolderContents()[0].getObject()

        self.assertEqual(self.dossier_responsible.getId(),
                         self.document.Creator())
        self.assertEqual(self.regular_user.getId(), doc.Creator())

        self.assertEqual('2016/08/31 16:07:33 GMT+2',
                         str(self.document.created()))
        self.assertEqual('2017/10/16 02:00:00 GMT+2',
                         str(doc.created()))

    def test_initialize_preserved_as_paper_with_current_default(self):
        self.login(self.regular_user)
        intids = getUtility(IIntIds)
        ids = [intids.getId(self.document)]

        self.assertTrue(self.document.preserved_as_paper)

        # change default to false
        api.portal.set_registry_record(
            name='preserved_as_paper_default', interface=IDocumentSettings,
            value=False)

        with freeze(datetime(2017, 10, 16, 0, 0, tzinfo=pytz.utc)):
            doc_transporter = getUtility(ITaskDocumentsTransporter)
            doc_transporter.copy_documents_from_remote_task(
                self.task.get_sql_object(), self.seq_subtask_1, documents=ids)

        doc = self.seq_subtask_1.getFolderContents()[0].getObject()
        self.assertFalse(doc.preserved_as_paper)
