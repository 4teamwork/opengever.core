from Acquisition import aq_base
from Acquisition import aq_inner
from Acquisition import aq_parent
from opengever.base.role_assignments import ASSIGNMENT_VIA_TASK
from opengever.base.role_assignments import ASSIGNMENT_VIA_TASK_AGENCY
from opengever.base.role_assignments import RoleAssignmentManager
from opengever.base.role_assignments import TaskAgencyRoleAssignment
from opengever.base.role_assignments import TaskRoleAssignment
from opengever.base.security import reindex_object_security_without_children
from opengever.document.document import IBaseDocument
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.globalindex.handlers.task import sync_task
from opengever.meeting.proposal import IBaseProposal
from opengever.ogds.base.actor import Actor
from opengever.ogds.base.utils import get_current_org_unit
from persistent.list import PersistentList
from plone import api
from zope.annotation.interfaces import IAnnotations
from zope.component import getUtility
from zope.intid import IIntIds


RELATED_ITEMS_KEY = 'opengever.task.related_items'


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
        self.task.reset_former_responsibles()

    def get_permission_identifier(self, actorid):
        actor = Actor.lookup(actorid)
        if isinstance(actor.permission_identifier, unicode):
            return actor.permission_identifier.encode('utf-8')
        return actor.permission_identifier

    @property
    def responsible_permission_identfier(self):
        """Returns the responsible pricipal. This may be the userid
        of a user which is able to log in or the principal of a group,
        if a inbox was selected.
        """
        # cache information
        if not self._permission_identifier:
            self._permission_identifier = self.get_permission_identifier(self.task.responsible)
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

    def _add_local_roles(self, context, principal, agency_principal, roles, reindex=True):
        """Adds local roles to the context.
        `roles` example:
        {'peter': ('Reader', 'Editor')}
        """

        assignments = [TaskRoleAssignment(principal, roles, self.task), ]
        if agency_principal:
            assignments.append(TaskAgencyRoleAssignment(agency_principal, roles, self.task))

        RoleAssignmentManager(context).add_or_update_assignments(assignments, reindex=reindex)

    def _add_informed_roles(self, context, roles, reindex=True):
        """Adds 'Reader' role to informed principals."""
        informed_principals = self.task.informed_principals
        for principal in informed_principals:
            principal = self.get_permission_identifier(principal)
            RoleAssignmentManager(context).add_or_update_assignments(
                [TaskRoleAssignment(principal, roles, context)], reindex=reindex)

    def _should_add_agency_localroles(self):
        if self.task.is_private:
            return False

        return self.is_inboxgroup_agency_active() and self.inbox_group_id

    def set_roles_on_task(self):
        """Set local roles on task
        """
        principal = self.responsible_permission_identfier
        agency_principal = None

        if self._should_add_agency_localroles():
            agency_principal = self.inbox_group_id

        self._add_local_roles(self.task, principal, agency_principal, ('Editor', ))

        # Grant "Reader" role to informed principals
        self._add_informed_roles(self.task, ('Reader',))

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
        distinct_parent = self.get_distinct_parent()

        principal = self.responsible_permission_identfier
        agency_principal = None

        if self._should_add_agency_localroles():
            agency_principal = self.inbox_group_id

        self._add_local_roles(distinct_parent, principal, agency_principal,
                              ('TaskResponsible', ), reindex=False)
        self._add_informed_roles(distinct_parent, ('TaskResponsible',))

        # We disabled reindexObjectSecurity and reindex the security manually
        # instead, to avoid reindexing all objects including all documents.
        # Because there View permission isn't affected by the `TaskResponsible`
        # role on the dossier.
        catalog = api.portal.get_tool('portal_catalog')
        subdossiers = [brain.getObject() for brain in catalog(
            object_provides=[IDossierMarker.__identifier__,
                             IBaseProposal.__identifier__],
            path='/'.join(distinct_parent.getPhysicalPath()))]

        for dossier in subdossiers:
            reindex_object_security_without_children(dossier)

    def set_roles_on_related_items(self):
        """Set local roles on related items (usually documents)."""

        # Some related items might have been deleted, we need to revoke the roles
        # on those first.
        annotations = IAnnotations(self.task)
        to_ids = [item.to_id for item in getattr(aq_base(self.task), 'relatedItems', [])]
        if RELATED_ITEMS_KEY not in annotations:
            annotations[RELATED_ITEMS_KEY] = PersistentList(to_ids)
        to_ids_set = set(to_ids)
        annotations_related_items_set = set(annotations[RELATED_ITEMS_KEY])
        deleted_intids = annotations_related_items_set - to_ids_set
        if deleted_intids:
            intids = getUtility(IIntIds)
            for deleted_intid in deleted_intids:
                try:
                    obj = intids.getObject(deleted_intid)
                except KeyError:
                    # obj has been deleted
                    continue
                self._revoke_roles(obj)

        if annotations_related_items_set != to_ids_set:
            annotations[RELATED_ITEMS_KEY] = PersistentList(to_ids)

        roles = ['Reader']
        if self.task.task_type_category in [
                'bidirectional_by_reference', 'unidirectional_by_value']:
            roles.append('Editor')

        for item in getattr(aq_base(self.task), 'relatedItems', []):
            principal = self.responsible_permission_identfier
            agency_principal = None
            document = item.to_object

            if self._should_add_agency_localroles():
                agency_principal = self.inbox_group_id

            self._add_local_roles(
                document, principal, agency_principal, roles)

            # Grant "Reader" role to informed principals on related items
            self._add_informed_roles(document, ('Reader',))

            if self._is_inside_a_proposal(document):
                proposal = document.get_proposal()
                self._add_local_roles(
                    proposal, principal, agency_principal, roles)

                # Grant "Reader" role to informed principals on related proposal
                self._add_informed_roles(proposal, ('Reader',))

    def _is_inside_a_proposal(self, maybe_document):
        if not IBaseDocument.providedBy(maybe_document):
            return False

        return maybe_document.is_inside_a_proposal()

    def _revoke_informed_principals_roles(self, context, reindex=True):
        manager = RoleAssignmentManager(context)
        informed_principals = self.task.informed_principals
        for principal in informed_principals:
            principal = self.get_permission_identifier(principal)
            manager.clear(ASSIGNMENT_VIA_TASK, principal, context, reindex)

    def _revoke_roles(self, obj, reindex=True):
        manager = RoleAssignmentManager(obj)
        manager.clear(ASSIGNMENT_VIA_TASK,
                      self.responsible_permission_identfier, self.task, reindex)
        manager.clear(ASSIGNMENT_VIA_TASK_AGENCY,
                      self.inbox_group_id, self.task, reindex)

        for former_responsible in self.task.get_former_responsibles():
            manager.clear(ASSIGNMENT_VIA_TASK,
                          self.get_permission_identifier(former_responsible),
                          self.task, reindex)

    def revoke_roles_on_task(self):
        self._revoke_roles(self.task)
        self._revoke_informed_principals_roles(self.task)

    def revoke_on_related_items(self):
        for item in getattr(aq_base(self.task), 'relatedItems', []):
            document = item.to_object

            self._revoke_roles(document)
            self._revoke_informed_principals_roles(document)

            if self._is_inside_a_proposal(document):
                proposal = document.get_proposal()
                self._revoke_roles(proposal)
                self._revoke_informed_principals_roles(proposal)

    def revoke_on_distinct_parent(self):
        distinct_parent = self.get_distinct_parent()

        # We disabled reindexObjectSecurity and reindex the security manually
        # instead, to avoid reindexing all objects including all documents.
        # Because there View permission isn't affected by the `Contributor` role
        # on the dossier.
        catalog = api.portal.get_tool('portal_catalog')
        subdossiers = [brain.getObject() for brain in catalog(
            object_provides=[IDossierMarker.__identifier__,
                             IBaseProposal.__identifier__],
            path='/'.join(distinct_parent.getPhysicalPath()))]

        self._revoke_roles(distinct_parent, reindex=False)
        self._revoke_informed_principals_roles(distinct_parent, reindex=False)

        for dossier in subdossiers:
            reindex_object_security_without_children(dossier)
