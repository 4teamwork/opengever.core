from datetime import date
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.base.oguid import Oguid
from opengever.base.role_assignments import ASSIGNMENT_VIA_SHARING
from opengever.base.role_assignments import ASSIGNMENT_VIA_TASK
from opengever.base.role_assignments import ASSIGNMENT_VIA_TASK_AGENCY
from opengever.base.role_assignments import RoleAssignmentManager
from opengever.testing import IntegrationTestCase


class TestRoleAssignmentManager(IntegrationTestCase):

    def test_add_register_assignment_in_the_storage(self):
        self.login(self.regular_user)

        manager = RoleAssignmentManager(self.empty_dossier)
        manager.add_or_update(self.secretariat_user.id,
                    ['Editor', 'Contributor', 'Reader'],
                    ASSIGNMENT_VIA_TASK, self.task)

        self.assertEquals(
            [{'principal': self.secretariat_user.id,
              'roles': ['Editor', 'Contributor', 'Reader'],
              'cause': ASSIGNMENT_VIA_TASK,
              'reference': Oguid.for_object(self.task).id}],
            manager.storage._storage())

    def test_add_updates_when_assignment_exists(self):
        self.login(self.regular_user)

        manager = RoleAssignmentManager(self.empty_dossier)
        manager.add_or_update(self.secretariat_user.id,
                    ['Editor', 'Contributor', 'Reader'],
                    ASSIGNMENT_VIA_SHARING)

        # update
        manager.add_or_update(self.secretariat_user.id,
                    ['Reader'],
                    ASSIGNMENT_VIA_SHARING)

        self.assertEquals(
            [{'principal': self.secretariat_user.id,
              'roles': ['Reader', ],
              'cause': ASSIGNMENT_VIA_SHARING,
              'reference': None}],
            manager.storage._storage())

    def test_sets_local_roles_when_adding(self):
        self.login(self.regular_user)
        manager = RoleAssignmentManager(self.empty_dossier)

        manager.add_or_update(self.secretariat_user.id,
                    ['Editor', 'Contributor', 'Reader'],
                    ASSIGNMENT_VIA_SHARING)
        manager.add_or_update(self.secretariat_user.id,
                    ['Reader'], ASSIGNMENT_VIA_TASK, self.task)
        manager.add_or_update(self.regular_user.id,
                    ['Publisher', 'Reviewer'], ASSIGNMENT_VIA_SHARING)

        self.assertEquals(
            (('jurgen.konig', ('Contributor', 'Editor', 'Reader')),
             ('kathi.barfuss', ('Publisher', 'Reviewer')),
             ('robert.ziegler', ('Owner',))),
            self.empty_dossier.get_local_roles())

    def test_does_not_clean_owner_roles_when_adding(self):
        self.login(self.regular_user)

        manager = RoleAssignmentManager(self.empty_dossier)

        manager.add_or_update(self.secretariat_user.id,
                    ['Editor', 'Contributor', 'Reader'],
                    ASSIGNMENT_VIA_SHARING)
        manager.add_or_update(self.secretariat_user.id,
                    ['Reader'], ASSIGNMENT_VIA_TASK, self.task)
        manager.add_or_update(self.regular_user.id,
                    ['Publisher', 'Reviewer'], ASSIGNMENT_VIA_SHARING)

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
              'cause': ASSIGNMENT_VIA_TASK,
              'reference': Oguid.for_object(task).id}],
            RoleAssignmentManager(task).storage._storage())

        self.assertEquals(
            [{'principal': self.regular_user.id,
              'roles': ['Reader', 'Editor'],
              'cause': ASSIGNMENT_VIA_TASK,
              'reference': Oguid.for_object(task).id}],
            RoleAssignmentManager(document).storage._storage())

        self.assertEquals(
            [{'principal': self.regular_user.id,
              'roles': ['Contributor'],
              'cause': ASSIGNMENT_VIA_TASK,
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
              'cause': ASSIGNMENT_VIA_TASK,
              'reference': Oguid.for_object(task).id},
             {'principal': u'fa_inbox_users',
              'roles': ['Editor'],
              'cause': ASSIGNMENT_VIA_TASK_AGENCY,
              'reference': Oguid.for_object(task).id}],
            RoleAssignmentManager(task).storage._storage())

        self.assertItemsEqual(
            [{'principal': self.regular_user.id,
              'roles': ['Reader', 'Editor'],
              'cause': ASSIGNMENT_VIA_TASK,
              'reference': Oguid.for_object(task).id},
             {'principal': u'fa_inbox_users',
              'roles': ['Reader', 'Editor'],
              'cause': ASSIGNMENT_VIA_TASK_AGENCY,
              'reference': Oguid.for_object(task).id}],
            RoleAssignmentManager(document).storage._storage())

        self.assertItemsEqual(
            [{'principal': self.regular_user.id,
              'roles': ['Contributor'],
              'cause': ASSIGNMENT_VIA_TASK,
              'reference': Oguid.for_object(task).id},
             {'principal': u'fa_inbox_users',
              'roles': ['Contributor'],
              'cause': ASSIGNMENT_VIA_TASK_AGENCY,
              'reference': Oguid.for_object(task).id}],
            RoleAssignmentManager(self.empty_dossier).storage._storage())


class TestManageRoleAssignmentsView(IntegrationTestCase):

    @browsing
    def test_is_only_visible_for_managers(self, browser):
        self.login(self.regular_user, browser=browser)
        with browser.expect_unauthorized():
            browser.open(self.dossier, view='manage-role-assignments')

        self.login(self.administrator, browser=browser)
        with browser.expect_unauthorized():
            browser.open(self.dossier, view='manage-role-assignments')

        self.login(self.manager, browser=browser)
        browser.open(self.dossier, view='manage-role-assignments')
        self.assertEquals(200, browser.status_code)

    @browsing
    def test_returns_all_assignments_of_the_current_user(self, browser):
        self.login(self.manager, browser=browser)
        browser.open(self.dossier, view='manage-role-assignments')
        expected_assignments = [
            {
                u'cause': {u'id': 1, u'title': u'By task'},
                u'roles': [u'Contributor'],
                u'reference': {u'url': self.task.absolute_url(), u'title': u'Vertragsentwurf \xdcberpr\xfcfen'},
                u'principal': u'kathi.barfuss',
            },
            {
                u'cause': {u'id': 1, 'title': u'By task'},
                u'roles': [u'Contributor'],
                u'reference': {
                    u'url': self.subtask.absolute_url(),
                    u'title': u'Rechtliche Grundlagen in Vertragsentwurf \xdcberpr\xfcfen',
                    },
                u'principal': u'kathi.barfuss',
            },
            {
                u'cause': {u'id': 1, u'title': u'By task'},
                u'roles': [u'Contributor'],
                u'reference': {u'url': self.sequential_task.absolute_url(), u'title': u'Personaleintritt'},
                u'principal': u'kathi.barfuss',
            },
            {
                u'cause': {u'id': 1, u'title': u'By task'},
                u'roles': [u'Contributor'],
                u'reference': {u'url': self.seq_subtask_1.absolute_url(), u'title': u'Mitarbeiter Dossier generieren'},
                u'principal': u'kathi.barfuss',
            },
            {
                u'cause': {u'id': 1, u'title': u'By task'},
                u'roles': [u'Contributor'],
                u'reference': {u'url': self.seq_subtask_2.absolute_url(), u'title': u'Arbeitsplatz vorbereiten'},
                u'principal': u'kathi.barfuss',
            },
            {
                u'cause': {u'id': 1, u'title': u'By task'},
                u'roles': [u'Contributor'],
                u'reference': {
                    u'url': self.seq_subtask_3.absolute_url(),
                    u'title': u'Vorstellungsrunde bei anderen Mitarbeitern',
                },
                u'principal': u'kathi.barfuss',
            },
            {
                u'cause': {u'id': 1, u'title': u'By task'},
                u'roles': [u'Contributor'],
                u'reference': {
                    u'url': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/task-11',
                    u'title': u'Vertragsentw\xfcrfe 2018',
                },
                u'principal': u'kathi.barfuss',
            }
        ]
        self.assertEquals(expected_assignments, browser.json)
