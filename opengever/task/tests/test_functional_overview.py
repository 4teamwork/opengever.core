from opengever.task.browser.overview import Overview
from plone.mocktestcase import MockTestCase
from zope.interface import directlyProvides
from opengever.globalindex.model.task import Task
from Products.ZCatalog.interfaces import ICatalogBrain
from z3c.form.interfaces import IFieldWidget


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

        # Dict
        item_dict = {'dict':'dict'}

        # Brain
        item_brain = self.create_dummy()
        directlyProvides(item_brain, ICatalogBrain)

        # SQLalchemy object
        item_sql = Task('id', 'id')

        # Others
        item_obj = self.create_dummy()

        self.replay()

        view = Overview(self.mock_context, self.mock_request)

        self.assertEqual(view.get_type(item_none), None)
        self.assertEqual(view.get_type(item_widget), 'widget')
        self.assertEqual(view.get_type(item_dict), 'dict')
        self.assertEqual(view.get_type(item_brain), 'brain')
        self.assertEqual(view.get_type(item_sql), 'sqlalchemy_object')
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
