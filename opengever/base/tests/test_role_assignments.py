from datetime import date
from ftw.builder import Builder
from ftw.builder import create
from opengever.base.oguid import Oguid
from opengever.base.role_assignments import ASSIGNNMENT_VIA_SHARING
from opengever.base.role_assignments import ASSIGNNMENT_VIA_TASK
from opengever.base.role_assignments import ASSIGNNMENT_VIA_TASK_AGENCY
from opengever.base.role_assignments import RoleAssignmentManager
from opengever.testing import IntegrationTestCase


class TestRoleAssignmentManager(IntegrationTestCase):

    def test_add_register_assignment_in_the_storage(self):
        self.login(self.regular_user)

        manager = RoleAssignmentManager(self.empty_dossier)
        manager.add(self.secretariat_user.id,
                    ['Editor', 'Contributor', 'Reader'],
                    ASSIGNNMENT_VIA_TASK, self.task)

        self.assertEquals(
            [{'principal': self.secretariat_user.id,
              'roles': ['Editor', 'Contributor', 'Reader'],
              'cause': ASSIGNNMENT_VIA_TASK,
              'reference': Oguid.for_object(self.task).id}],
            manager.storage._storage())

    def test_add_updates_when_assignment_exists(self):
        self.login(self.regular_user)

        manager = RoleAssignmentManager(self.empty_dossier)
        manager.add(self.secretariat_user.id,
                    ['Editor', 'Contributor', 'Reader'],
                    ASSIGNNMENT_VIA_SHARING)

        # update
        manager.add(self.secretariat_user.id,
                    ['Reader'],
                    ASSIGNNMENT_VIA_SHARING)

        self.assertEquals(
            [{'principal': self.secretariat_user.id,
              'roles': ['Reader', ],
              'cause': ASSIGNNMENT_VIA_SHARING,
              'reference': None}],
            manager.storage._storage())

    def test_sets_local_roles_when_adding(self):
        self.login(self.regular_user)
        manager = RoleAssignmentManager(self.empty_dossier)

        manager.add(self.secretariat_user.id,
                    ['Editor', 'Contributor', 'Reader'],
                    ASSIGNNMENT_VIA_SHARING)
        manager.add(self.secretariat_user.id,
                    ['Reader'], ASSIGNNMENT_VIA_TASK, self.task)
        manager.add(self.regular_user.id,
                    ['Publisher', 'Reviewer'], ASSIGNNMENT_VIA_SHARING)

        self.assertEquals(
            (('jurgen.konig', ('Contributor', 'Editor', 'Reader')),
             ('kathi.barfuss', ('Publisher', 'Reviewer')),
             ('robert.ziegler', ('Owner',))),
            self.empty_dossier.get_local_roles())

    def test_does_not_clean_owner_roles_when_adding(self):
        self.login(self.regular_user)

        manager = RoleAssignmentManager(self.empty_dossier)

        manager.add(self.secretariat_user.id,
                    ['Editor', 'Contributor', 'Reader'],
                    ASSIGNNMENT_VIA_SHARING)
        manager.add(self.secretariat_user.id,
                    ['Reader'], ASSIGNNMENT_VIA_TASK, self.task)
        manager.add(self.regular_user.id,
                    ['Publisher', 'Reviewer'], ASSIGNNMENT_VIA_SHARING)

        self.assertEquals(
            (('jurgen.konig', ('Contributor', 'Editor', 'Reader')),
             ('kathi.barfuss', ('Publisher', 'Reviewer')),
             ('robert.ziegler', ('Owner',))),
            self.empty_dossier.get_local_roles())

    def test_role_assignmets_on_tasks(self):
        self.login(self.regular_user)
        document = create(Builder('document')
                          .within(self.empty_dossier)
                          .titled(u'Vertr\xe4gsentwurf'))
        task = create(Builder('task')
                      .within(self.empty_dossier)
                      .titled(u'Vertragsentwurf \xdcberpr\xfcfen')
                      .having(
                          responsible_client='fa',
                          responsible=self.regular_user.getId(),
                          issuer=self.dossier_responsible.getId(),
                          task_type='correction',
                          deadline=date(2016, 11, 1))
                      .in_state('task-state-in-progress')
                      .relate_to(document))

        self.assertEquals(
            [{'principal': self.regular_user.id,
              'roles': ['Editor'],
              'cause': ASSIGNNMENT_VIA_TASK,
              'reference': Oguid.for_object(task).id}],
            RoleAssignmentManager(task).storage._storage())

        self.assertEquals(
            [{'principal': self.regular_user.id,
              'roles': ['Reader', 'Editor'],
              'cause': ASSIGNNMENT_VIA_TASK,
              'reference': Oguid.for_object(task).id}],
            RoleAssignmentManager(document).storage._storage())

        self.assertEquals(
            [{'principal': self.regular_user.id,
              'roles': ['Contributor'],
              'cause': ASSIGNNMENT_VIA_TASK,
              'reference': Oguid.for_object(task).id}],
            RoleAssignmentManager(self.empty_dossier).storage._storage())

    def test_role_assignmets_on_tasks_with_inbox_agency(self):
        self.login(self.regular_user)
        self.add_additional_org_unit()

        document = create(Builder('document')
                          .within(self.empty_dossier)
                          .titled(u'Vertr\xe4gsentwurf'))
        task = create(Builder('task')
                      .within(self.empty_dossier)
                      .titled(u'Vertragsentwurf \xdcberpr\xfcfen')
                      .having(
                          responsible_client='fa',
                          responsible=self.regular_user.getId(),
                          issuer=self.dossier_responsible.getId(),
                          task_type='correction',
                          deadline=date(2016, 11, 1))
                      .in_state('task-state-in-progress')
                      .relate_to(document))

        self.assertItemsEqual(
            [{'principal': self.regular_user.id,
              'roles': ['Editor'],
              'cause': ASSIGNNMENT_VIA_TASK,
              'reference': Oguid.for_object(task).id},
             {'principal': u'fa_inbox_users',
              'roles': ['Editor'],
              'cause': ASSIGNNMENT_VIA_TASK_AGENCY,
              'reference': Oguid.for_object(task).id}],
            RoleAssignmentManager(task).storage._storage())

        self.assertItemsEqual(
            [{'principal': self.regular_user.id,
              'roles': ['Reader', 'Editor'],
              'cause': ASSIGNNMENT_VIA_TASK,
              'reference': Oguid.for_object(task).id},
             {'principal': u'fa_inbox_users',
              'roles': ['Reader', 'Editor'],
              'cause': ASSIGNNMENT_VIA_TASK_AGENCY,
              'reference': Oguid.for_object(task).id}],
            RoleAssignmentManager(document).storage._storage())

        self.assertItemsEqual(
            [{'principal': self.regular_user.id,
              'roles': ['Contributor'],
              'cause': ASSIGNNMENT_VIA_TASK,
              'reference': Oguid.for_object(task).id},
             {'principal': u'fa_inbox_users',
              'roles': ['Contributor'],
              'cause': ASSIGNNMENT_VIA_TASK_AGENCY,
              'reference': Oguid.for_object(task).id}],
            RoleAssignmentManager(self.empty_dossier).storage._storage())
