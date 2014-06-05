from opengever.globalindex.interfaces import ITaskQuery
from opengever.ogds.base.utils import get_client_id
from opengever.task.interfaces import ITaskDocumentsTransporter
from opengever.task.task import ITask
from opengever.testing import OPENGEVER_INTEGRATION_TESTING
from opengever.testing import create_client
from opengever.testing import set_current_client_id
from plone.app.testing import TEST_USER_ID
from plone.dexterity.utils import createContentInContainer
from plone.dexterity.utils import iterSchemata
from z3c.form.interfaces import IValue
from z3c.relationfield.relation import RelationValue
from zope.component import getUtility, queryMultiAdapter
from zope.intid.interfaces import IIntIds
from zope.schema import getFieldsInOrder
import unittest2 as unittest


def set_defaults(obj):
    for schemata in iterSchemata(obj):
        for name, field in getFieldsInOrder(schemata):
            try:
                value = field.get(field.interface(obj))
                if value:
                    # field is present with a truthy value, nothing to do
                    continue
            except AttributeError:
                # Field not present, set default
                pass
            default = queryMultiAdapter(
                (obj, obj.REQUEST, None, field, None),
                IValue,
                name='default')
            if default is not None:
                default = default.get()
            if default is None:
                default = getattr(field, 'default', None)
            if default is None:
                try:
                    default = field.missing_value
                except AttributeError:
                    pass
            field.set(field.interface(obj), default)

    return obj


class TestTransporter(unittest.TestCase):

    layer = OPENGEVER_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']

        create_client()
        set_current_client_id(self.portal)


    def _create_task(self, context, with_docs=False, return_docs=False):

        # task
        task = createContentInContainer(
            context,
            'opengever.task.task',
            title="Task1", task_type='correction',
            checkConstraints=False)
        task.responsible = TEST_USER_ID

        if not with_docs:
            return task

        documents = []
        # containing documents
        documents.append(set_defaults(createContentInContainer(
                task, 'opengever.document.document', title=u'Doc 1')))
        documents.append(set_defaults(createContentInContainer(
                task, 'opengever.document.document', title=u'Doc 2')))

        # related documents
        documents.append(set_defaults(createContentInContainer(
            context, 'opengever.document.document', title=u'Doc 3')))

        documents.append(set_defaults(createContentInContainer(
            context, 'opengever.document.document', title=u'Doc 4')))

        intids = getUtility(IIntIds)
        ITask(task).relatedItems = [
            RelationValue(intids.getId(documents[2]))]

        if return_docs:
            return task, documents
        return task

    def test_documents_task_transport(self):
        intids = getUtility(IIntIds)

        task = self._create_task(self.portal, with_docs=True)
        target = self._create_task(self.portal)

        sql_task = getUtility(ITaskQuery).get_task(
            intids.getId(task), get_client_id())

        doc_transporter = getUtility(ITaskDocumentsTransporter)
        doc_transporter.copy_documents_from_remote_task(
            sql_task, target)

        self.assertEquals(
            [aa.Title for aa in target.getFolderContents()].sort(),
            ['Doc 1', 'Doc 2', 'Doc 3', 'Doc 4'].sort())

    def test_documents_task_transport_selected_docs(self):
        intids = getUtility(IIntIds)

        task, documents = self._create_task(
            self.portal, with_docs=True, return_docs=True)
        target = self._create_task(self.portal)
        sql_task = getUtility(ITaskQuery).get_task(
            intids.getId(task), get_client_id())

        doc_transporter = getUtility(ITaskDocumentsTransporter)
        ids = [intids.getId(documents[0]), intids.getId(documents[3])]
        intids_mapping = doc_transporter.copy_documents_from_remote_task(
            sql_task, target, documents=ids)

        self.assertEquals(
            [aa.Title for aa in target.getFolderContents()].sort(),
            ['Doc 1', 'Doc 4'].sort())

        pair1 = intids_mapping.items()[0]
        pair2 = intids_mapping.items()[0]

        self.assertEquals(
            intids.getObject(pair1[0]).Title(),
            intids.getObject(pair1[1]).Title()
            )

        self.assertEquals(
            intids.getObject(pair2[0]).Title(),
            intids.getObject(pair2[1]).Title()
            )
