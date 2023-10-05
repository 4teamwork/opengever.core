from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.exceptions import InsufficientPrivileges
from opengever.base.role_assignments import ASSIGNMENT_VIA_SHARING
from opengever.base.role_assignments import ASSIGNMENT_VIA_TASK
from opengever.base.role_assignments import ASSIGNMENT_VIA_TASK_AGENCY
from opengever.base.role_assignments import RoleAssignmentManager
from opengever.base.role_assignments import SharingRoleAssignment
from opengever.base.role_assignments import TaskRoleAssignment
from opengever.ogds.base.interfaces import IOGDSSyncConfiguration
from opengever.testing import IntegrationTestCase
from plone import api
from urllib import urlencode
import json


class TestOpengeverSharing(IntegrationTestCase):

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
    def test_available_roles_on_committeecontainer(self, browser):
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
            [u'Reader', u'Contributor', u'Editor', u'Reviewer',
             u'Publisher', u'DossierManager', u'TaskResponsible'],
            [role['id'] for role in browser.json.get('available_roles')])
        self.assertEqual(
            [u'Publisher', u'TaskResponsible', u'DossierManager', u'Editor',
             u'Reader', u'Contributor', u'Reviewer'],
            browser.json['entries'][0]['roles'].keys())

    @browsing
    def test_show_role_manager_on_dossier_when_feature_active(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.dossier, view='@sharing?ignore_permissions=1',
                     method='GET', headers={'Accept': 'application/json'})

        self.assertEqual(
            [u'Reader', u'Contributor', u'Editor', u'Reviewer',
             u'Publisher', u'DossierManager', u'TaskResponsible'],
            [role['id'] for role in browser.json.get('available_roles')])
        self.assertEqual(
            [u'Publisher', u'TaskResponsible', u'DossierManager', u'Editor',
             u'Reader', u'Contributor', u'Reviewer'],
            browser.json['entries'][0]['roles'].keys())

        self.activate_feature("grant_role_manager_to_responsible")
        browser.open(self.dossier, view='@sharing?ignore_permissions=1',
                     method='GET', headers={'Accept': 'application/json'})

        self.assertEqual(
            [u'Reader', u'Contributor', u'Editor', u'Reviewer', u'Publisher',
             u'DossierManager', u'TaskResponsible', u'Role Manager'],
            [role['id'] for role in browser.json.get('available_roles')])
        self.assertEqual(
            [u'Publisher', u'Role Manager', u'TaskResponsible', u'DossierManager',
             u'Editor', u'Reader', u'Contributor', u'Reviewer'],
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
    def test_only_manager_can_grant_task_responsible(self, browser):
        self.login(self.administrator, browser=browser)

        data = json.dumps({
            "entries": [
                {"id": self.regular_user.id,
                 "roles": {"TaskResponsible": True,
                           "Contributor": False,
                           "Editor": False,
                           "Reader": True,
                           "Reviewer": False,
                           "Publisher": False},
                 "type": "user"},
            ],
            "inherit": True})

        browser.open(self.empty_dossier, data, view='@sharing',
                     method='POST', headers=self.api_headers)
        self.assertEqual(((u'kathi.barfuss', (u'Reader',)),
                          ('robert.ziegler', ('Owner',))),
                         self.empty_dossier.get_local_roles())

        self.login(self.manager, browser=browser)
        browser.open(self.empty_dossier, data, view='@sharing',
                     method='POST', headers=self.api_headers)
        self.assertEqual(((u'kathi.barfuss', (u'TaskResponsible', u'Reader')),
                          ('robert.ziegler', ('Owner',))),
                         self.empty_dossier.get_local_roles())

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

        roles = ['Member', 'Role Manager']
        acl_users.userFolderEditUser(self.dossier_responsible.id, None, list(roles), [])

        data = json.dumps({"entries": [], "inherit": False})
        browser.open(self.empty_dossier, data, view='@sharing', method='POST',
                     headers={'Accept': 'application/json', 'Content-Type': 'application/json'})

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
            {u'available_roles': [], u'items_total': 0, u'inherit': True, u'items': []},
            browser.json)

        browser.open(self.empty_dossier, view='@sharing?search=Robert',
                     method='Get', headers={'Accept': 'application/json'})
        self.assertEquals(
            {u'available_roles': [],
             u'items_total': 1,
             u'inherit': True,
             u'items': [
                 {u'roles': {},
                  u'computed_roles': {},
                  u'automatic_roles': {},
                  u'title': u'Ziegler Robert',
                  u'url': u'http://nohost/plone/@@user-details-plain/robert.ziegler',
                  u'login': u'robert.ziegler',
                  u'ogds_summary': {u'@id': u'http://nohost/plone/@ogds-users/robert.ziegler',
                                    u'@type': u'virtual.ogds.user',
                                    u'active': True,
                                    u'department': None,
                                    u'directorate': None,
                                    u'email': u'robert.ziegler@gever.local',
                                    u'email2': None,
                                    u'firstname': u'Robert',
                                    u'job_title': None,
                                    u'lastname': u'Ziegler',
                                    u'phone_fax': None,
                                    u'phone_mobile': None,
                                    u'phone_office': None,
                                    u'title': u'Ziegler Robert',
                                    u'userid': u'robert.ziegler'},
                  u'actor': {u'@id': u'http://nohost/plone/@actors/robert.ziegler',
                             u'identifier': u'robert.ziegler'},
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
        manager.add_or_update_assignment(
            SharingRoleAssignment(
                u'projekt_a', ['Reader']))

        browser.open(self.empty_dossier, view='@sharing',
                     method='Get', headers={'Accept': 'application/json'})

        entries = browser.json['entries']

        self.assertEqual(
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
             u'ogds_summary': {u'@id': u'http://nohost/plone/@ogds-users/kathi.barfuss',
                               u'@type': u'virtual.ogds.user',
                               u'active': True,
                               u'department': u'Staatskanzlei',
                               u'directorate': u'Staatsarchiv',
                               u'email': u'foo@example.com',
                               u'email2': u'bar@example.com',
                               u'firstname': u'K\xe4thi',
                               u'last_login': None,
                               u'job_title': u'Gesch\xe4ftsf\xfchrerin',
                               u'lastname': u'B\xe4rfuss',
                               u'phone_fax': u'012 34 56 77',
                               u'phone_mobile': u'012 34 56 76',
                               u'phone_office': u'012 34 56 78',
                               u'title': u'B\xe4rfuss K\xe4thi',
                               u'userid': u'kathi.barfuss'},
             u'actor': {u'@id': u'http://nohost/plone/@actors/kathi.barfuss',
                        u'identifier': u'kathi.barfuss'},
             u'roles': {u'Contributor': True,
                        u'Editor': True,
                        u'Publisher': False,
                        u'Reader': True,
                        u'Reviewer': False},
             u'title': u'B\xe4rfuss K\xe4thi',
             u'type': u'user',
             u'url': u'http://nohost/plone/@@user-details-plain/kathi.barfuss'},
            [item for item in entries if item['id'] == self.regular_user.id][0])

        self.assertEqual(
          {u'automatic_roles': {u'Contributor': False,
                                u'Editor': False,
                                u'Publisher': False,
                                u'Reader': False,
                                u'Reviewer': False},
           u'computed_roles': {u'Contributor': False,
                               u'Editor': False,
                               u'Publisher': False,
                               u'Reader': True,
                               u'Reviewer': False},
           u'disabled': False,
           u'id': u'projekt_a',
           u'ogds_summary': {u'@id': u'http://nohost/plone/@ogds-groups/projekt_a',
                             u'@type': u'virtual.ogds.group',
                             u'active': True,
                             u'groupid': u'projekt_a',
                             u'groupurl': u'http://nohost/plone/@groups/projekt_a',
                             u'is_local': False,
                             u'title': u'Projekt A'},
           u'actor': {u'@id': u'http://nohost/plone/@actors/projekt_a',
                      u'identifier': u'projekt_a'},
           u'roles': {u'Contributor': False,
                      u'Editor': False,
                      u'Publisher': False,
                      u'Reader': True,
                      u'Reviewer': False},
           u'title': u'projekt_a',
           u'type': u'user',
           u'url': u'http://nohost/plone/@@list_groupmembers?group=projekt_a'},
          [item for item in entries if item['id'] == u'projekt_a'][0])

    @browsing
    def test_sharing_view_handles_groupids_with_spaces(self, browser):
        self.login(self.administrator, browser=browser)

        group_id = 'group with spaces'
        create(Builder('ogds_group')
               .having(groupid=group_id))

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

    @browsing
    def test_sharing_view_handles_inactive_group(self, browser):
        self.login(self.administrator, browser=browser)

        group_id = 'inactive group'
        create(Builder('ogds_group')
               .having(groupid=group_id, active=False, title='Inactive group'))

        manager = RoleAssignmentManager(self.empty_dossier)
        manager.add_or_update_assignment(
            TaskRoleAssignment(group_id, ['Reader'], self.task))

        browser.open(self.empty_dossier, view='@sharing',
                     method='Get', headers={'Accept': 'application/json'})

        entry = [entry for entry in browser.json['entries']
                 if entry['id'] == u'inactive group'][0]

        self.assertEquals(
            u'http://nohost/plone/@@list_groupmembers?group=inactive+group',
            entry['url'])

    @browsing
    def test_searches_also_for_group_description_if_configured(self, browser):
        self.login(self.administrator, browser=browser)

        group = api.group.get('rk_inbox_users')
        group.setGroupProperties({'description': 'K%C3%B6nizer Schulen'})

        browser.open(self.empty_dossier, view='@sharing?search=K%C3%B6niz',
                     method='Get', headers={'Accept': 'application/json'})

        self.assertNotIn('rk_inbox_users',
                         [aa.get('id') for aa in browser.json['items']])

        api.portal.set_registry_record(
            name='group_title_ldap_attribute',
            value=u'description', interface=IOGDSSyncConfiguration)

        browser.open(self.empty_dossier, view='@sharing?search=K%C3%B6niz',
                     method='Get', headers={'Accept': 'application/json'})

        self.assertIn('rk_inbox_users',
                      [aa.get('id') for aa in browser.json['items']])

    @browsing
    def test_search_result_is_batched(self, browser):
        self.login(self.administrator, browser=browser)

        browser.open(self.empty_dossier, view='@sharing?search=g&b_size=3',
                     method='Get', headers={'Accept': 'application/json'})

        result = browser.json
        self.assertEqual(22, result['items_total'])
        self.assertEqual(3, len(result['items']))
        self.assertIn('batching', result)

    @browsing
    def test_search_result_is_batched_for_empty_search_terms(self, browser):
        self.login(self.administrator, browser=browser)

        browser.open(self.empty_dossier, view='@sharing?search=&b_size=1',
                     method='Get', headers={'Accept': 'application/json'})

        result = browser.json

        self.assertIn('batching', result)

    @browsing
    def test_existing_settings_are_sorted_before_search_result(self, browser):
        self.login(self.administrator, browser=browser)

        browser.open(self.empty_dossier, view='@sharing',
                     method='Get', headers={'Accept': 'application/json'})

        self.assertEqual(
            [u'fa Users Group',
             u'Fischer J\xfcrgen',
             u'K\xf6nig J\xfcrgen'],
            [each["title"] for each in browser.json["entries"]])

        browser.open(self.empty_dossier, view='@sharing?search=in',
                     method='Get', headers={'Accept': 'application/json'})

        self.assertEqual(
            [u'fa Users Group',
             u'Fischer J\xfcrgen',
             u'K\xf6nig J\xfcrgen',
             u'Administrators',
             u'Site Administrators',
             u'fa Inbox Users Group',
             u'rk Inbox Users Group',
             u'Fr\xfchling F\xe4ivel',
             u'Hugentobler Fridolin',
             u'Schr\xf6dinger B\xe9atrice',
             u'User Inactive'],
            [each["title"] for each in browser.json["items"]])


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
                u'title': u'Via task'},
              u'roles': [u'Editor'],
              u'reference': {
                  u'url': self.task.absolute_url(),
                  u'title': self.task.title},
              u'principal': u'kathi.barfuss'},
             {u'cause': {
                 u'id': ASSIGNMENT_VIA_TASK_AGENCY,
                 u'title': u'Via task agency'},
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
                u'title': u'Via task'},
              u'roles': [u'Editor'],
              u'reference': {
                  u'url': self.task.absolute_url(),
                  u'title': self.task.title},
              u'principal': u'kathi.barfuss'}],
            browser.json)

    @browsing
    def test_remove_role_assignments_and_updates_local_roles(self, browser):
        self.login(self.administrator, browser=browser)

        manager = RoleAssignmentManager(self.empty_dossier)
        manager.add_or_update_assignment(
            SharingRoleAssignment(
                self.regular_user.id, ['Reader', 'Editor', 'Contributor']))

        data = json.dumps({
            "entries": [
                {"id": self.regular_user.id,
                 "roles": {"Contributor": False,
                           "Editor": False,
                           "Reader": False,
                           "Reviewer": False,
                           "Publisher": False},
                 "type": "user"},
            ],
            "inherit": True})

        browser.open(self.empty_dossier, data, view='@sharing', method='POST',
                     headers={'Accept': 'application/json',
                              'Content-Type': 'application/json'})

        self.assertEquals(
            (('robert.ziegler', ('Owner',)),),
            self.empty_dossier.get_local_roles())
        self.assertEquals(
            [],
            RoleAssignmentManager(self.empty_dossier).storage._storage())


class TestWorkspaceSharing(IntegrationTestCase):

    @browsing
    def test_available_roles_on_a_workspace_root(self, browser):
        # Only managers can delegate roles on the workspace root
        self.login(self.manager, browser=browser)

        browser.open(self.workspace_root, view='@sharing',
                     method='GET', headers={'Accept': 'application/json'})

        self.assertEqual(
            [u'WorkspacesCreator', u'WorkspacesUser'],
            [role['id'] for role in browser.json.get('available_roles')])

    @browsing
    def test_available_roles_on_a_workspace(self, browser):
        self.login(self.administrator, browser=browser)

        browser.open(self.workspace, view='@sharing',
                     method='GET', headers={'Accept': 'application/json'})

        self.assertEqual(
            [u'WorkspaceAdmin', u'WorkspaceMember', u'WorkspaceGuest'],
            [role['id'] for role in browser.json.get('available_roles')])

    @browsing
    def test_available_roles_on_a_workspace_folder(self, browser):
        self.login(self.administrator, browser=browser)

        browser.open(self.workspace_folder, view='@sharing',
                     method='GET', headers={'Accept': 'application/json'})

        self.assertEqual(
            [u'WorkspaceAdmin', u'WorkspaceMember', u'WorkspaceGuest'],
            [role['id'] for role in browser.json.get('available_roles')])

    @browsing
    def test_only_workspace_users_are_shown_for_workspace_admin_on_workspace(self, browser):
        self.login(self.workspace_admin, browser=browser)

        query = {"search": "nicole"}
        browser.open(self.workspace,
                     view='@sharing?{}'.format(urlencode(query)),
                     method='GET',
                     headers={'Accept': 'application/json'})

        self.assertItemsEqual(
            [u'fridolin.hugentobler', u'hans.peter',
             u'beatrice.schrodinger', u'gunther.frohlich'],
            [entry['id'] for entry in browser.json.get('items')])

    @browsing
    def test_only_workspace_users_are_shown_for_workspace_owner_on_workspace(self, browser):
        self.login(self.workspace_owner, browser=browser)

        query = {"search": "nicole"}
        browser.open(self.workspace,
                     view='@sharing?{}'.format(urlencode(query)),
                     method='GET',
                     headers={'Accept': 'application/json'})

        self.assertItemsEqual(
            [u'fridolin.hugentobler', u'hans.peter',
             u'beatrice.schrodinger', u'gunther.frohlich'],
            [entry['id'] for entry in browser.json.get('items')])

    @browsing
    def test_all_users_are_shown_for_admins_on_workspace(self, browser):
        self.login(self.administrator, browser=browser)

        query = {"search": "nicole"}
        browser.open(self.workspace,
                     view='@sharing?{}'.format(urlencode(query)),
                     method='GET',
                     headers={'Accept': 'application/json'})

        self.assertItemsEqual(
            [u'nicole.kohler', u'fridolin.hugentobler', u'gunther.frohlich',
             u'hans.peter', u'beatrice.schrodinger'],
            [entry['id'] for entry in browser.json.get('items')])

    @browsing
    def test_only_workspace_users_are_shown_for_workspace_admin_on_workspace_folder(self, browser):
        self.login(self.workspace_admin, browser=browser)

        query = {"search": "nicole"}
        browser.open(self.workspace_folder,
                     view='@sharing?{}'.format(urlencode(query)),
                     method='GET',
                     headers={'Accept': 'application/json'})

        self.assertItemsEqual(
            [u'fridolin.hugentobler', u'hans.peter', u'beatrice.schrodinger',
             u'gunther.frohlich'],
            [entry['id'] for entry in browser.json.get('items')])

    @browsing
    def test_only_workspace_users_are_shown_for_workspace_owner_on_workspace_folder(self, browser):
        self.login(self.workspace_owner, browser=browser)

        query = {"search": "nicole"}
        browser.open(self.workspace_folder,
                     view='@sharing?{}'.format(urlencode(query)),
                     method='GET',
                     headers={'Accept': 'application/json'})

        self.assertItemsEqual(
            [u'fridolin.hugentobler', u'hans.peter', u'beatrice.schrodinger',
             u'gunther.frohlich'],
            [entry['id'] for entry in browser.json.get('items')])

    @browsing
    def test_all_users_are_shown_for_admins_on_workspace_folder(self, browser):
        self.login(self.administrator, browser=browser)

        query = {"search": "nicole"}
        browser.open(self.workspace_folder,
                     view='@sharing?{}'.format(urlencode(query)),
                     method='GET',
                     headers={'Accept': 'application/json'})

        self.assertItemsEqual(
            [u'nicole.kohler', u'fridolin.hugentobler',
             u'hans.peter', u'beatrice.schrodinger', u'gunther.frohlich'],
            [entry['id'] for entry in browser.json.get('items')])


class TestSharingViewPermissions(IntegrationTestCase):

    @browsing
    def test_limited_admin_cannot_access_sharing_view_on_dossier(self, browser):
        self.login(self.manager, browser=browser)
        browser.open(self.dossier, view='@@sharing')

        self.login(self.administrator, browser=browser)
        browser.open(self.dossier, view='@@sharing')

        with self.assertRaises(InsufficientPrivileges):
            self.login(self.limited_admin, browser=browser)
            browser.open(self.dossier, view='@@sharing')

    @browsing
    def test_limited_admin_cannot_access_sharing_view_on_repository_root(self, browser):
        self.login(self.manager, browser=browser)
        browser.open(self.repository_root, view='@@sharing')

        self.login(self.administrator, browser=browser)
        browser.open(self.repository_root, view='@@sharing')

        with self.assertRaises(InsufficientPrivileges):
            self.login(self.limited_admin, browser=browser)
            browser.open(self.repository_root, view='@@sharing')

    @browsing
    def test_limited_admin_cannot_access_sharing_view_on_repository_folder(self, browser):
        self.login(self.manager, browser=browser)
        browser.open(self.leaf_repofolder, view='@@sharing')

        self.login(self.administrator, browser=browser)
        browser.open(self.leaf_repofolder, view='@@sharing')

        with self.assertRaises(InsufficientPrivileges):
            self.login(self.limited_admin, browser=browser)
            browser.open(self.leaf_repofolder, view='@@sharing')
