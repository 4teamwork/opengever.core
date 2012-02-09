from opengever.task.browser.overview import Overview
from plone.mocktestcase import MockTestCase
from zope.interface import directlyProvides
from opengever.globalindex.model.task import Task
from z3c.form.interfaces import IFieldWidget
from opengever.task.task import ITask
from mocker import ANY
from datetime import datetime
from plone.i18n.normalizer.interfaces import IIDNormalizer
from opengever.task.interfaces import ISuccessorTaskController
from opengever.ogds.base.interfaces import IContactInformation
from opengever.base.interfaces import ISequenceNumber
from plone.registry.interfaces import IRegistry



class TestOverviewFunctions(MockTestCase):

    def setUp(self):
        self.mock_context = self.mocker.mock(count=False)
        self.mock_request = self.mocker.mock(count=False)

    def test_get_type(self):
        """ Test for get_type method
        """
        # None
        item_none = []

        # Widget
        item_widget = self.create_dummy()
        directlyProvides(item_widget, IFieldWidget)

        # SQLalchemy object
        item_sql = Task('id', 'id')

        # Task-Object
        item_task = self.create_dummy()
        directlyProvides(item_task, ITask)

        # Others
        item_obj = self.create_dummy()

        self.replay()

        view = Overview(self.mock_context, self.mock_request)

        self.assertEqual(view.get_type(item_none), None)
        self.assertEqual(view.get_type(item_widget), 'widget')
        self.assertEqual(view.get_type(item_sql), 'task')
        self.assertEqual(view.get_type(item_task), 'task')
        self.assertEqual(view.get_type(item_obj), 'obj')

    def test_boxes(self):
        """ Test the boxlayout. We don't check the content, just the layout
        because we test the content in other tests
        """
        self.replay()

        view = Overview(self.mock_context, self.mock_request)
        view.additional_attributes = lambda : 'box'
        view.documents = lambda : 'box'
        view.get_containing_task = lambda : 'box'
        view.get_sub_tasks = lambda : 'box'
        view.get_predecessor_task = lambda : 'box'
        view.get_successor_tasks = lambda : 'box'

        boxes = view.boxes()

        # Rows
        self.assertTrue(len(boxes) == 2)

        # Left row
        self.assertTrue(len(boxes[0]) == 2)

        # Right row
        self.assertTrue(len(boxes[1]) == 4)

        # The rows contains dicts
        items = boxes[0] + boxes[1]
        for item in items:
            self.assertTrue(type(item) == dict)

    def test_documents(self):

        doc_cat_1 = self.mocker.mock(count=False)
        self.expect(doc_cat_1.getObject()).result(doc_cat_1)
        self.expect(doc_cat_1.modified()).result(datetime(2012, 6, 1))

        doc_cat_2 = self.mocker.mock(count=False)
        self.expect(doc_cat_2.getObject()).result(doc_cat_2)
        self.expect(doc_cat_2.modified()).result(datetime(2012, 1, 1))

        doc_rel_1 = self.mocker.mock(count=False)
        self.expect(doc_rel_1.to_object).result(doc_rel_1)
        self.expect(doc_rel_1.portal_type).result('opengever.document.document')
        self.expect(doc_rel_1.modified()).result(datetime(2012, 3, 1))

        doc_rel_2 = self.mocker.mock(count=False)
        self.expect(doc_rel_2.to_object).result(doc_rel_2)
        self.expect(doc_rel_2.portal_type).result('ftw.mail.mail')
        self.expect(doc_rel_2.modified()).result(datetime(2012, 2, 1))

        mock_catalog = self.mocker.mock()
        self.mock_tool(mock_catalog, 'portal_catalog')
        self.expect(mock_catalog(path=ANY, portal_type=ANY)).result([doc_cat_1, doc_cat_2])

        self.expect(self.mock_context.relatedItems).result([doc_rel_1, doc_rel_2])
        self.expect(self.mock_context.getPhysicalPath()).result('google')

        self.replay()

        view = Overview(self.mock_context, self.mock_request)
        docs = view.documents()

        # Look for sort-order
        self.assertEqual(docs[0].modified(), datetime(2012, 6, 1))
        self.assertEqual(docs[1].modified(), datetime(2012, 3, 1))
        self.assertEqual(docs[2].modified(), datetime(2012, 2, 1))
        self.assertEqual(docs[3].modified(), datetime(2012, 1, 1))

    def test_additional_attributes(self):
        pass

    def test_get_css_class(self):

        item = self.mocker.mock(count=False)
        self.expect(item.portal_type).result('testtype')

        id_normalizer = self.mocker.mock()
        self.expect(id_normalizer(ANY)).call(lambda x: x)
        self.expect(id_normalizer.normalize).result(id_normalizer)
        self.mock_utility(id_normalizer, IIDNormalizer)

        self.replay()

        view = Overview(self.mock_context, self.mock_request)

        # Check the string
        self.assertEqual(
            view.get_css_class(item),
            "rollover-breadcrumb contenttype-testtype"
            )

    def test_get_containing_task(self):
        """ We get a the parent in a list, if its a task.
        """
        parent_task = self.mocker.mock(count=False)
        self.expect(parent_task.portal_type).result('task')

        context_task = self.mocker.mock(count=False)
        self.expect(context_task.__parent__).result(parent_task)
        self.expect(context_task.portal_type).result('task')

        parent_obj = self.mocker.mock(count=False)
        self.expect(parent_obj.portal_type).result('obj')

        context_obj = self.mocker.mock(count=False)
        self.expect(context_obj.__parent__).result(parent_obj)
        self.expect(context_obj.portal_type).result('task')

        self.replay()

        view_task = Overview(context_task, self.mock_request)
        view_obj = Overview(context_obj, self.mock_request)

        result_task = view_task.get_containing_task()
        result_obj = view_obj.get_containing_task()

        # We need a list
        self.assertTrue(isinstance(result_task, list))
        self.assertTrue(isinstance(result_obj, list))

        # Check number of items
        self.assertTrue(len(result_task) == 1)
        self.assertTrue(len(result_obj) == 0)

    def test_get_predecessor_task(self):
        """ Get the predecessor in a list
        """
        context_with = self.create_dummy()
        directlyProvides(context_with, ISuccessorTaskController)
        mock_context_with = self.mocker.proxy(context_with, spec=False)
        self.expect(mock_context_with.get_predecessor()).result('predecessor')

        context_without = self.create_dummy()
        directlyProvides(context_without, ISuccessorTaskController)
        mock_context_without = self.mocker.proxy(context_without, spec=False)
        self.expect(mock_context_without.get_predecessor()).result(None)

        self.replay()

        view_with = Overview(mock_context_with, self.mock_request)
        view_without = Overview(mock_context_without, self.mock_request)

        result_with = view_with.get_predecessor_task()
        result_without = view_without.get_predecessor_task()

        # We need a list
        self.assertTrue(isinstance(result_with, list))
        self.assertTrue(isinstance(result_without, list))

        # Check number of items
        self.assertTrue(len(result_with) == 1)
        self.assertTrue(len(result_without) == 0)

    def test_task_state_wrapper(self):
        """ Wrap the state-class arount a text
        """

        # SQLalchemy object
        item_sql = Task('id', 'id')
        mock_item_sql = self.mocker.proxy(item_sql, spec=False)
        self.expect(mock_item_sql.review_state).result('state-sql')

        # Task-Object
        item_task = self.create_dummy()
        directlyProvides(item_task, ITask)

        # Others
        item_obj = self.create_dummy()

        mock_wftool = self.mocker.mock()
        self.mock_tool(mock_wftool, 'portal_workflow')
        self.expect(mock_wftool.getInfoFor(ANY, ANY)).result('state-task')

        self.replay()

        view = Overview(self.mock_context, self.mock_request)

        sql = view.task_state_wrapper(mock_item_sql, 'wraptext')
        task = view.task_state_wrapper(item_task, 'wraptext')
        obj = view.task_state_wrapper(item_obj, 'wraptext')

        self.assertEqual(obj, '')
        self.assertEqual(sql, '<span class="wf-state-sql">wraptext</span>')
        self.assertEqual(task, '<span class="wf-state-task">wraptext</span>')

    def test_get_task_info(self):

        # Task-Object
        item_task = self.create_dummy()
        directlyProvides(item_task, ITask)
        mock_item_task = self.mocker.proxy(item_task, spec=False, count=False)
        self.expect(mock_item_task.responsible_client).result('client_name')
        self.expect(mock_item_task.responsible).result('user1')

        # Task-Object wihout responsible client
        item_task_without = self.create_dummy()
        directlyProvides(item_task_without, ITask)
        mock_item_task_without = self.mocker.proxy(item_task_without, spec=False, count=False)
        self.expect(mock_item_task_without.responsible_client).result(None)
        self.expect(mock_item_task_without.responsible).result('user2')

        # Others
        item_obj = self.create_dummy()

        # Contactinfo utility
        contact_info = self.mocker.mock(count=False)
        self.mock_utility(contact_info, IContactInformation)
        self.expect(contact_info.get_clients()).result(['c1', 'c2'])
        self.expect(contact_info.get_client_by_id(ANY)).result(None)
        self.expect(contact_info.describe(ANY)).call(lambda x: x)
        self.expect(contact_info.render_link(ANY)).call(lambda x: x)

        # Sequencenumber utility
        sequencenumber = self.mocker.mock(count=False)
        self.mock_utility(sequencenumber, ISequenceNumber)
        self.expect(sequencenumber.get_number(ANY)).result(3)

        # Registry utility
        registry = self.mocker.mock(count=False)
        self.mock_utility(registry, IRegistry)
        self.expect(registry.forInterface(ANY)).result(registry)
        self.expect(registry.client_id).result('client_id')

        self.replay()

        view = Overview(self.mock_context, self.mock_request)

        info_obj = view.get_task_info(item_obj)
        info_with = view.get_task_info(mock_item_task)
        info_without = view.get_task_info(mock_item_task_without)

        self.assertEqual(info_obj, None)
        self.assertEqual(info_with, 'client_id 3 / client_name / user1')
        self.assertEqual(info_without, 'user2')