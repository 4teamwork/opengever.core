from datetime import date
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.base.oguid import Oguid
from opengever.base.role_assignments import ASSIGNMENT_VIA_TASK
from opengever.base.role_assignments import ASSIGNMENT_VIA_TASK_AGENCY
from opengever.base.role_assignments import RoleAssignmentManager
from opengever.base.role_assignments import SharingRoleAssignment
from opengever.task.task import ITask
from opengever.testing import index_data_for
from opengever.testing import IntegrationTestCase
from plone import api
from z3c.relationfield.relation import RelationValue
from zope.component import getUtility
from zope.event import notify
from zope.intid.interfaces import IIntIds
from zope.lifecycleevent import ObjectModifiedEvent


class TestLocalRolesSetter(IntegrationTestCase):

    def test_responsible_has_local_editor_role_on_task_when_is_added(self):
        self.login(self.regular_user)

        self.assertEqual(
            ('Editor', ),
            self.task.get_local_roles_for_userid(self.regular_user.id))

    def test_new_responsible_has_local_editor_role_on_task_when_is_changed(self):
        self.login(self.regular_user)

        self.task.responsible = self.secretariat_user.id
        notify(ObjectModifiedEvent(self.task))

        self.assertEqual(
            ('Editor', ),
            self.task.get_local_roles_for_userid(self.secretariat_user.id))

    def test_relate_to_proposal_document_grants_permissions_on_proposal(self):
        self.login(self.regular_user)

        intids = getUtility(IIntIds)
        relation = RelationValue(intids.getId(self.proposaldocument))
        ITask(self.task).relatedItems.append(relation)

        notify(ObjectModifiedEvent(self.task))

        self.assertEqual(
            ('Editor', 'Reader'),
            self.proposaldocument.get_local_roles_for_userid(
                self.regular_user.id))
        self.assertEqual(
            ('Editor', 'Reader'),
            self.proposal.get_local_roles_for_userid(
                self.regular_user.id),
            "The proposal should have the same local roles as its document.")

    def test_responsible_has_reader_and_editor_role_on_related_items_of_direct_execution_task(self):
        self.login(self.regular_user)

        # inactive_task is unidirectional by value
        manager = RoleAssignmentManager(self.inactive_document)
        assignment = manager.storage.get_by_reference(
            Oguid.for_object(self.inactive_task).id)[0]

        self.assertEqual(['Reader', 'Editor'], assignment.get('roles'))

    def test_responsible_has_reader_role_on_related_items_of_information_task(self):
        self.login(self.regular_user)

        # info_task is unidirectional by value
        manager = RoleAssignmentManager(self.document)
        assignment = manager.storage.get_by_reference(Oguid.for_object(self.info_task).id)[0]
        self.assertEqual(['Reader'], assignment.get('roles'))

    def test_reassigning_task_grants_local_roles_to_new_responsible(self):
        self.login(self.regular_user)

        roles = self.inactive_document.get_local_roles_for_userid(
            self.secretariat_user.id)
        self.assertEqual(tuple(), roles)

        self.inactive_task.responsible = self.secretariat_user.id
        notify(ObjectModifiedEvent(self.inactive_task))

        roles = self.inactive_document.get_local_roles_for_userid(
            self.secretariat_user.id)
        self.assertEqual(('Editor', 'Reader'), roles)

    def test_responsible_of_a_bidirectional_by_ref_task_has_reader_and_editor_role_on_related_items(self):
        self.login(self.regular_user)

        # task is bidirectional by value
        self.assertEqual(
            ('Editor', 'Reader', ),
            self.document.get_local_roles_for_userid(self.regular_user.id))

    def test_responsible_has_contributor_role_on_distinct_parent_when_task_is_added(self):
        self.login(self.regular_user)
        self.assertEqual(
            ('Contributor', ),
            self.dossier.get_local_roles_for_userid(self.regular_user.id))

    def test_responsible_has_contributor_role_on_distinct_parent_when_task_is_updated(self):
        self.login(self.regular_user)

        self.inactive_task.responsible = self.secretariat_user.id
        notify(ObjectModifiedEvent(self.inactive_task))

        self.assertEqual(
            ('Contributor', ),
            self.inactive_dossier.get_local_roles_for_userid(self.secretariat_user.id))

    def test_inbox_group_of_the_responsible_client_has_the_same_localroles_as_the_responsible_in_a_multiclient_setup(self):
        self.login(self.regular_user)
        self.assertEqual(
            ('Editor', ),
            self.task.get_local_roles_for_userid('fa_inbox_users'))
        self.assertEqual(
            ('Editor', 'Reader', ),
            self.document.get_local_roles_for_userid('fa_inbox_users'))
        self.assertEqual(
            ('Contributor', ),
            self.dossier.get_local_roles_for_userid('fa_inbox_users'))

    def test_inbox_group_has_no_additional_localroles_on_private_tasks(self):
        self.login(self.regular_user)
        self.assertEqual(
            (),
            self.private_task.get_local_roles_for_userid('fa_inbox_users'))

    def test_inbox_group_has_no_additional_localroles_in_a_oneclient_setup(self):
        self.login(self.regular_user)
        self.disable_additional_org_units()

        dossier = create(Builder('dossier'))
        document = create(Builder('document'))
        task = create(Builder('task')
                      .within(dossier)
                      .relate_to(document)
                      .having(responsible=self.regular_user.getId()))

        self.assertEqual(
            (),
            task.get_local_roles_for_userid('fa_inbox_users'))
        self.assertEqual(
            (),
            document.get_local_roles_for_userid('fa_inbox_users'))
        self.assertEqual(
            (),
            dossier.get_local_roles_for_userid('fa_inbox_users'))

    def test_use_inbox_group_when_inbox_is_responsible(self):
        self.login(self.regular_user)

        self.assertEqual(
            ('Editor', ),
            self.inbox_task.get_local_roles_for_userid('fa_inbox_users'))

        self.assertEqual(
            ('Contributor', ),
            self.dossier.get_local_roles_for_userid('fa_inbox_users'))

        self.assertEqual(
            (), self.inbox_task.get_local_roles_for_userid('inbox:fa'))

    @browsing
    def test_responsible_can_edit_related_documents_that_are_inside_a_task(self, browser):
        self.login(self.administrator, browser=browser)
        api.content.disable_roles_acquisition(obj=self.dossier)

        RoleAssignmentManager(self.dossier).add_or_update_assignment(
            SharingRoleAssignment(self.administrator.getId(),
                                  ['Reader', 'Contributor', 'Editor']))

        self.task.responsible = self.secretariat_user.id
        notify(ObjectModifiedEvent(self.task))

        self.login(self.secretariat_user, browser=browser)
        browser.open(self.taskdocument, view='edit')


class TestLocalRolesRevoking(IntegrationTestCase):

    @browsing
    def test_closing_a_task_revokes_responsible_roles_on_task(self, browser):
        self.login(self.dossier_responsible, browser=browser)
        self.set_workflow_state('task-state-tested-and-closed', self.subtask)
        self.set_workflow_state('task-state-resolved', self.task)

        storage = RoleAssignmentManager(self.task).storage
        self.assertEqual(
            [{'cause': ASSIGNMENT_VIA_TASK,
              'roles': ['Editor'],
              'reference': Oguid.for_object(self.task),
              'principal': 'kathi.barfuss'},
             {'cause': ASSIGNMENT_VIA_TASK_AGENCY,
              'roles': ['Editor'],
              'reference': Oguid.for_object(self.task),
              'principal': 'fa_inbox_users'}], storage._storage())

        # close
        browser.open(self.task, view='tabbedview_view-overview')
        browser.click_on('task-transition-resolved-tested-and-closed')
        browser.fill({'Response': 'Done!'})
        browser.click_on('Save')

        self.assertEqual([], storage._storage())

    @browsing
    def test_closing_does_not_revoke_roles_on_task_if_revoke_permission_is_false(self, browser):
        self.login(self.dossier_responsible, browser=browser)
        self.set_workflow_state('task-state-tested-and-closed', self.subtask)
        self.set_workflow_state('task-state-resolved', self.task)
        self.task.revoke_permissions = False

        storage = RoleAssignmentManager(self.task).storage
        self.assertEqual(
            [{'cause': ASSIGNMENT_VIA_TASK,
              'roles': ['Editor'],
              'reference': Oguid.for_object(self.task),
              'principal': 'kathi.barfuss'},
             {'cause': ASSIGNMENT_VIA_TASK_AGENCY,
              'roles': ['Editor'],
              'reference': Oguid.for_object(self.task),
              'principal': 'fa_inbox_users'}], storage._storage())

        # close
        browser.open(self.task, view='tabbedview_view-overview')
        browser.click_on('task-transition-resolved-tested-and-closed')
        browser.fill({'Response': 'Done!'})
        browser.click_on('Save')

        self.assertEqual(
            [{'cause': ASSIGNMENT_VIA_TASK,
              'roles': ['Editor'],
              'reference': Oguid.for_object(self.task),
              'principal': 'kathi.barfuss'},
             {'cause': ASSIGNMENT_VIA_TASK_AGENCY,
              'roles': ['Editor'],
              'reference': Oguid.for_object(self.task),
              'principal': 'fa_inbox_users'}], storage._storage())

    @browsing
    def test_reassigning_task_revokes_responsible_roles_on_task(self, browser):
        self.login(self.regular_user, browser)

        roles = self.task.get_local_roles_for_userid(
            self.regular_user.id)
        self.assertEqual(('Editor',), roles)

        roles = self.task.get_local_roles_for_userid(
            self.secretariat_user.id)
        self.assertEqual(tuple(), roles)

        # assign
        browser.open(self.task, view='tabbedview_view-overview')
        browser.click_on('task-transition-reassign')
        form = browser.find_form_by_field('Responsible')
        form.find_widget('Responsible').fill(self.secretariat_user)
        browser.fill({'Response': 'For you'})
        browser.click_on('Assign')

        # old responsible's permissions were revoked
        roles = self.task.get_local_roles_for_userid(
            self.regular_user.id)
        self.assertEqual(tuple(), roles)

        # new responsible was granted permissions
        roles = self.task.get_local_roles_for_userid(
            self.secretariat_user.id)
        self.assertEqual(('Editor', ), roles)

    @browsing
    def test_reassigning_task_does_not_revoke_roles_if_revoke_permission_is_false(self, browser):
        self.login(self.regular_user, browser)
        self.task.revoke_permissions = False

        roles = self.task.get_local_roles_for_userid(
            self.regular_user.id)
        self.assertEqual(('Editor',), roles)

        roles = self.task.get_local_roles_for_userid(
            self.secretariat_user.id)
        self.assertEqual(tuple(), roles)

        # assign
        browser.open(self.task, view='tabbedview_view-overview')
        browser.click_on('task-transition-reassign')
        form = browser.find_form_by_field('Responsible')
        form.find_widget('Responsible').fill(self.secretariat_user)
        browser.fill({'Response': 'For you'})
        browser.click_on('Assign')

        # old responsible's permissions were not revoked
        roles = self.task.get_local_roles_for_userid(
            self.regular_user.id)
        self.assertEqual(('Editor',), roles)

        # new responsible was granted permissions
        roles = self.task.get_local_roles_for_userid(
            self.secretariat_user.id)
        self.assertEqual(('Editor', ), roles)

    @browsing
    def test_reject_task_revokes_responsible_roles_on_task(self, browser):
        self.login(self.regular_user, browser)

        self.set_workflow_state('task-state-open', self.subtask)

        roles = self.subtask.get_local_roles_for_userid(self.regular_user.id)
        self.assertEqual(('Editor',), roles)

        roles = self.subtask.get_local_roles_for_userid(self.dossier_responsible.id)
        self.assertEqual(('Owner', ), roles)

        # reject
        browser.open(self.subtask, view='tabbedview_view-overview')
        browser.click_on('task-transition-open-rejected')
        browser.fill({'Response': 'Nope!'})
        browser.click_on('Save')

        # old responsible's permissions were revoked
        roles = self.subtask.get_local_roles_for_userid(self.regular_user.id)
        self.assertEqual(tuple(), roles)

        # The new responsible, which is the issuer was granted permissions
        roles = self.subtask.get_local_roles_for_userid(self.dossier_responsible.id)
        self.assertEqual(('Editor', 'Owner', ), roles)

    @browsing
    def test_reader_of_parent_can_still_view_closed_task(self, browser):
        with self.login(self.regular_user):
            RoleAssignmentManager(self.portal).add_or_update_assignment(
                SharingRoleAssignment(self.reader_user.getId(), ['Reader']),
            )
            RoleAssignmentManager(self.dossier).add_or_update_assignment(
                SharingRoleAssignment(self.reader_user.getId(), ['Reader']),
            )

        self.login(self.reader_user, browser)
        browser.open(self.task, view='tabbedview_view-overview')
        expected_actions = []
        self.assertEqual(expected_actions, browser.css('#action-menu a').text)

        with self.login(self.dossier_responsible, browser=browser):
            self.set_workflow_state('task-state-tested-and-closed', self.subtask)
            self.set_workflow_state('task-state-resolved', self.task)

        browser.open(self.task, view='tabbedview_view-overview')
        expected_actions = []
        self.assertEqual(expected_actions, browser.css('#action-menu a').text)

    @browsing
    def test_closing_a_task_revokes_responsible_roles_on_related_documents(self, browser):
        self.login(self.dossier_responsible, browser=browser)
        self.set_workflow_state('task-state-tested-and-closed', self.subtask)
        self.set_workflow_state('task-state-resolved', self.task)
        storage = RoleAssignmentManager(self.document).storage
        expected_oguids = [
            Oguid.for_object(task).id
            for task in (
                self.task, self.task, self.subtask, self.subtask,
                self.info_task, self.info_task, self.private_task,
                self.inbox_task)
        ]
        self.assertEqual(
            expected_oguids,
            [item.get('reference') for item in storage._storage()],
        )
        # close
        browser.open(self.task, view='tabbedview_view-overview')
        browser.click_on('task-transition-resolved-tested-and-closed')
        browser.fill({'Response': 'Done!'})
        browser.click_on('Save')
        expected_oguids = [
            Oguid.for_object(task).id
            for task in (self.subtask, self.subtask, self.info_task,
                         self.info_task, self.private_task, self.inbox_task)
        ]
        self.assertEqual(
            expected_oguids,
            [item.get('reference') for item in storage._storage()],
        )

    @browsing
    def test_closing_does_not_revoke_roles_on_related_documents_if_revoke_permission_is_false(self, browser):
        self.login(self.dossier_responsible, browser=browser)
        self.set_workflow_state('task-state-tested-and-closed', self.subtask)
        self.set_workflow_state('task-state-resolved', self.task)
        self.task.revoke_permissions = False

        storage = RoleAssignmentManager(self.document).storage
        expected_oguids = [Oguid.for_object(task).id for task in (self.task,
                           self.task, self.subtask, self.subtask,
                           self.info_task, self.info_task, self.private_task,
                           self.inbox_task)]
        self.assertEqual(expected_oguids, [item.get('reference') for item in storage._storage()])

        # close
        browser.open(self.task, view='tabbedview_view-overview')
        browser.click_on('task-transition-resolved-tested-and-closed')
        browser.fill({'Response': 'Done!'})
        browser.click_on('Save')

        self.assertEqual(expected_oguids, [item.get('reference') for item in storage._storage()])

    @browsing
    def test_closing_a_task_revokes_roles_on_proposal(self, browser):
        self.login(self.dossier_responsible, browser=browser)

        intids = getUtility(IIntIds)
        relation = RelationValue(intids.getId(self.proposaldocument))
        ITask(self.task).relatedItems.append(relation)
        notify(ObjectModifiedEvent(self.task))

        expected_assignments = [{'cause': ASSIGNMENT_VIA_TASK,
                                 'roles': ['Reader', 'Editor'],
                                 'reference': Oguid.for_object(self.task),
                                 'principal': self.regular_user.id},
                                {'cause': ASSIGNMENT_VIA_TASK_AGENCY,
                                 'roles': ['Reader', 'Editor'],
                                 'reference': Oguid.for_object(self.task),
                                 'principal': u'fa_inbox_users'}]

        document_storage = RoleAssignmentManager(self.proposaldocument).storage
        self.assertEqual(expected_assignments, document_storage._storage())

        proposal_storage = RoleAssignmentManager(self.proposal).storage
        self.assertEqual(expected_assignments, proposal_storage._storage())

        self.set_workflow_state('task-state-tested-and-closed', self.subtask)
        self.set_workflow_state('task-state-resolved', self.task)
        notify(ObjectModifiedEvent(self.task))

        browser.open(self.task, view='tabbedview_view-overview')
        browser.click_on('task-transition-resolved-tested-and-closed')
        browser.click_on('Save')

        self.assertEqual([], proposal_storage._storage())
        self.assertEqual([], document_storage._storage())

    @browsing
    def test_closing_does_not_revoke_roles_on_proposal_if_revoke_permission_is_false(self, browser):
        self.login(self.dossier_responsible, browser=browser)
        self.task.revoke_permissions = False

        intids = getUtility(IIntIds)
        relation = RelationValue(intids.getId(self.proposaldocument))
        ITask(self.task).relatedItems.append(relation)
        notify(ObjectModifiedEvent(self.task))

        expected_assignments = [{'cause': ASSIGNMENT_VIA_TASK,
                                 'roles': ['Reader', 'Editor'],
                                 'reference': Oguid.for_object(self.task),
                                 'principal': self.regular_user.id},
                                {'cause': ASSIGNMENT_VIA_TASK_AGENCY,
                                 'roles': ['Reader', 'Editor'],
                                 'reference': Oguid.for_object(self.task),
                                 'principal': u'fa_inbox_users'}]

        document_storage = RoleAssignmentManager(self.proposaldocument).storage
        self.assertEqual(expected_assignments, document_storage._storage())

        proposal_storage = RoleAssignmentManager(self.proposal).storage
        self.assertEqual(expected_assignments, proposal_storage._storage())

        self.set_workflow_state('task-state-tested-and-closed', self.subtask)
        self.set_workflow_state('task-state-resolved', self.task)
        notify(ObjectModifiedEvent(self.task))

        browser.open(self.task, view='tabbedview_view-overview')
        browser.click_on('task-transition-resolved-tested-and-closed')
        browser.click_on('Save')

        self.assertEqual(expected_assignments, proposal_storage._storage())
        self.assertEqual(expected_assignments, document_storage._storage())

    @browsing
    def test_closing_a_task_revokes_responsible_roles_on_distinct_parent(self, browser):
        self.login(self.dossier_responsible, browser=browser)
        self.set_workflow_state('task-state-resolved', self.meeting_task)

        storage = RoleAssignmentManager(self.meeting_dossier).storage
        self.assertEqual(
            [{'cause': ASSIGNMENT_VIA_TASK,
              'roles': ['Contributor'],
              'reference': Oguid.for_object(self.meeting_task),
              'principal': self.dossier_responsible.id},
             {'cause': ASSIGNMENT_VIA_TASK_AGENCY,
              'roles': ['Contributor'],
              'reference': Oguid.for_object(self.meeting_task),
              'principal': 'fa_inbox_users'},
             {'cause': ASSIGNMENT_VIA_TASK,
              'roles': ['Contributor'],
              'reference': Oguid.for_object(self.meeting_subtask),
              'principal': self.dossier_responsible.id},
             {'cause': ASSIGNMENT_VIA_TASK_AGENCY,
              'roles': ['Contributor'],
              'reference': Oguid.for_object(self.meeting_subtask),
              'principal': 'fa_inbox_users'}],
            storage._storage())

        # close subtask
        browser.open(self.meeting_subtask, view='tabbedview_view-overview')
        browser.click_on('task-transition-resolved-tested-and-closed')
        browser.click_on('Save')

        browser.open(self.meeting_task, view='tabbedview_view-overview')
        browser.click_on('task-transition-resolved-tested-and-closed')
        browser.click_on('Save')

        self.assertEqual([], storage._storage())
        self.assertEqual(
            (('franzi.muller', ('Owner',)),),
            self.meeting_dossier.get_local_roles())

    @browsing
    def test_closing_does_not_revoke_roles_on_distinct_parent_if_revoke_permission_is_false(self, browser):
        self.login(self.dossier_responsible, browser=browser)
        self.set_workflow_state('task-state-resolved', self.meeting_task)
        self.meeting_task.revoke_permissions = False

        self.assertEqual(
            (('fa_inbox_users', ('Contributor',)),
             ('franzi.muller', ('Owner',)),
             ('robert.ziegler', ('Contributor',))),
            self.meeting_dossier.get_local_roles())

        storage = RoleAssignmentManager(self.meeting_dossier).storage
        self.assertEqual(
            [{'cause': ASSIGNMENT_VIA_TASK,
              'roles': ['Contributor'],
              'reference': Oguid.for_object(self.meeting_task),
              'principal': self.dossier_responsible.id},
             {'cause': ASSIGNMENT_VIA_TASK_AGENCY,
              'roles': ['Contributor'],
              'reference': Oguid.for_object(self.meeting_task),
              'principal': 'fa_inbox_users'},
             {'cause': ASSIGNMENT_VIA_TASK,
              'roles': ['Contributor'],
              'reference': Oguid.for_object(self.meeting_subtask),
              'principal': self.dossier_responsible.id},
             {'cause': ASSIGNMENT_VIA_TASK_AGENCY,
              'roles': ['Contributor'],
              'reference': Oguid.for_object(self.meeting_subtask),
              'principal': 'fa_inbox_users'}],
            storage._storage())

        # close subtask
        browser.open(self.meeting_subtask, view='tabbedview_view-overview')
        browser.click_on('task-transition-resolved-tested-and-closed')
        browser.click_on('Save')

        browser.open(self.meeting_task, view='tabbedview_view-overview')
        browser.click_on('task-transition-resolved-tested-and-closed')
        browser.click_on('Save')

        self.assertEqual(
            [{'cause': ASSIGNMENT_VIA_TASK,
              'roles': ['Contributor'],
              'reference': Oguid.for_object(self.meeting_task),
              'principal': self.dossier_responsible.id},
             {'cause': ASSIGNMENT_VIA_TASK_AGENCY,
              'roles': ['Contributor'],
              'reference': Oguid.for_object(self.meeting_task),
              'principal': 'fa_inbox_users'}],
            storage._storage())
        self.assertEqual(
            (('fa_inbox_users', ('Contributor',)),
             ('franzi.muller', ('Owner',)),
             ('robert.ziegler', ('Contributor',))),
            self.meeting_dossier.get_local_roles())

    @browsing
    def test_cancelling_a_task_revokes_roles(self, browser):
        self.login(self.dossier_responsible, browser=browser)
        self.set_workflow_state('task-state-open', self.subtask)

        # cancel
        browser.open(self.subtask, view='tabbedview_view-overview')
        browser.click_on('task-transition-open-cancelled')
        browser.click_on('Save')

        storage = RoleAssignmentManager(self.subtask).storage
        self.assertEqual([], storage._storage())

    @browsing
    def test_cancelling_a_task_does_not_revoke_roles_if_revoke_permission_is_false(self, browser):
        self.login(self.dossier_responsible, browser=browser)
        self.set_workflow_state('task-state-open', self.subtask)
        self.subtask.revoke_permissions = False

        # cancel
        browser.open(self.subtask, view='tabbedview_view-overview')
        browser.click_on('task-transition-open-cancelled')
        browser.click_on('Save')

        storage = RoleAssignmentManager(self.subtask).storage

        self.assertEqual(
            [{'cause': ASSIGNMENT_VIA_TASK,
              'roles': ['Editor'],
              'reference': Oguid.for_object(self.subtask),
              'principal': self.regular_user.id},
             {'cause': ASSIGNMENT_VIA_TASK_AGENCY,
              'roles': ['Editor'],
              'reference': Oguid.for_object(self.subtask),
              'principal': 'fa_inbox_users'}],
            storage._storage())

    @browsing
    def test_closing_a_direct_execution_task_revokes_roles(self, browser):
        self.login(self.regular_user, browser=browser)
        self.subtask.task_type = 'direct-execution'
        self.subtask.sync()
        self.set_workflow_state('task-state-in-progress', self.subtask)

        # close
        browser.open(self.subtask, view='tabbedview_view-overview')
        browser.click_on('task-transition-in-progress-tested-and-closed')
        browser.click_on('Save')

        storage = RoleAssignmentManager(self.subtask).storage
        self.assertEqual([], storage._storage())

    @browsing
    def test_closing_direct_execution_task_does_not_revoke_roles_if_revoke_permission_is_false(self, browser):
        self.login(self.regular_user, browser=browser)
        self.subtask.revoke_permissions = False
        self.subtask.task_type = 'direct-execution'
        self.subtask.sync()
        self.set_workflow_state('task-state-in-progress', self.subtask)

        # close
        browser.open(self.subtask, view='tabbedview_view-overview')
        browser.click_on('task-transition-in-progress-tested-and-closed')
        browser.click_on('Save')

        storage = RoleAssignmentManager(self.subtask).storage
        self.assertEqual(
            [{'cause': ASSIGNMENT_VIA_TASK,
              'roles': ['Editor'],
              'reference': Oguid.for_object(self.subtask),
              'principal': self.regular_user.id},
             {'cause': ASSIGNMENT_VIA_TASK_AGENCY,
              'roles': ['Editor'],
              'reference': Oguid.for_object(self.subtask),
              'principal': 'fa_inbox_users'}],
            storage._storage())

    @browsing
    def test_skip_a_task_revokes_roles(self, browser):
        self.login(self.secretariat_user, browser=browser)

        storage = RoleAssignmentManager(self.seq_subtask_2).storage
        self.assertEqual(
            [{'cause': ASSIGNMENT_VIA_TASK,
              'roles': ['Editor'],
              'reference': Oguid.for_object(self.seq_subtask_2),
              'principal': 'kathi.barfuss'},
             {'cause': ASSIGNMENT_VIA_TASK_AGENCY,
              'roles': ['Editor'],
              'reference': Oguid.for_object(self.seq_subtask_2),
              'principal': 'fa_inbox_users'}], storage._storage())

        # skip
        browser.open(self.seq_subtask_2, view='tabbedview_view-overview')
        browser.click_on('task-transition-planned-skipped')
        browser.click_on('Save')

        self.assertEqual([], storage._storage())

    @browsing
    def test_skip_task_does_not_revoke_roles_if_revoke_permission_is_false(self, browser):
        self.login(self.secretariat_user, browser=browser)
        self.seq_subtask_2.revoke_permissions = False

        storage = RoleAssignmentManager(self.seq_subtask_2).storage
        self.assertEqual(
            [{'cause': ASSIGNMENT_VIA_TASK,
              'roles': ['Editor'],
              'reference': Oguid.for_object(self.seq_subtask_2),
              'principal': 'kathi.barfuss'},
             {'cause': ASSIGNMENT_VIA_TASK_AGENCY,
              'roles': ['Editor'],
              'reference': Oguid.for_object(self.seq_subtask_2),
              'principal': 'fa_inbox_users'}], storage._storage())

        # skip
        browser.open(self.seq_subtask_2, view='tabbedview_view-overview')
        browser.click_on('task-transition-planned-skipped')
        browser.click_on('Save')

        self.assertEqual(
            [{'cause': ASSIGNMENT_VIA_TASK,
              'roles': ['Editor'],
              'reference': Oguid.for_object(self.seq_subtask_2),
              'principal': 'kathi.barfuss'},
             {'cause': ASSIGNMENT_VIA_TASK_AGENCY,
              'roles': ['Editor'],
              'reference': Oguid.for_object(self.seq_subtask_2),
              'principal': 'fa_inbox_users'}], storage._storage())

    def test_can_delete_related_document_from_task(self):
        """The localroles update event used to explode when a related item was
        deleted.
        """
        self.login(self.manager)
        api.content.delete(self.document)
        self.assertEqual([], self.task.relatedItems)


class TestLocalRolesReindexing(IntegrationTestCase):

    def test_reindexes_distinct_parent_and_related_documents(self):
        self.login(self.dossier_responsible)

        principal = 'user:{}'.format(self.secretariat_user.id)

        self.assertNotIn(principal,
                         index_data_for(self.dossier)['allowedRolesAndUsers'])
        self.assertNotIn(principal,
                         index_data_for(self.document)['allowedRolesAndUsers'])

        task = create(Builder('task')
                      .within(self.dossier)
                      .titled(u'Aufgabe 1')
                      .having(responsible_client='fa',
                              responsible=self.secretariat_user.id,
                              issuer=self.dossier_responsible.getId(),
                              task_type='correction',
                              deadline=date(2016, 11, 1))
                      .in_state('task-state-in-progress')
                      .relate_to(self.document))

        self.assertIn(principal,
                      index_data_for(self.dossier)['allowedRolesAndUsers'])
        self.assertIn(principal,
                      index_data_for(self.document)['allowedRolesAndUsers'])
        self.assertIn(principal,
                      index_data_for(task)['allowedRolesAndUsers'])

    def test_also_reindexes_containing_subdossier(self):
        """The dossier are reindex manually
        """
        self.login(self.dossier_responsible)

        principal = 'user:{}'.format(self.secretariat_user.id)

        self.assertNotIn(principal,
                         index_data_for(self.dossier)['allowedRolesAndUsers'])
        self.assertNotIn(principal,
                         index_data_for(self.subdossier)['allowedRolesAndUsers'])
        self.assertNotIn(principal,
                         index_data_for(self.subsubdossier)['allowedRolesAndUsers'])

        create(Builder('task')
               .within(self.dossier)
               .titled(u'Aufgabe 1')
               .having(responsible_client='fa',
                       responsible=self.secretariat_user.id,
                       issuer=self.dossier_responsible.getId(),
                       task_type='correction',
                       deadline=date(2016, 11, 1))
               .in_state('task-state-in-progress')
               .relate_to(self.document))

        self.assertIn(principal,
                      index_data_for(self.dossier)['allowedRolesAndUsers'])
        self.assertIn(principal,
                      index_data_for(self.subdossier)['allowedRolesAndUsers'])
        self.assertIn(principal,
                      index_data_for(self.subsubdossier)['allowedRolesAndUsers'])

    @browsing
    def test_revokes_reindex_task_as_expected(self, browser):
        self.login(self.dossier_responsible, browser=browser)

        task = create(Builder('task')
                      .within(self.dossier)
                      .titled(u'Aufgabe 1')
                      .having(responsible_client='fa',
                              responsible=self.secretariat_user.id,
                              issuer=self.dossier_responsible.id,
                              task_type='correction',
                              deadline=date(2016, 11, 1))
                      .in_state('task-state-in-progress')
                      .relate_to(self.document))

        browser.open(task, view='tabbedview_view-overview')
        browser.click_on('task-transition-reassign')

        # Reassign
        form = browser.find_form_by_field('Responsible')
        form.find_widget('Responsible').fill(self.dossier_responsible)
        browser.click_on('Assign')

        old_principal = 'user:{}'.format(self.secretariat_user.id)
        new_principal = 'user:{}'.format(self.dossier_responsible.id)

        self.assertIn(new_principal,
                      index_data_for(self.dossier)['allowedRolesAndUsers'])
        self.assertNotIn(old_principal,
                         index_data_for(self.dossier)['allowedRolesAndUsers'])

        self.assertIn(new_principal,
                      index_data_for(self.subdossier)['allowedRolesAndUsers'])
        self.assertNotIn(old_principal,
                         index_data_for(self.subdossier)['allowedRolesAndUsers'])

        self.assertIn(new_principal,
                      index_data_for(self.subsubdossier)['allowedRolesAndUsers'])
        self.assertNotIn(old_principal,
                         index_data_for(self.subsubdossier)['allowedRolesAndUsers'])


class TestDossierReindexShortcut(IntegrationTestCase):

    # Types which are reindexed manually by the local roles setter.
    types_to_ignore = ['opengever.dossier.businesscasedossier',
                       'opengever.meeting.proposal']

    def test_reindexObjectSecurity_shortcut_is_safe(self):
        """Test the fact that none of a dossiers allowed content types assign
        permissions to the `Contributor` role.
        """
        self.login(self.administrator)

        types_tool = api.portal.get_tool('portal_types')
        dossier_type = types_tool['opengever.dossier.businesscasedossier']
        allowed_types = dossier_type.allowed_content_types
        wftool = api.portal.get_tool('portal_workflow')

        for content_type in allowed_types:
            if content_type in self.types_to_ignore:
                continue

            wf_id, = wftool.getChainFor(content_type)
            wf = wftool.getWorkflowById(wf_id)
            for state_id in wf.states:
                permission_info = wf.states[state_id].getPermissionInfo('View')
                self.assertNotIn(
                    'Contributor', permission_info['roles'],
                    u'`{}` allows Contributor to View on `{}` state.'.format(wf_id, state_id))
                self.assertEqual(
                    0, permission_info['acquired'],
                    u'{} has acquired View permission on `{}` state.'.format(wf_id, state_id))
