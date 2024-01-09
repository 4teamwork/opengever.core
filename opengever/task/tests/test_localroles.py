from datetime import date
from ftw.builder import Builder
from ftw.builder import create
from ftw.contentmenu.menu import FactoriesMenu
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
import json


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

    def test_responsible_has_task_responsible_role_on_distinct_parent_when_task_is_added(self):
        self.login(self.regular_user)
        self.assertEqual(
            ('TaskResponsible', ),
            self.dossier.get_local_roles_for_userid(self.regular_user.id))

    def test_responsible_has_task_responsible_role_on_distinct_parent_when_task_is_updated(self):
        self.login(self.regular_user)

        self.inactive_task.responsible = self.secretariat_user.id
        notify(ObjectModifiedEvent(self.inactive_task))

        self.assertEqual(
            ('TaskResponsible', ),
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
            ('TaskResponsible', ),
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
            ('TaskResponsible', ),
            self.dossier.get_local_roles_for_userid('fa_inbox_users'))

        self.assertEqual(
            (), self.inbox_task.get_local_roles_for_userid('inbox:fa'))

    @browsing
    def test_responsible_can_edit_related_documents_that_are_inside_a_task(self, browser):
        self.login(self.administrator, browser=browser)
        api.content.disable_roles_acquisition(obj=self.dossier)

        RoleAssignmentManager(self.dossier).add_or_update_assignment(
            SharingRoleAssignment(self.administrator.getId(),
                                  ['Reader', 'TaskResponsible', 'Editor']))

        self.task.responsible = self.secretariat_user.id
        notify(ObjectModifiedEvent(self.task))

        self.login(self.secretariat_user, browser=browser)
        browser.open(self.taskdocument, view='edit')

    @browsing
    def test_permissions_granted_to_task_responsible(self, browser):
        self.login(self.administrator, browser=browser)
        self.empty_dossier.__ac_local_roles_block__ = True
        document1 = create(Builder('document').within(self.empty_dossier))
        document2 = create(Builder('document').within(self.empty_dossier))

        task = create(Builder('task')
                      .within(self.empty_dossier)
                      .relate_to(document1)
                      .having(responsible=self.regular_user.getId(),
                              responsible_client='fa',
                              issuer=self.dossier_responsible.getId(),
                              task_type='correction',
                              deadline=date(2016, 11, 1)))

        self.login(self.regular_user, browser=browser)
        menu = FactoriesMenu(self.portal)
        # TaskResponsible role does not allow to add any objects in the dossier
        items = [el['id'] for el in menu.getMenuItems(self.empty_dossier, self.portal.REQUEST)]
        self.assertEqual([], items)

        # Editor role allows to add documents in the task
        items = [el['id'] for el in menu.getMenuItems(task, self.portal.REQUEST)]
        self.assertEqual(['opengever.document.document'], items)

        # Responsible gets view on document1 but not on document2
        self.assertTrue(api.user.has_permission("View", obj=document1))
        self.assertFalse(api.user.has_permission("View", obj=document2))

    @browsing
    def test_removing_related_documents_revokes_roles_on_removed_documents(self, browser):
        self.login(self.dossier_responsible, browser=browser)

        intids = getUtility(IIntIds)
        relation = RelationValue(intids.getId(self.proposaldocument))
        ITask(self.task).relatedItems.append(relation)
        notify(ObjectModifiedEvent(self.task))

        self.assertEqual(
            [self.document, self.proposaldocument],
            [item.to_object for item in ITask(self.task).relatedItems])

        storage = RoleAssignmentManager(self.document).storage
        assignments = filter(lambda assignment: assignment[
                             'reference'] == Oguid.for_object(self.task).id, storage._storage())
        self.assertEqual(
            [self.regular_user.id, u'fa_inbox_users'],
            [assignment['principal'] for assignment in assignments])

        storage = RoleAssignmentManager(self.proposaldocument).storage
        assignments = filter(lambda assignment: assignment[
                             'reference'] == Oguid.for_object(self.task).id, storage._storage())
        self.assertEqual(
            [self.regular_user.id, u'fa_inbox_users'],
            [assignment['principal'] for assignment in assignments])

        ITask(self.task).relatedItems = []
        notify(ObjectModifiedEvent(self.task))

        storage = RoleAssignmentManager(self.document).storage
        assignments = filter(lambda assignment: assignment[
                             'reference'] == Oguid.for_object(self.task).id, storage._storage())
        self.assertEqual(
            [], [assignment['principal'] for assignment in assignments])

        storage = RoleAssignmentManager(self.proposaldocument).storage
        assignments = filter(lambda assignment: assignment[
                             'reference'] == Oguid.for_object(self.task).id, storage._storage())
        self.assertEqual(
            [], [assignment['principal'] for assignment in assignments])

    def test_setting_local_roles_on_inactive_subdossier(self):
        self.login(self.regular_user)
        api.content.transition(obj=self.subdossier, transition='dossier-transition-deactivate')
        self.dossier.__ac_local_roles_block__ = True
        self.dossier.reindexObjectSecurity()
        notify(ObjectModifiedEvent(self.task))


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
              'principal': self.regular_user.id},
             {'cause': ASSIGNMENT_VIA_TASK_AGENCY,
              'roles': ['Editor'],
              'reference': Oguid.for_object(self.task),
              'principal': 'fa_inbox_users'}], storage._storage())

        # close
        browser.open(self.task, view='tabbedview_view-overview')
        browser.click_on('Close')
        browser.fill({'Response': 'Done!'})
        browser.click_on('Save')

        self.assertEqual([], storage._storage())

    @browsing
    def test_closing_a_task_revokes_former_responsible_roles_on_task(self, browser):
        self.login(self.dossier_responsible, browser=browser)
        self.set_workflow_state('task-state-tested-and-closed', self.subtask)

        # reassign
        browser.open(self.task, view='tabbedview_view-overview')
        browser.click_on('Reassign')
        form = browser.find_form_by_field('Responsible')
        form.find_widget('Responsible').fill(self.secretariat_user)
        browser.fill({'Response': 'For you'})
        browser.click_on('Assign')

        # reassign
        browser.open(self.task, view='tabbedview_view-overview')
        browser.click_on('Reassign')
        form = browser.find_form_by_field('Responsible')
        form.find_widget('Responsible').fill(self.administrator)
        browser.fill({'Response': 'For you'})
        browser.click_on('Assign')

        self.set_workflow_state('task-state-resolved', self.task)

        storage = RoleAssignmentManager(self.task).storage

        self.assertEqual(
            [{'cause': ASSIGNMENT_VIA_TASK,
              'roles': ['Editor'],
              'reference': Oguid.for_object(self.task),
              'principal': self.regular_user.id},
             {'cause': ASSIGNMENT_VIA_TASK_AGENCY,
              'roles': ['Editor'],
              'reference': Oguid.for_object(self.task),
              'principal': u'fa_inbox_users'},
             {'cause': ASSIGNMENT_VIA_TASK,
              'reference': Oguid.for_object(self.task),
              'roles': ['Editor'],
              'principal': self.secretariat_user.id},
             {'cause': ASSIGNMENT_VIA_TASK,
              'roles': ['Editor'],
              'reference': Oguid.for_object(self.task),
              'principal': self.administrator.id}], storage._storage())
        self.assertEqual([self.regular_user.id, self.secretariat_user.id], self.task.get_former_responsibles())

        # close
        browser.open(self.task, view='tabbedview_view-overview')
        browser.click_on('Close')
        browser.fill({'Response': 'Done!'})
        browser.click_on('Save')

        self.assertEqual([], storage._storage())
        self.assertEqual([], self.task.get_former_responsibles())

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
              'principal': self.regular_user.id},
             {'cause': ASSIGNMENT_VIA_TASK_AGENCY,
              'roles': ['Editor'],
              'reference': Oguid.for_object(self.task),
              'principal': 'fa_inbox_users'}], storage._storage())

        # close
        browser.open(self.task, view='tabbedview_view-overview')
        browser.click_on('Close')
        browser.fill({'Response': 'Done!'})
        browser.click_on('Save')

        self.assertEqual(
            [{'cause': ASSIGNMENT_VIA_TASK,
              'roles': ['Editor'],
              'reference': Oguid.for_object(self.task),
              'principal': self.regular_user.id},
             {'cause': ASSIGNMENT_VIA_TASK_AGENCY,
              'roles': ['Editor'],
              'reference': Oguid.for_object(self.task),
              'principal': 'fa_inbox_users'}], storage._storage())

    @browsing
    def test_reassigning_task_does_not_revoke_responsible_roles_on_task(self, browser):
        self.login(self.regular_user, browser)

        roles = self.task.get_local_roles_for_userid(
            self.regular_user.id)
        self.assertEqual(('Editor',), roles)

        roles = self.task.get_local_roles_for_userid(
            self.secretariat_user.id)
        self.assertEqual(tuple(), roles)

        # assign
        browser.open(self.task, view='tabbedview_view-overview')
        browser.click_on('Reassign')
        form = browser.find_form_by_field('Responsible')
        form.find_widget('Responsible').fill(self.secretariat_user)
        browser.fill({'Response': 'For you'})
        browser.click_on('Assign')

        # old responsible's permissions were not revoked
        roles = self.task.get_local_roles_for_userid(
            self.regular_user.id)
        self.assertEqual(('Editor', ), roles)

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
        browser.click_on('Reassign')
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
    def test_reject_task_does_not_revoke_responsible_roles_on_task(self, browser):
        self.login(self.regular_user, browser)

        self.set_workflow_state('task-state-open', self.subtask)

        roles = self.subtask.get_local_roles_for_userid(self.regular_user.id)
        self.assertEqual(('Editor',), roles)

        roles = self.subtask.get_local_roles_for_userid(self.dossier_responsible.id)
        self.assertEqual(('Owner', ), roles)

        # reject
        browser.open(self.subtask, view='tabbedview_view-overview')
        browser.click_on('Reject')
        browser.fill({'Response': 'Nope!'})
        browser.click_on('Save')

        # old responsible's permissions were not revoked
        # but old responsible is added to former responsibles list
        roles = self.subtask.get_local_roles_for_userid(self.regular_user.id)
        self.assertEqual(('Editor',), roles)
        self.assertEqual([self.regular_user.id], self.subtask.get_former_responsibles())

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
        # reassign
        browser.open(self.task, view='tabbedview_view-overview')
        browser.click_on('Reassign')
        form = browser.find_form_by_field('Responsible')
        form.find_widget('Responsible').fill(self.administrator)
        browser.fill({'Response': 'For you'})
        browser.click_on('Assign')

        self.set_workflow_state('task-state-tested-and-closed', self.subtask)
        self.set_workflow_state('task-state-resolved', self.task)

        storage = RoleAssignmentManager(self.document).storage
        assignments = filter(lambda assignment: assignment[
                             'reference'] == Oguid.for_object(self.task).id, storage._storage())
        self.assertEqual([self.regular_user.id, u'fa_inbox_users', self.administrator.id], [
                         assignment['principal'] for assignment in assignments])

        # close
        browser.open(self.task, view='tabbedview_view-overview')
        browser.click_on('Close')
        browser.fill({'Response': 'Done!'})
        browser.click_on('Save')
        assignments = filter(lambda assignment: assignment[
                             'reference'] == Oguid.for_object(self.task).id, storage._storage())
        self.assertEqual([], assignments)

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
        browser.click_on('Close')
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

        # reassign
        browser.open(self.task, view='tabbedview_view-overview')
        browser.click_on('Reassign')
        form = browser.find_form_by_field('Responsible')
        form.find_widget('Responsible').fill(self.secretariat_user)
        browser.fill({'Response': 'For you'})
        browser.click_on('Assign')

        expected_assignments = [{'cause': ASSIGNMENT_VIA_TASK,
                                 'roles': ['Reader', 'Editor'],
                                 'reference': Oguid.for_object(self.task),
                                 'principal': self.regular_user.id},
                                {'cause': ASSIGNMENT_VIA_TASK_AGENCY,
                                 'roles': ['Reader', 'Editor'],
                                 'reference': Oguid.for_object(self.task),
                                 'principal': u'fa_inbox_users'},
                                {'cause': ASSIGNMENT_VIA_TASK,
                                 'roles': ['Reader', 'Editor'],
                                 'reference': Oguid.for_object(self.task),
                                 'principal': self.secretariat_user.id}]

        document_storage = RoleAssignmentManager(self.proposaldocument).storage
        self.assertEqual(expected_assignments, document_storage._storage())

        proposal_storage = RoleAssignmentManager(self.proposal).storage
        self.assertEqual(expected_assignments, proposal_storage._storage())

        self.set_workflow_state('task-state-tested-and-closed', self.subtask)
        self.set_workflow_state('task-state-resolved', self.task)
        notify(ObjectModifiedEvent(self.task))

        browser.open(self.task, view='tabbedview_view-overview')
        browser.click_on('Close')
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
        browser.click_on('Close')
        browser.click_on('Save')

        self.assertEqual(expected_assignments, proposal_storage._storage())
        self.assertEqual(expected_assignments, document_storage._storage())

    @browsing
    def test_closing_a_task_revokes_responsible_roles_on_distinct_parent(self, browser):
        self.login(self.dossier_responsible, browser=browser)
        # reassign
        browser.open(self.meeting_task, view='tabbedview_view-overview')
        browser.click_on('Reassign')
        form = browser.find_form_by_field('Responsible')
        form.find_widget('Responsible').fill(self.administrator)
        browser.click_on('Assign')

        self.set_workflow_state('task-state-resolved', self.meeting_task)

        storage = RoleAssignmentManager(self.meeting_dossier).storage

        self.assertEqual(
            [{'cause': ASSIGNMENT_VIA_TASK,
              'roles': ['TaskResponsible'],
              'reference': Oguid.for_object(self.meeting_task),
              'principal': self.dossier_responsible.id},
             {'cause': ASSIGNMENT_VIA_TASK_AGENCY,
              'roles': ['TaskResponsible'],
              'reference': Oguid.for_object(self.meeting_task),
              'principal': 'fa_inbox_users'},
             {'cause': ASSIGNMENT_VIA_TASK,
              'roles': ['TaskResponsible'],
              'reference': Oguid.for_object(self.meeting_subtask),
              'principal': self.dossier_responsible.id},
             {'cause': ASSIGNMENT_VIA_TASK_AGENCY,
              'roles': ['TaskResponsible'],
              'reference': Oguid.for_object(self.meeting_subtask),
              'principal': 'fa_inbox_users'},
             {'cause': ASSIGNMENT_VIA_TASK,
              'roles': ['TaskResponsible'],
              'reference': Oguid.for_object(self.meeting_task),
              'principal': self.administrator.id}],
            storage._storage())

        # close subtask
        browser.open(self.meeting_subtask, view='tabbedview_view-overview')
        browser.click_on('Close')
        browser.click_on('Save')

        browser.open(self.meeting_task, view='tabbedview_view-overview')
        browser.click_on('Close')
        browser.click_on('Save')

        self.assertEqual([], storage._storage())
        self.assertEqual(
            ((self.committee_responsible.id, ('Owner',)),),
            self.meeting_dossier.get_local_roles())

    @browsing
    def test_closing_does_not_revoke_roles_on_distinct_parent_if_revoke_permission_is_false(self, browser):
        self.login(self.dossier_responsible, browser=browser)
        self.set_workflow_state('task-state-resolved', self.meeting_task)
        self.meeting_task.revoke_permissions = False

        self.assertEqual(
            ((self.committee_responsible.id, ('Owner',)),
             ('fa_inbox_users', ('TaskResponsible',)),
             (self.dossier_responsible.id, ('TaskResponsible',))),
            self.meeting_dossier.get_local_roles())

        storage = RoleAssignmentManager(self.meeting_dossier).storage
        self.assertEqual(
            [{'cause': ASSIGNMENT_VIA_TASK,
              'roles': ['TaskResponsible'],
              'reference': Oguid.for_object(self.meeting_task),
              'principal': self.dossier_responsible.id},
             {'cause': ASSIGNMENT_VIA_TASK_AGENCY,
              'roles': ['TaskResponsible'],
              'reference': Oguid.for_object(self.meeting_task),
              'principal': 'fa_inbox_users'},
             {'cause': ASSIGNMENT_VIA_TASK,
              'roles': ['TaskResponsible'],
              'reference': Oguid.for_object(self.meeting_subtask),
              'principal': self.dossier_responsible.id},
             {'cause': ASSIGNMENT_VIA_TASK_AGENCY,
              'roles': ['TaskResponsible'],
              'reference': Oguid.for_object(self.meeting_subtask),
              'principal': 'fa_inbox_users'}],
            storage._storage())

        # close subtask
        browser.open(self.meeting_subtask, view='tabbedview_view-overview')
        browser.click_on('Close')
        browser.click_on('Save')

        browser.open(self.meeting_task, view='tabbedview_view-overview')
        browser.click_on('Close')
        browser.click_on('Save')

        self.assertEqual(
            [{'cause': ASSIGNMENT_VIA_TASK,
              'roles': ['TaskResponsible'],
              'reference': Oguid.for_object(self.meeting_task),
              'principal': self.dossier_responsible.id},
             {'cause': ASSIGNMENT_VIA_TASK_AGENCY,
              'roles': ['TaskResponsible'],
              'reference': Oguid.for_object(self.meeting_task),
              'principal': 'fa_inbox_users'}],
            storage._storage())
        self.assertEqual(
            ((self.committee_responsible.id, ('Owner',)),
             ('fa_inbox_users', ('TaskResponsible',)),
             (self.dossier_responsible.id, ('TaskResponsible',))),
            self.meeting_dossier.get_local_roles())

    @browsing
    def test_cancelling_a_task_revokes_roles(self, browser):
        self.login(self.dossier_responsible, browser=browser)
        self.set_workflow_state('task-state-open', self.subtask)

        # cancel
        browser.open(self.subtask, view='tabbedview_view-overview')
        browser.click_on('Close')
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
        browser.click_on('Close')
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
        browser.click_on('Close')
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
        browser.click_on('Close')
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
              'principal': self.regular_user.id},
             {'cause': ASSIGNMENT_VIA_TASK_AGENCY,
              'roles': ['Editor'],
              'reference': Oguid.for_object(self.seq_subtask_2),
              'principal': 'fa_inbox_users'}], storage._storage())

        # skip
        browser.open(self.seq_subtask_2, view='tabbedview_view-overview')
        browser.click_on('Skip')
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
              'principal': self.regular_user.id},
             {'cause': ASSIGNMENT_VIA_TASK_AGENCY,
              'roles': ['Editor'],
              'reference': Oguid.for_object(self.seq_subtask_2),
              'principal': 'fa_inbox_users'}], storage._storage())

        # skip
        browser.open(self.seq_subtask_2, view='tabbedview_view-overview')
        browser.click_on('Skip')
        browser.click_on('Save')

        self.assertEqual(
            [{'cause': ASSIGNMENT_VIA_TASK,
              'roles': ['Editor'],
              'reference': Oguid.for_object(self.seq_subtask_2),
              'principal': self.regular_user.id},
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

    @browsing
    def test_closed_to_open_readd_localroles(self, browser):
        self.login(self.dossier_responsible, browser=browser)
        self.set_workflow_state('task-state-tested-and-closed', self.subtask)
        self.set_workflow_state('task-state-resolved', self.task)

        # close task
        browser.open(self.task, view='tabbedview_view-overview')
        browser.click_on('Close')
        browser.fill({'Response': 'Done!'})
        browser.click_on('Save')

        storage = RoleAssignmentManager(self.task).storage
        self.assertEqual([], storage._storage())

        # Request revision by administrator
        self.login(self.administrator, browser=browser)
        browser.open(self.task, view='tabbedview_view-overview')
        browser.click_on('Request revision')
        browser.fill({'Response': 'Please correct this!'})
        browser.click_on('Save')

        self.assertEqual(
            [{'cause': ASSIGNMENT_VIA_TASK,
              'roles': ['Editor'],
              'reference': Oguid.for_object(self.task),
              'principal': self.regular_user.id},
             {'cause': ASSIGNMENT_VIA_TASK_AGENCY,
              'roles': ['Editor'],
              'reference': Oguid.for_object(self.task),
              'principal': 'fa_inbox_users'}], storage._storage())

    @browsing
    def test_closing_a_forwarding_revokes_roles_on_inbox(self, browser):
        self.login(self.secretariat_user, browser=browser)

        storage = RoleAssignmentManager(self.inbox).storage
        forwarding_oguid = Oguid.for_object(self.inbox_forwarding)
        self.assertTrue(self.inbox_forwarding.revoke_permissions)
        self.assertEqual(
            [
                {
                    "cause": 3,
                    "reference": None,
                    "roles": ["Contributor", "Editor", "Reader"],
                    "principal": self.secretariat_user.id,
                },
                {
                    "cause": 3,
                    "reference": None,
                    "roles": ["Contributor", "Editor", "Reader"],
                    "principal": self.dossier_manager.id,
                },
                {
                    "cause": ASSIGNMENT_VIA_TASK,
                    "roles": ["TaskResponsible"],
                    "reference": forwarding_oguid,
                    'principal': self.regular_user.id,
                },
                {
                    "cause": ASSIGNMENT_VIA_TASK_AGENCY,
                    "roles": ["TaskResponsible"],
                    "reference": forwarding_oguid,
                    "principal": "fa_inbox_users",
                },
            ], storage._storage())

        browser.open(self.inbox_forwarding, method="POST", headers=self.api_headers,
                     view='@workflow/forwarding-transition-close')

        self.assertEqual(
            [
                {
                    "cause": 3,
                    "reference": None,
                    "roles": ["Contributor", "Editor", "Reader"],
                    "principal": self.secretariat_user.id,
                },
                {
                    "cause": 3,
                    "reference": None,
                    "roles": ["Contributor", "Editor", "Reader"],
                    "principal": self.dossier_manager.id,
                },
            ], storage._storage())

    @browsing
    def test_assign_forwarding_to_a_dossier_revokes_roles_on_inbox(self, browser):
        self.login(self.secretariat_user, browser=browser)

        storage = RoleAssignmentManager(self.inbox).storage
        forwarding_oguid = Oguid.for_object(self.inbox_forwarding)
        self.assertTrue(self.inbox_forwarding.revoke_permissions)
        self.assertEqual(
            [
                {
                    "cause": 3,
                    "reference": None,
                    "roles": ["Contributor", "Editor", "Reader"],
                    "principal": self.secretariat_user.id,
                },
                {
                    "cause": 3,
                    "reference": None,
                    "roles": ["Contributor", "Editor", "Reader"],
                    "principal": self.dossier_manager.id,
                },
                {
                    "cause": ASSIGNMENT_VIA_TASK,
                    "roles": ["TaskResponsible"],
                    "reference": forwarding_oguid,
                    'principal': self.regular_user.id,
                },
                {
                    "cause": ASSIGNMENT_VIA_TASK_AGENCY,
                    "roles": ["TaskResponsible"],
                    "reference": forwarding_oguid,
                    "principal": "fa_inbox_users",
                },
            ], storage._storage())

        browser.open(
            self.inbox_forwarding.absolute_url(),
            view='@assign-to-dossier',
            method='POST',
            headers=self.api_headers,
            data=json.dumps({
                'target_uid': self.dossier.UID(),
            }))

        self.assertEqual(201, browser.status_code)
        self.assertEqual(
            [
                {
                    "cause": 3,
                    "reference": None,
                    "roles": ["Contributor", "Editor", "Reader"],
                    "principal": self.secretariat_user.id,
                },
                {
                    "cause": 3,
                    "reference": None,
                    "roles": ["Contributor", "Editor", "Reader"],
                    "principal": self.dossier_manager.id,
                },
            ], storage._storage())


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
        self.login(self.secretariat_user, browser=browser)

        task = create(Builder('task')
                      .within(self.dossier)
                      .titled(u'Aufgabe 1')
                      .having(responsible_client='fa',
                              responsible=self.secretariat_user.id,
                              issuer=self.dossier_responsible.id,
                              task_type='direct-execution',
                              deadline=date(2016, 11, 1))
                      .in_state('task-state-in-progress')
                      .relate_to(self.document))

        principal = 'user:{}'.format(self.secretariat_user.id)

        self.assertIn(principal,
                      index_data_for(self.dossier)['allowedRolesAndUsers'])
        self.assertIn(principal,
                      index_data_for(self.subdossier)['allowedRolesAndUsers'])
        self.assertIn(principal,
                      index_data_for(self.subsubdossier)['allowedRolesAndUsers'])

        browser.open(task, view='tabbedview_view-overview')
        browser.click_on('Close')
        browser.click_on('Save')

        self.assertNotIn(principal,
                         index_data_for(self.dossier)['allowedRolesAndUsers'])
        self.assertNotIn(principal,
                         index_data_for(self.subdossier)['allowedRolesAndUsers'])
        self.assertNotIn(principal,
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
