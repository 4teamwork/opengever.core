from Acquisition import aq_chain
from Acquisition import aq_inner
from opengever.base.oguid import Oguid
from persistent.list import PersistentList
from persistent.mapping import PersistentMapping
from plone.app.layout.navigation.interfaces import INavigationRoot
from Products.CMFPlone.utils import base_hasattr
from zope.annotation.interfaces import IAnnotations


ASSIGNNMENT_VIA_TASK = 1
ASSIGNNMENT_VIA_TASK_AGENCY = 2
ASSIGNNMENT_VIA_SHARING = 3


class RoleAssignment(object):

    def __init__(self, principal, roles, cause, reference=None):
        self.principal = principal
        self.roles = roles
        self.cause = cause
        self.reference = reference

    def cause_title(self):
        return self.cause

    def serialize(self):
        data = {'principal': self.principal,
                'roles': self.roles,
                'cause': {
                    'id': self.cause,
                    'title': self.cause_title(),
                },
         'reference': None}

        if self.reference:
            reference_obj = Oguid.parse(self.reference).resolve_object()
            data['reference'] = {
                'url': reference_obj.absolute_url(),
                'title': reference_obj.Title().decode('utf-8')}

        return data


class SharingRoleAssignment(RoleAssignment):

    cause = ASSIGNNMENT_VIA_SHARING

    def __init__(self, principal, roles):
        self.principal = principal
        self.roles = roles
        self.reference = None


class RoleAssignmentStorage(object):

    key = 'ROLE_ASSIGNMENTS'

    def __init__(self, context):
        self.context = context

    def _storage(self):
        ann = IAnnotations(self.context)
        if self.key not in ann.keys():
            ann[self.key] = PersistentList()

        return ann[self.key]

    def get(self, principal, cause, reference):
        for item in self._storage():
            if item['principal'] == principal and item['cause'] == cause:
                if not reference:
                    return item
                elif item['reference'] == reference:
                    return item

    def drop_all(self, cause):
        to_remove = [item for item in
                     self._storage() if item['cause'] == cause]
        for item in to_remove:
            self._storage().remove(item)

    def get_all_by_cause(self, cause):
        return [item for item in self._storage() if item['cause'] == cause]

    def get_all_by_principal(self, principal_id):
        return [item for item in
                self._storage() if item['principal'] == principal_id]

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

    def summarize(self):
        data = {}
        for assignment in self._storage():
            if assignment['principal'] not in data.keys():
                data[assignment['principal']] = list(assignment['roles'])
            else:
                data[assignment['principal']] += assignment['roles']

        for principal, roles in data.items():
            yield principal, [role for role in set(roles)]


class RoleAssignmentManager(object):

    def __init__(self, context):
        self.context = context
        self.storage = RoleAssignmentStorage(self.context)

    def add(self, principal, roles, cause, reference=None):
        self.storage.add_or_update(principal, roles, cause, reference)
        self._upate_local_roles()

    def get_assignments_by_cause(self, cause):
        return self.storage.get_all_by_cause(cause)

    def get_assignments_chain(self, principal_id):
        """Recursively returns assignments till the local_roles
        inheritance is blocked.
        """

        assignments = []

        for obj in aq_chain(aq_inner(self.context)):
            manager = RoleAssignmentManager(obj)
            assignments += manager.get_assignments_by_principal_id(
                principal_id)

            if INavigationRoot.providedBy(obj):
                break

            if base_hasattr(self.context, '__ac_local_roles_block__') \
               and self.context.__ac_local_roles_block__:
                break

        return assignments

    def get_assignments_by_principal_id(self, principal_id):
        return [RoleAssignment(**data) for data
                in self.storage.get_all_by_principal(principal_id)]

    def set(self, assignments):
        cause = assignments[0].cause
        if len(set([asg.cause for asg in assignments])) > 1:
            raise ValueError('All assignments need to have the same cause')

        self.storage.drop_all(cause)

        for assignment in assignments:
            self.storage.add_or_update(
                assignment.principal, assignment.roles, assignment.cause,
                assignment.reference)

        self._upate_local_roles()

    def _upate_local_roles(self):
        for principal, roles in self.storage.summarize():
            self.context.manage_setLocalRoles(
                principal, [role for role in roles])

        self.context.reindexObjectSecurity()
