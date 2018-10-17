from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.base.role_assignments import ASSIGNMENT_VIA_SHARING
from opengever.base.role_assignments import ASSIGNMENT_VIA_TASK
from opengever.base.role_assignments import ASSIGNMENT_VIA_TASK_AGENCY
from opengever.base.role_assignments import RoleAssignmentManager
from opengever.base.role_assignments import SharingRoleAssignment
from opengever.base.role_assignments import TaskRoleAssignment
from opengever.testing import IntegrationTestCase
from plone import api
import json


class TestOpengeverSharingIntegration(IntegrationTestCase):

    @browsing
    def test_available_roles_on_a_dossier(self, browser):
        self.login(self.administrator, browser=browser)

        browser.open(self.dossier, view='@sharing',
                     method='GET', headers={'Accept': 'application/json'})

        self.assertEqual(
            [u'Reader', u'Contributor', u'Editor', u'Reviewer', u'Publisher'],
            [role['id'] for role in browser.json.get('available_roles')])

    @browsing
    def test_available_roles_on_a_templatedossier(self, browser):
        self.login(self.administrator, browser=browser)

        browser.open(self.templates, view='@sharing',
                     method='GET', headers={'Accept': 'application/json'})

        self.assertEqual(
            [u'Reader', u'Contributor', u'Editor'],
            [role['id'] for role in browser.json.get('available_roles')])

    @browsing
    def test_available_roles_on_commiteecontainer(self, browser):
        self.login(self.manager, browser=browser)

        browser.open(self.committee_container, view='@sharing',
                     method='GET', headers={'Accept': 'application/json'})

        self.assertEqual(
            [u'MeetingUser', u'CommitteeAdministrator'],
            [role['id'] for role in browser.json.get('available_roles')])

    @browsing
    def test_consider_the_ignore_permissions_flag(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.dossier, view='@sharing',
                     method='GET', headers={'Accept': 'application/json'})
        self.assertEquals(
            {u'available_roles': [], u'inherit': True, u'entries': []},
            browser.json)

        browser.open(self.dossier, view='@sharing?ignore_permissions=1',
                     method='GET', headers={'Accept': 'application/json'})

        self.assertEqual(
            [u'Reader', u'Contributor', u'Editor',
             u'Reviewer', u'Publisher', u'DossierManager'],
            [role['id'] for role in browser.json.get('available_roles')])
        self.assertEqual(
            [u'Publisher', u'DossierManager', u'Editor',
             u'Reader', u'Contributor', u'Reviewer'],
            browser.json['entries'][0]['roles'].keys())

    @browsing
    def test_sets_role_assignments_and_updates_local_roles(self, browser):
        self.login(self.administrator, browser=browser)

        data = json.dumps({
            "entries": [
                {"id": self.regular_user.id,
                 "roles": {"Contributor": False,
                           "Editor": False,
                           "Reader": True,
                           "Reviewer": False,
                           "Publisher": False},
                 "type": "user"},
                {"id": self.secretariat_user.id,
                 "roles": {"Contributor": True,
                           "Editor": True,
                           "Reader": True,
                           "Reviewer": False,
                           "Publisher": False},
                 "type": "user"},
            ],
            "inherit": True})

        browser.open(self.empty_dossier, data, view='@sharing', method='POST',
                     headers={'Accept': 'application/json',
                              'Content-Type': 'application/json'})

        self.assertEquals(
            ((self.secretariat_user.id, (u'Contributor', u'Editor', u'Reader')),
             (self.regular_user.id, (u'Reader',)),
             ('robert.ziegler', ('Owner',))),
            self.empty_dossier.get_local_roles())

        self.assertEquals(
            [{'cause': ASSIGNMENT_VIA_SHARING,
              'roles': [u'Reader'],
              'reference': None,
              'principal': self.regular_user.id},
             {'cause': ASSIGNMENT_VIA_SHARING,
              'roles': [u'Contributor', u'Editor', u'Reader'],
              'reference': None,
              'principal': self.secretariat_user.id}],
            RoleAssignmentManager(self.empty_dossier).storage._storage())

    @browsing
    def test_stop_inheritance(self, browser):
        self.login(self.administrator, browser=browser)

        data = json.dumps({"entries": [], "inherit": False})

        browser.open(self.empty_dossier, data, view='@sharing', method='POST',
                     headers={'Accept': 'application/json',
                              'Content-Type': 'application/json'})

        self.assertTrue(self.empty_dossier.__ac_local_roles_block__)

    @browsing
    def test_stop_inheritance_fallback(self, browser):
        self.login(self.dossier_responsible, browser=browser)

        acl_users = api.portal.get_tool('acl_users')

        roles =['Member', 'Role Manager']
        acl_users.userFolderEditUser(self.dossier_responsible.id, None, list(roles), [])

        data = json.dumps({"entries": [], "inherit": False})
        browser.open(self.empty_dossier, data, view='@sharing', method='POST',headers={'Accept': 'application/json','Content-Type': 'application/json'})

        self.assertTrue(self.empty_dossier.__ac_local_roles_block__)
        self.assertEquals(
            ((self.dossier_responsible.id,
              ('Contributor', 'Owner', 'Editor', 'Reader')),),
            self.empty_dossier.get_local_roles())

        self.assertEquals(
            [{'cause': 3,
              'roles': ['Contributor', 'Editor', 'Reader', 'Owner'],
              'reference': None, 'principal': 'robert.ziegler'}],
            RoleAssignmentManager(self.empty_dossier).storage._storage())

    @browsing
    def test_stop_inheritance_fallback_is_skipped_for_administrators(self, browser):
        self.login(self.administrator, browser=browser)

        data = json.dumps({"entries": [], "inherit": False})
        browser.open(self.empty_dossier, data, view='@sharing', method='POST',
                     headers={'Accept': 'application/json',
                              'Content-Type': 'application/json'})

        self.assertTrue(self.empty_dossier.__ac_local_roles_block__)
        self.assertEquals([], RoleAssignmentManager(self.empty_dossier).storage._storage())

    @browsing
    def test_sharing_view_only_returns_users_from_current_admin_unit(self, browser):
        self.login(self.regular_user, browser=browser)

        # create other group, from different admin unit
        other_admin_unit = create(Builder('admin_unit').id('other'))
        create(Builder('user')
               .named(u'Hans', u'M\xfcller')
               .with_userid('hans.mueller'))
        hans = create(Builder('ogds_user')
                      .id('hans.mueller')
                      .having(firstname='Hans', lastname=u'M\xfcller'))
        create(Builder('org_unit')
               .id(u'otherunit')
               .having(admin_unit=other_admin_unit)
               .assign_users([hans]))

        browser.open(self.empty_dossier, view='@sharing?search=Test',
                     method='Get', headers={'Accept': 'application/json'})
        self.assertEquals(
            {u'available_roles': [], u'inherit': True, u'entries': []},
            browser.json)

        browser.open(self.empty_dossier, view='@sharing?search=Robert',
                     method='Get', headers={'Accept': 'application/json'})
        self.assertEquals(
            {u'available_roles': [],
             u'inherit': True,
             u'entries': [
                 {u'roles': {},
                  u'computed_roles': {},
                  u'automatic_roles': {},
                  u'title': u'Ziegler Robert',
                  u'url': u'http://nohost/plone/@@user-details-plain/robert.ziegler',
                  u'login': u'robert.ziegler',
                  u'type': u'user',
                  u'id': u'robert.ziegler'}]},
            browser.json)

    @browsing
    def test_sharing_view_extends_information(self, browser):
        self.login(self.administrator, browser=browser)

        manager = RoleAssignmentManager(self.empty_dossier)
        manager.add_or_update_assignment(
            TaskRoleAssignment(
                self.regular_user.id, ['Contributor'], self.task))
        manager.add_or_update_assignment(
            SharingRoleAssignment(
                self.regular_user.id, ['Reader', 'Editor', 'Contributor']))

        browser.open(self.empty_dossier, view='@sharing',
                     method='Get', headers={'Accept': 'application/json'})

        entries = browser.json['entries']

        self.assertEquals(
            {u'automatic_roles': {u'Contributor': True,
                                  u'Editor': False,
                                  u'Publisher': False,
                                  u'Reader': False,
                                  u'Reviewer': False},
             u'computed_roles': {u'Contributor': True,
                                 u'Editor': True,
                                 u'Publisher': False,
                                 u'Reader': True,
                                 u'Reviewer': False},
             u'disabled': False,
             u'id': u'kathi.barfuss',
             u'login': u'kathi.barfuss',
             u'roles': {u'Contributor': True,
                        u'Editor': True,
                        u'Publisher': False,
                        u'Reader': True,
                        u'Reviewer': False},
             u'title': u'B\xe4rfuss K\xe4thi',
             u'type': u'user',
             u'url': u'http://nohost/plone/@@user-details-plain/kathi.barfuss'},
            [item for item in entries if item['id'] == self.regular_user.id][0])

    @browsing
    def test_sharing_view_handles_groupids_with_spaces(self, browser):
        self.login(self.administrator, browser=browser)

        group_id = 'group with spaces'
        create(Builder('group')
               .with_groupid(group_id)
               .having(title='Group with sapces'))

        manager = RoleAssignmentManager(self.empty_dossier)
        manager.add_or_update_assignment(
            TaskRoleAssignment(group_id, ['Reader'], self.task))

        browser.open(self.empty_dossier, view='@sharing',
                     method='Get', headers={'Accept': 'application/json'})

        entry = [entry for entry in browser.json['entries']
                 if entry['id'] == u'group with spaces'][0]
        self.assertEquals(
            u'http://nohost/plone/@@list_groupmembers?group=group+with+spaces',
            entry['url'])


class TestRoleAssignmentsGet(IntegrationTestCase):

    @browsing
    def test_returns_serialized_assignments(self, browser):
        self.login(self.secretariat_user, browser=browser)
        manager = RoleAssignmentManager(self.empty_dossier)
        manager.add_or_update(self.regular_user.id, ['Editor'],
                    ASSIGNMENT_VIA_TASK, reference=self.task)
        manager.add_or_update(self.regular_user.id, ['Reader'],
                              ASSIGNMENT_VIA_TASK_AGENCY)

        browser.open(self.empty_dossier,
                     view='@role-assignments/{}'.format(self.regular_user.id),
                     method='Get', headers={'Accept': 'application/json'})

        self.assertEquals(
            [{u'cause': {
                u'id': ASSIGNMENT_VIA_TASK,
                u'title': u'By task'},
              u'roles': [u'Editor'],
              u'reference': {
                  u'url': self.task.absolute_url(),
                  u'title': self.task.title},
              u'principal': u'kathi.barfuss'},
             {u'cause': {
                 u'id': ASSIGNMENT_VIA_TASK_AGENCY,
                 u'title': u'By task agency'},
              u'roles': [u'Reader'],
              u'reference': None,
              u'principal': u'kathi.barfuss'}],
            browser.json)

    @browsing
    def test_sharing_assignments_get_sipped(self, browser):
        self.login(self.secretariat_user, browser=browser)
        manager = RoleAssignmentManager(self.empty_dossier)
        manager.add_or_update(self.regular_user.id, ['Editor'],
                              ASSIGNMENT_VIA_TASK, reference=self.task)
        manager.add_or_update(self.regular_user.id, ['Reader'],
                              ASSIGNMENT_VIA_SHARING)

        browser.open(self.empty_dossier,
                     view='@role-assignments/{}'.format(self.regular_user.id),
                     method='Get', headers={'Accept': 'application/json'})

        self.assertEquals(
            [{u'cause': {
                u'id': ASSIGNMENT_VIA_TASK,
                u'title': u'By task'},
              u'roles': [u'Editor'],
              u'reference': {
                  u'url': self.task.absolute_url(),
                  u'title': self.task.title},
              u'principal': u'kathi.barfuss'}],
            browser.json)
