from Acquisition import aq_base
from Acquisition import aq_inner
from Acquisition import aq_parent
from opengever.base.role_assignments import ASSIGNMENT_VIA_TASK
from opengever.base.role_assignments import ASSIGNMENT_VIA_TASK_AGENCY
from opengever.base.role_assignments import RoleAssignmentManager
from opengever.base.role_assignments import TaskAgencyRoleAssignment
from opengever.base.role_assignments import TaskRoleAssignment
from opengever.globalindex.handlers.task import sync_task
from opengever.ogds.base.utils import get_current_org_unit
from zope.container.interfaces import IContainerModifiedEvent


class LocalRolesSetter(object):
    """Sets local roles.
    """

    def __init__(self, task):
        self.task = task
        self._inbox_group_id = None
        self._permission_identifier = None
        self.event = None
        self._inbox_group = None

    def set_roles(self, event):
        if self.task.is_in_final_state:
            return

        self.event = event
        self.set_roles_on_task()
        self.globalindex_reindex_task()
        self.set_roles_on_related_items()
        self.set_roles_on_distinct_parent()

    def revoke_roles(self):
        self.revoke_roles_on_task()
        self.globalindex_reindex_task()
        self.revoke_on_related_items()
        self.revoke_on_distinct_parent()

    @property
    def responsible_permission_identfier(self):
        """Returns the responsible pricipal. This may be the userid
        of a user which is able to log in or the principal of a group,
        if a inbox was selected.
        """
        # cache information
        if not self._permission_identifier:
            actor = self.task.get_responsible_actor()
            self._permission_identifier = actor.permission_identifier

            if isinstance(self._permission_identifier, unicode):
                self._permission_identifier = (
                    self._permission_identifier.encode('utf-8')
                    )

        return self._permission_identifier

    @property
    def inbox_group_id(self):
        if self._inbox_group_id is None:
            self._inbox_group = (
                self.task.get_responsible_org_unit().inbox_group.groupid
                )

        return self._inbox_group

    def is_inboxgroup_agency_active(self):
        return get_current_org_unit().is_inboxgroup_agency_active

    def _add_local_roles(self, context, principal, roles, is_agency=False):
        """Adds local roles to the context.
        `roles` example:
        {'peter': ('Reader', 'Editor')}
        """

        assignment = TaskRoleAssignment(principal, roles, self.task)
        if is_agency:
            assignment = TaskAgencyRoleAssignment(principal, roles, self.task)

        RoleAssignmentManager(context).add_or_update_assignment(assignment)

    def set_roles_on_task(self):
        """Set local roles on task
        """
        self._add_local_roles(
            self.task,
            self.responsible_permission_identfier,
            ('Editor', ),
            )

        if self.is_inboxgroup_agency_active() and self.inbox_group_id:
            self._add_local_roles(self.task, self.inbox_group_id,
                                  ('Editor', ), is_agency=True)

    def globalindex_reindex_task(self):
        """We need to reindex the task in globalindex. This was done
        already with an earlier event handler - but we have just changed
        the roles which are indexed too (allowed users).
        """
        sync_task(self.task, self.event)

    def get_distinct_parent(self):
        context = self.task
        while context.Type() == self.task.Type():
            context = aq_parent(aq_inner(context))

        return context

    def set_roles_on_distinct_parent(self):
        """Set local roles on next parent having a different content type."""
        context = self.get_distinct_parent()

        self._add_local_roles(
            context,
            self.responsible_permission_identfier,
            ('Contributor', ),
            )

        if self.is_inboxgroup_agency_active() and self.inbox_group_id:
            self._add_local_roles(context, self.inbox_group_id,
                                  ('Contributor', ), is_agency=True)

    def set_roles_on_related_items(self):
        """Set local roles on related items (usually documents)."""
        roles = ['Reader']
        if self.task.task_type_category == 'bidirectional_by_reference':
            roles.append('Editor')

        for item in getattr(aq_base(self.task), 'relatedItems', []):
            self._add_local_roles(
                item.to_object,
                self.responsible_permission_identfier,
                roles,
                )

            if self.is_inboxgroup_agency_active() and self.inbox_group_id:
                self._add_local_roles(
                    item.to_object, self.inbox_group_id, roles, is_agency=True)

    def revoke_roles_on_task(self):
        manager = RoleAssignmentManager(self.task)
        manager.clear(ASSIGNMENT_VIA_TASK,
                      self.responsible_permission_identfier, self.task)
        manager.clear(ASSIGNMENT_VIA_TASK_AGENCY,
                      self.inbox_group_id, self.task)

    def revoke_on_related_items(self):
        for item in getattr(aq_base(self.task), 'relatedItems', []):
            manager = RoleAssignmentManager(item.to_object)
            manager.clear(ASSIGNMENT_VIA_TASK,
                          self.responsible_permission_identfier, self.task)
            manager.clear(ASSIGNMENT_VIA_TASK_AGENCY,
                          self.inbox_group_id, self.task)

    def revoke_on_distinct_parent(self):
        manager = RoleAssignmentManager(self.get_distinct_parent())
        manager.clear(ASSIGNMENT_VIA_TASK,
                      self.responsible_permission_identfier, self.task)
        manager.clear(ASSIGNMENT_VIA_TASK_AGENCY,
                      self.inbox_group_id, self.task)


def set_roles_after_adding(context, event):
    LocalRolesSetter(context).set_roles(event)


def set_roles_after_modifying(context, event):
    # Handle the modify event having been a removal of a related item
    setattr(
        context,
        'relatedItems',
        [item for item in getattr(context, 'relatedItems', []) if item.to_object],
    )

    if IContainerModifiedEvent.providedBy(event):
        return

    LocalRolesSetter(context).set_roles(event)
