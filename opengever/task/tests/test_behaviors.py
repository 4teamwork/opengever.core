from opengever.base.interfaces import ISequenceNumber
from opengever.testing import Builder
from opengever.testing import FunctionalTestCase
from zope.component import getUtility


class TestTaskNameFromTitle(FunctionalTestCase):

    def test_id_generation(self):
        task1 = Builder('task').create()
        task2 = Builder('task').create()

        self.assertEquals(1, getUtility(ISequenceNumber).get_number(task1))
        self.assertEquals('task-1', task1.id)

        self.assertEquals(2, getUtility(ISequenceNumber).get_number(task2))
        self.assertEquals('task-2', task2.id)
