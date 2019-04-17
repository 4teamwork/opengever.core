from opengever.base import _
from opengever.base.oguid import Oguid
from persistent.list import PersistentList
from persistent.mapping import PersistentMapping
from zope.annotation.interfaces import IAnnotations
from zope.globalrequest import getRequest
from zope.i18n import translate


# Those numbers get persisted in the RoleAssignmentStorage (annotations)
# Do not remove them without migration
ASSIGNMENT_VIA_TASK = 1
ASSIGNMENT_VIA_TASK_AGENCY = 2
ASSIGNMENT_VIA_SHARING = 3
ASSIGNMENT_VIA_PROTECT_DOSSIER = 4
ASSIGNMENT_VIA_INVITATION = 5
ASSIGNMENT_VIA_COMMITTEE_GROUP = 6

# When copying a dossier, we keep or drop local roles depending on
# their assignment cause.
assignments_kept_when_copying = (ASSIGNMENT_VIA_SHARING,
                                 ASSIGNMENT_VIA_PROTECT_DOSSIER,
                                 ASSIGNMENT_VIA_INVITATION)


class RoleAssignment(object):

    registry = None

    def __init__(self, principal, roles, cause, reference=None):
        self.principal = principal
        self.roles = roles
        self.cause = cause
        self.reference = reference

    @classmethod
    def register(cls, subcls):
        if not cls.registry:
            cls.registry = {}
        cls.registry[subcls.cause] = subcls

    @classmethod
    def get(cls, cause, **kwargs):
        assignment = cls.registry.get(cause)
        if not assignment:
            raise ValueError(
                'No assignment class registered for `{}`'.format(cause))

        return assignment(**kwargs)

    def cause_title(self):
        raise NotImplementedError()

    def serialize(self):
        data = {'principal': self.principal,
                'roles': self.roles,
                'cause': {
                    'id': self.cause,
                    'title': translate(
                        self.cause_title(), context=getRequest())},
                'reference': None}

        if self.reference:
            reference_obj = Oguid.parse(self.reference).resolve_object()
            data['reference'] = {
                'url': reference_obj.absolute_url(),
                'title': reference_obj.Title().decode('utf-8')}

        return data


class SharingRoleAssignment(RoleAssignment):

    cause = ASSIGNMENT_VIA_SHARING

    def __init__(self, principal, roles, reference=None):
        self.principal = principal
        self.roles = roles
        self.reference = None

    def cause_title(self):
        return _(u'label_assignment_via_sharing', default=u'Via sharing')


RoleAssignment.register(SharingRoleAssignment)


class TaskRoleAssignment(RoleAssignment):

    cause = ASSIGNMENT_VIA_TASK

    def __init__(self, principal, roles, reference):
        self.principal = principal
        self.roles = roles
        self.reference = reference

    def cause_title(self):
        return _(u'label_assignment_via_task', default=u'By task')


RoleAssignment.register(TaskRoleAssignment)


class TaskAgencyRoleAssignment(RoleAssignment):

    cause = ASSIGNMENT_VIA_TASK_AGENCY

    def __init__(self, principal, roles, reference):
        self.principal = principal
        self.roles = roles
        self.reference = reference

    def cause_title(self):
        return _(u'label_assignment_via_task_agency',
                 default=u'By task agency')


RoleAssignment.register(TaskAgencyRoleAssignment)


class ProtectDossierRoleAssignment(RoleAssignment):

    cause = ASSIGNMENT_VIA_PROTECT_DOSSIER

    def __init__(self, principal, roles, reference=None):
        self.principal = principal
        self.roles = roles
        self.reference = None

    def cause_title(self):
        return _(u'label_assignment_via_protect_dossier',
                 default=u'By protect dossier')


RoleAssignment.register(ProtectDossierRoleAssignment)


class InvitationRoleAssignment(RoleAssignment):

    cause = ASSIGNMENT_VIA_INVITATION

    def __init__(self, principal, roles, reference):
        self.principal = principal
        self.roles = roles
        self.reference = reference

    def cause_title(self):
        return _(u'label_assignment_via_workspace_invitation',
                 default=u'By workspace invitation')


RoleAssignment.register(InvitationRoleAssignment)


class CommitteeGroupAssignment(RoleAssignment):

    cause = ASSIGNMENT_VIA_COMMITTEE_GROUP

    def __init__(self, principal, roles, reference):
        self.principal = principal
        self.roles = roles
        self.reference = reference

    def cause_title(self):
        return _(u'label_assignment_via_committee_group',
                 default=u'By committee group')


RoleAssignment.register(CommitteeGroupAssignment)


class RoleAssignmentStorage(object):

    key = 'ROLE_ASSIGNMENTS'

    def __init__(self, context):
        self.context = context

    def _storage(self):
        ann = IAnnotations(self.context)
        if self.key not in ann.keys():
            ann[self.key] = PersistentList()

        return ann[self.key]

    def has_storage(self):
        ann = IAnnotations(self.context)
        return self.key in ann.keys()

    def get(self, principal, cause, reference):
        for item in self._storage():
            if item['principal'] == principal and item['cause'] == cause:
                if not reference:
                    return item
                elif item['reference'] == reference:
                    return item

    def get_all(self):
        return self._storage()

    def clear_by_cause_and_principal(self, cause, principal):
        item = self.get_by_cause_and_principal(cause, principal)
        if item:
            self._storage().remove(item)

    def clear_by_cause(self, cause):
        for item in self.get_by_cause(cause):
            self._storage().remove(item)

    def clear_by_reference(self, reference):
        for item in self.get_by_reference(reference):
            self._storage().remove(item)

    def clear_all(self):
        ann = IAnnotations(self.context)
        ann[self.key] = PersistentList()

    def clear(self, item):
        self._storage().remove(item)

    def get_by_cause(self, cause):
        return [item for item in self._storage() if item['cause'] == cause]

    def get_by_principal(self, principal_id):
        return [item for item in
                self._storage() if item['principal'] == principal_id]

    def get_by_cause_and_principal(self, cause, principal):
        for item in self._storage():
            if item['cause'] == cause and item['principal'] == principal:
                return item

    def get_by_reference(self, reference):
        return [item for item in self._storage() if item['reference'] == reference]

    def add_or_update(self, principal, roles, cause, reference):
        """Add or update a role assignment
        """

        oguid = Oguid.for_object(reference).id if reference else None
        data = {
            'principal': principal,
            'roles': list(roles),
            'cause': cause,
            'reference': oguid}

        assignment = self.get(principal, cause, oguid)
        if assignment:
            assignment.update(data)
        else:
            self._storage().append(PersistentMapping(data))

    def compute_effective(self):
        data = {}
        for assignment in self._storage():
            if assignment['principal'] not in data.keys():
                data[assignment['principal']] = list(assignment['roles'])
            else:
                data[assignment['principal']] += assignment['roles']

        for principal, roles in data.items():
            yield principal, tuple(set(roles))


class RoleAssignmentManager(object):

    def __init__(self, context):
        self.context = context
        self.storage = RoleAssignmentStorage(self.context)

    def has_storage(self):
        return self.storage.has_storage()

    def add_or_update_assignment(self, assignment, reindex=True):
        self.storage.add_or_update(assignment.principal,
                                   assignment.roles,
                                   assignment.cause,
                                   assignment.reference)
        self._update_local_roles(reindex=reindex)

    def add_or_update_assignments(self, assignments, reindex=True):
        for assignment in assignments:
            self.storage.add_or_update(assignment.principal,
                                       assignment.roles,
                                       assignment.cause,
                                       assignment.reference)

        self._update_local_roles(reindex=reindex)

    def add_or_update(self, principal, roles, cause, reference=None):
        self.storage.add_or_update(principal, roles, cause, reference)
        self._update_local_roles()

    def get_assignments_by_cause(self, cause):
        return self.storage.get_by_cause(cause)

    def get_assignments_by_principal_id(self, principal_id):
        return [RoleAssignment.get(**data) for data
                in self.storage.get_by_principal(principal_id)]

    def reset(self, assignments):
        cause = assignments[0].cause
        if len(set([asg.cause for asg in assignments])) > 1:
            raise ValueError('All assignments need to have the same cause')

        self.storage.clear_by_cause(cause)

        for assignment in assignments:
            self.storage.add_or_update(
                assignment.principal, assignment.roles, assignment.cause,
                assignment.reference)

        self._update_local_roles()

    def clear_all(self):
        """Remove all assignments.
        """
        self.storage.clear_all()
        self._update_local_roles()

    def clear_by_cause_and_principals(self, cause, principals):
        """Remove all assignments of the given cause and principals.
        """
        for principal in principals:
            self.storage.clear_by_cause_and_principal(cause, principal)

        self._update_local_roles()

    def clear_by_cause_and_principal(self, cause, principal):
        """Remove all assignments of the given cause by the given principal.
        """
        self.storage.clear_by_cause_and_principal(cause, principal)
        self._update_local_roles()

    def clear_by_reference(self, reference):
        """Remove all assignments from the given reference.
        """
        self.storage.clear_by_reference(Oguid.for_object(reference).id)
        self._update_local_roles()

    def clear(self, cause, principal, reference, reindex=True):
        item = self.storage.get(principal, cause, Oguid.for_object(reference).id)
        if not item:
            return

        self.storage.clear(item)
        self._update_local_roles(reindex=reindex)

    def set_new_owner(self, userid, reindex=True):
        """ Remove all current owners and set Owner for userid.
        """
        for principal, roles in self.context.get_local_roles():
            if 'Owner' not in roles:
                continue
            new_roles = (role for role in roles if not role == "Owner")
            self.context.manage_setLocalRoles(
                principal, new_roles, verified=True)

        self.context.manage_addLocalRoles(
                userid, ['Owner'], verified=True)

        if reindex:
            self.context.reindexObjectSecurity()

    def update_local_roles_after_copying(self, new_owner):
        """ We only delete certain local roles when copying an object
        depending on their assignment cause. We also set a new owner
        on the copied object.
        """
        are_all_local_roles_deleted = True
        for assignment in RoleAssignment.registry.values():
            if assignment.cause not in assignments_kept_when_copying:
                self.storage.clear_by_cause(assignment.cause)
            elif self.get_assignments_by_cause(assignment.cause):
                are_all_local_roles_deleted = False

        self.set_new_owner(new_owner, reindex=False)
        self._update_local_roles()
        return are_all_local_roles_deleted

    def _update_local_roles(self, reindex=True):
        current_principals = []
        owner_principals = []

        for principal, roles in self.context.get_local_roles():
            current_principals.append(principal)
            if 'Owner' in roles:
                owner_principals.append(principal)

        # drop all existing local roles
        self.context.manage_delLocalRoles(current_principals, verified=True)

        for principal, roles in self.storage.compute_effective():
            self.context.manage_setLocalRoles(
                principal, list(roles), verified=True)

        # re-add owner roles
        for principal in owner_principals:
            self.context.manage_addLocalRoles(
                principal, ['Owner'], verified=True)

        if reindex:
            self.context.reindexObjectSecurity()
