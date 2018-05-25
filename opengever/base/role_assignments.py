from opengever.base.oguid import Oguid
from persistent.list import PersistentList
from persistent.mapping import PersistentMapping
from zope.annotation.interfaces import IAnnotations


ASSIGNNMENT_VIA_TASK = 1
ASSIGNNMENT_VIA_TASK_AGENCY = 2
ASSIGNNMENT_VIA_SHARING = 3


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

    def _upate_local_roles(self):
        for principal, roles in self.storage.summarize():
            self.context.manage_setLocalRoles(
                principal, [role for role in roles])

        self.context.reindexObjectSecurity()
