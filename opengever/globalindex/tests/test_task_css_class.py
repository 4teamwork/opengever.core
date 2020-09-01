from ftw.builder import Builder
from ftw.builder import create
from opengever.inbox import FORWARDING_TASK_TYPE_ID
from opengever.testing import FunctionalTestCase


class TestTaskCssClass(FunctionalTestCase):

    def setUp(self):
        super(TestTaskCssClass, self).setUp()

        additional_admin_unit = create(Builder('admin_unit').id(u'additional'))
        create(Builder('org_unit').id(u'additional')
               .having(admin_unit=additional_admin_unit))

    def test_forwarding_class(self):
        forwarding = create(Builder('globalindex_task')
                            .having(int_id=123, sequence_number=123,
                                    task_type=FORWARDING_TASK_TYPE_ID,
                                    assigned_org_unit='org-unit-1',
                                    issuing_org_unit='org-unit-1',
                                    admin_unit_id='foo'))

        self.assertEqual('contenttype-opengever-inbox-forwarding',
                         forwarding.get_css_class())

    def test_remote_forwardings_has_forwarding_class(self):
        remote_forwarding = create(Builder('globalindex_task')
                                   .having(int_id=123, sequence_number=123,
                                           admin_unit_id='admin-unit-1',
                                           task_type=FORWARDING_TASK_TYPE_ID,
                                           issuing_org_unit='org-unit-1',
                                           assigned_org_unit=u'additional'))

        self.assertEqual('contenttype-opengever-inbox-forwarding',
                         remote_forwarding.get_css_class())

    def test_subtask_class(self):
        subtask = create(Builder('globalindex_task')
                         .having(int_id=123, sequence_number=123,
                                 admin_unit_id='admin-unit-1',
                                 assigned_org_unit='org-unit-1',
                                 issuing_org_unit='org-unit-1',
                                 is_subtask=True))

        self.assertEqual('contenttype-opengever-task-sub-task', subtask.get_css_class())

    def test_remote_task_class(self):
        remote_task = create(Builder('globalindex_task')
                             .having(int_id=123, sequence_number=123,
                                     admin_unit_id='additional',
                                     issuing_org_unit='additional',
                                     assigned_org_unit='org-unit-1'))

        self.assertEqual('contenttype-opengever-task-remote-task', remote_task.get_css_class())

    def test_remote_subtask_is_marked_as_subtask_when_admin_unit_is_the_current_one(self):
        remote_task = create(Builder('globalindex_task')
                             .having(int_id=123, sequence_number=123,
                                     is_subtask=True,
                                     admin_unit_id='admin-unit-1',
                                     issuing_org_unit='org-unit-1',
                                     assigned_org_unit='additional'))

        self.assertEqual('contenttype-opengever-task-sub-task', remote_task.get_css_class())

    def test_remote_subtask_is_marked_as_remote_task_when_admin_unit_is_a_remote_one(self):
        remote_task = create(Builder('globalindex_task')
                             .having(int_id=123, sequence_number=123,
                                     is_subtask=True,
                                     admin_unit_id='additional',
                                     issuing_org_unit='additional',
                                     assigned_org_unit='org-unit-1'))
        self.assertEqual('contenttype-opengever-task-remote-task', remote_task.get_css_class())

    def test_normal_task_classk(self):
        task = create(Builder('globalindex_task')
                      .having(int_id=123, sequence_number=123,
                              admin_unit_id='admin-unit-1',
                              issuing_org_unit='org-unit-1',
                              assigned_org_unit='org-unit-1'))

        self.assertEqual('contenttype-opengever-task-task',
                         task.get_css_class())
