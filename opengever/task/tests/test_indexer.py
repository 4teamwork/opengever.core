from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from opengever.testing import create_ogds_user
from opengever.testing import FunctionalTestCase
from opengever.testing import index_data_for
from opengever.testing import obj2brain
from plone.app.testing import login
from plone.app.testing import TEST_USER_NAME


class TestTaskIndexers(FunctionalTestCase):

    def setUp(self):
        super(TestTaskIndexers, self).setUp()
        self.portal.portal_types['opengever.task.task'].global_allow = True

        self.user, self.org_unit, self.admin_unit = create(
            Builder('fixture').with_all_unit_setup())

        self.grant('Contributor', 'Editor', 'Manager')
        login(self.portal, TEST_USER_NAME)

        self.task = create(Builder("task").titled("Test task 1"))
        self.subtask = create(Builder("task").within(self.task).titled("Test task 1"))
        self.doc1 = create(Builder("document").titled(u"Doc One"))
        self.doc2 = create(Builder("document").titled(u"Doc Two"))

    def test_date_of_completion(self):
        self.assertEquals(
            obj2brain(self.task).date_of_completion,
            datetime(1970, 1, 1))

        self.task.date_of_completion = datetime(2012, 2, 2)
        self.task.reindexObject()

        self.assertEquals(
            obj2brain(self.task).date_of_completion,
            datetime(2012, 2, 2))

    def test_assigned_client(self):
        self.assertEquals(
            obj2brain(self.task).assigned_client, '')

        self.task.responsible = 'hugo.boss'
        self.task.responsible_client = 'client_xy'
        self.task.reindexObject()

        self.assertEquals(
            obj2brain(self.task).assigned_client, 'client_xy')

    def test_is_subtask(self):
        self.assertFalse(obj2brain(self.task).is_subtask)

        self.assertTrue(obj2brain(self.subtask).is_subtask)

    def test_searchable_text(self):
        self.task.title = u'Test Aufgabe'
        self.task.text = u'Lorem ipsum olor sit amet'

        create_ogds_user('hboss', firstname='Hugo', lastname='Boss')
        self.task.responsible = 'hboss'

        self.task.reindexObject()

        self.assertEquals(
            index_data_for(self.task).get('SearchableText'),
            ['test', 'aufgabe', 'lorem', 'ipsum', 'olor', 'sit',
             'amet', '1', 'boss', 'hugo', 'hboss'])
