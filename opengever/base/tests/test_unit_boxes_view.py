from opengever.base.browser.boxes_view import BoxesViewMixin
from opengever.globalindex.model.task import Task
from Products.ZCatalog.CatalogBrains import AbstractCatalogBrain
from unittest import TestCase
from z3c.form.interfaces import IFieldWidget
from z3c.form.widget import Widget
from zope.interface import alsoProvides


class MockBrain(AbstractCatalogBrain):
    __record_schema__ = {}


class TestUnitBoxesView(TestCase):

    def setUp(self):
        super(TestUnitBoxesView, self).setUp()

        self.view = BoxesViewMixin()

    def test_get_type_dict(self):
        self.assertEqual('dict', self.view.get_type(dict()))

    def test_get_type_brain(self):
        self.assertEqual('brain', self.view.get_type(MockBrain()))

    def test_get_type_widget(self):
        mock_widget = Widget(None)
        alsoProvides(mock_widget, IFieldWidget)

        self.assertEqual('widget', self.view.get_type(mock_widget))

    def test_get_type_task(self):
        self.assertEqual('globalindex_task',
                         self.view.get_type(Task(123, 'foo')))

    def test_invalid_value_raises(self):
        class Foo(object):
            pass

        with self.assertRaises(ValueError):
            self.view.get_type(Foo())
