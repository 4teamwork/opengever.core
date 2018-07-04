from ftw.builder import Builder
from ftw.builder import create
from opengever.base.role_assignments import RoleAssignmentManager
from opengever.base.role_assignments import SharingRoleAssignment
from opengever.ogds.base.sources import AllUsersInboxesAndTeamsSource
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.ogds.base.utils import get_current_org_unit
from opengever.testing import IntegrationTestCase
from opengever.workspace.utils import get_workspace_user_ids
from opengever.workspace.utils import is_within_workspace


class TestAllUsersInboxesAndTeamsSourceForWorkspace(IntegrationTestCase):

    def setUp(self):
        super(TestAllUsersInboxesAndTeamsSourceForWorkspace, self).setUp()
        self.login(self.administrator)
        self.org_unit2 = create(Builder('org_unit')
                                .id('unit2')
                                .having(title=u'Finanzdirektion',
                                        admin_unit=get_current_admin_unit())
                                .with_default_groups())

        self.john = create(Builder('ogds_user')
                           .id('john')
                           .having(firstname=u'John', lastname=u'Doe')
                           .assign_to_org_units([get_current_org_unit()]))
        self.hugo = create(Builder('ogds_user')
                           .id('hugo')
                           .having(firstname=u'Hugo', lastname=u'Boss')
                           .assign_to_org_units([get_current_org_unit()]))
        self.hans = create(Builder('ogds_user')
                           .id('hans')
                           .having(firstname=u'Hans', lastname=u'Peter')
                           .assign_to_org_units([get_current_org_unit(),
                                                 self.org_unit2]))
        self.reto = create(Builder('ogds_user')
                           .id('reto')
                           .having(firstname=u'Reto', lastname=u'Rageto')
                           .assign_to_org_units([self.org_unit2]))

    def set_permissions_on_workspace(self):
        self.workspace.manage_permission('View', roles=['Contributor', ])

        RoleAssignmentManager(self.workspace).add_assignment(
            SharingRoleAssignment(self.hugo.userid, ['Contributor']))
        RoleAssignmentManager(self.workspace).add_assignment(
            SharingRoleAssignment(self.john.userid, ['Contributor']))

    def test_is_within_workspace(self):
        self.assertFalse(is_within_workspace(self.dossier),
                         'Dossier is not within workspace')
        self.assertFalse(is_within_workspace(self.workspace_root),
                         'WorkspaceRoot is not within workspace')

        self.assertTrue(is_within_workspace(self.workspace),
                        'Workspace is within Workspace')

        doc_in_workspace = create(Builder('document').within(self.workspace))
        self.assertTrue(is_within_workspace(doc_in_workspace),
                        'Document in workspace is within workspace')

    def test_get_workspace_user_ids(self):
        self.set_permissions_on_workspace()
        self.assertEquals([self.john.userid, self.hugo.userid],
                          get_workspace_user_ids(self.workspace))

    def test_only_local_roles_with_view_permission_are_selectable(self):
        source = AllUsersInboxesAndTeamsSource(self.workspace)
        self.assertNotIn(u'fa:john', source)
        self.assertNotIn(u'fa:hugo', source)
        self.assertNotIn(u'fa:hans', source)
        self.assertNotIn(u'unit2:hans', source)
        self.assertNotIn(u'unit2:reto', source)
        self.assertNotIn(u'unit2:john', source)

    def test_local_roles_from_workspace_are_in_source(self):
        self.set_permissions_on_workspace()
        source = AllUsersInboxesAndTeamsSource(self.workspace)

        self.assertIn(u'fa:john', source)
        self.assertIn(u'fa:hugo', source)
        self.assertIn(u'unit2:john', source)
        self.assertNotIn(u'fa:hans', source)
        self.assertNotIn(u'unit2:hans', source)
        self.assertNotIn(u'unit2:reto', source)

    def test_search_for_users_within_workspace(self):
        source = AllUsersInboxesAndTeamsSource(self.workspace)
        result = source.search('John')

        self.assertFalse(
            result,
            'Expect no result, since there are no permissions set.')

        self.set_permissions_on_workspace()

        result = source.search('John')
        self.assertEqual(1, len(result), 'Expect one result. only John')

        result = source.search('Hugo')
        self.assertEqual(1, len(result), 'Expect one result. only John')
