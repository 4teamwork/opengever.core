from opengever.task.browser.layout import LayoutPolicy
from opengever.testing import Builder
from opengever.testing import FunctionalTestCase
from opengever.testing import create


class TestBodyClasses(FunctionalTestCase):

    def assert_base_classes(self, task, additional_class=None):
        layout_view = task.restrictedTraverse('plone_layout')
        origin_classes = super(LayoutPolicy, layout_view).bodyClass(
            task.base_view, None).split(' ')
        new_classes = layout_view.bodyClass(task.base_view, None).split(' ')

        if additional_class:
            origin_classes.append(additional_class)

        self.assertEquals(origin_classes,
                          new_classes,
                          'Bodyclasses are not equal to the origin classes.')

    def test_maintask_classes_are_super_classes(self):
        task1 = create(Builder('task'))
        self.assert_base_classes(task1)

    def test_subtask_appends_subtask_class(self):
        task1 = create(Builder('task'))
        subtask1 = create(Builder('task').within(task1))
        self.assert_base_classes(subtask1, additional_class='tasktype-subtask')

    def test_remotetask_appends_remotetask_class(self):
        task1 = create(Builder('task')
                       .having(responsible_client='another client'))
        self.assert_base_classes(task1, additional_class='tasktype-remotetask')
