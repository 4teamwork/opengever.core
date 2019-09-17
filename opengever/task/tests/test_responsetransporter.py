from datetime import date
from ftw.builder import Builder
from ftw.builder import create
from opengever.base.response import IResponseContainer
from opengever.task.interfaces import IDeadlineModifier
from opengever.task.task import ITask
from opengever.task.transporter import IResponseTransporter
from opengever.task.util import add_simple_response
from opengever.testing import FunctionalTestCase
from plone.app.testing import TEST_USER_ID


class TestResponeTransporter(FunctionalTestCase):

    def setUp(self):
        super(TestResponeTransporter, self).setUp()

        create(Builder('ogds_user')
               .having(userid=u'peter.mueller', firstname=u'Peter',
                       lastname=u'M\xfcller'))
        create(Builder('ogds_user')
               .having(userid=u'hugo.boss', firstname=u'Hugo',
                       lastname=u'B\xf6ss'))

        self.task = create(Builder('task')
                           .having(responsible=u'hugo.boss',
                                   responsible_client=u'org-unit-1',
                                   deadline=date(2016, 03, 27))
                           .in_state('task-state-in-progress'))
        add_simple_response(self.task,
                            text=u'Ich \xfcbernehme diese Aufgabe',
                            transition='task-transition-open-in-progress')

    def test_send_responses(self):
        copy = create(Builder('task')
                      .in_state('task-state-in-progress')
                      .having(responsible_client=u'org-unit-1'))
        IResponseTransporter(self.task).send_responses(
            'admin-unit-1', copy.get_physical_path())

        responses = IResponseContainer(copy)
        self.assertEquals(1, len(responses))
        self.assertEquals('task-transition-open-in-progress', responses.list()[0].transition)
        self.assertEquals(u'Ich \xfcbernehme diese Aufgabe', responses.list()[0].text)
        self.assertEquals(TEST_USER_ID, responses.list()[0].creator)

    def test_get_responses(self):
        copy = create(Builder('task')
                      .in_state('task-state-in-progress')
                      .having(responsible_client=u'org-unit-1'))
        IResponseTransporter(copy).get_responses(
            'admin-unit-1', self.task.get_physical_path(), {})

        responses = IResponseContainer(copy)
        self.assertEquals(1, len(responses))
        self.assertEquals('task-transition-open-in-progress', responses.list()[0].transition)
        self.assertEquals(u'Ich \xfcbernehme diese Aufgabe', responses.list()[0].text)
        self.assertEquals(TEST_USER_ID, responses.list()[0].creator)

    def test_syncing_response_changes(self):
        add_simple_response(self.task,
                            text=u'Neu zugewiesen',
                            field_changes=[(ITask['responsible'], 'peter.mueller'),
                                           (ITask['responsible_client'], 'org-unit-2')],
                            transition='task-transition-reassign',)

        copy = create(Builder('task')
                      .in_state('task-state-in-progress')
                      .having(responsible_client=u'org-unit-1'))
        IResponseTransporter(self.task).send_responses(
            'admin-unit-1', copy.get_physical_path())

        self.assertEquals([{u'after': u'peter.mueller',
                            u'field_id': u'responsible',
                            u'field_title': u'label_responsible',
                            u'before': u'hugo.boss'},
                           {u'after': u'org-unit-2',
                            u'field_id': u'responsible_client',
                            u'field_title': u'label_resonsible_client',
                            u'before': u'org-unit-1'}],
                          IResponseContainer(copy).list()[1].changes)

    def test_deadline_change_synchronisation(self):
        IDeadlineModifier(self.task).modify_deadline(
            date(2016, 03, 29),
            u'Frist wurde verschoben.',
            u'task-transition-modify-deadline')

        copy = create(Builder('task')
                      .in_state('task-state-in-progress')
                      .having(responsible_client=u'org-unit-1'))
        IResponseTransporter(self.task).send_responses(
            'admin-unit-1', copy.get_physical_path())

        self.assertEquals(
            [{u'after': date(2016, 03, 29),
              u'field_id': u'deadline',
              u'field_title': u'label_deadline',
              u'before': date(2016, 03, 27)}],
            IResponseContainer(copy).list()[1].changes)
