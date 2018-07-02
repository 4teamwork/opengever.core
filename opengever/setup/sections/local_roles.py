from AccessControl.interfaces import IRoleManager
from collective.blueprint.jsonmigrator.blueprint import LocalRoles
from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.utils import Expression
from opengever.base.role_assignments import SharingRoleAssignment
from opengever.base.role_assignments import RoleAssignmentManager
from zope.interface import classProvides, implements
import logging


ROLE_MAPPING = {
    'read_dossiers_access': 'Reader',
    'add_dossiers_access': 'Contributor',
    'edit_dossiers_access': 'Editor',
    'close_dossiers_access': 'Reviewer',
    'reactivate_dossiers_access': 'Publisher',
    'manage_dossiers_access': 'DossierManager',
}


class BlockLocalRoleInheritance(object):
    """ Block the inheritance of ac_local_roles
    """

    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.context = transmogrifier.context
        self.logger = logging.getLogger(options['blueprint'])
        self.fields = Expression(options['fields'], transmogrifier, name,
                                 options)

    def __iter__(self):
        for item in self.previous:
            self.row_name = self.fields(item)[0]

            # Look for the rows value.
            block = item.get(self.row_name)

            # Should we block the inheritance?
            if not block:
                yield item
                continue

            # Get the object
            obj = self.context.unrestrictedTraverse(
                item['_path'].lstrip('/'), None)

            if obj is None:
                yield item
                continue

            # Block the inheritance of the objects security
            obj.__ac_local_roles_block__ = True
            obj.reindexObjectSecurity()

            yield item


class InsertLocalRolesSection(object):
    """Prepare localroles to set them correctly
    """

    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.logger = logging.getLogger(options['blueprint'])
        self.fields = Expression(options['fields'], transmogrifier, name,
                                 options)

    def __iter__(self):

        for item in self.previous:
            group_mapping = {}

            # Get the row-headers. This are the rolenames
            for field in self.fields(item):

                # Look for mapped groups
                for group in self._get_groups(item, field):

                    if not group:
                        continue

                    # We append the group to the groupmapping.
                    if not group_mapping.get(group, None):
                        group_mapping[group] = []
                    group_mapping[group] += [ROLE_MAPPING.get(field, field)]

            # Format for _ac_local_roles:
            # "_ac_local_roles": {"admin": ["Owner"]},
            item['_ac_local_roles'] = group_mapping
            yield item

    def _get_groups(self, item, field):
        """Look for groups in the given row (field), split by comma and strip
        leading and trailing spaces.
        """
        return [group.strip() for group in item.get(field, '').split(',')]


class LocalRolesSetter(LocalRoles):

    classProvides(ISectionBlueprint)
    implements(ISection)

    def __iter__(self):
        for item in self.previous:
            pathkey = self.pathkey(*item.keys())[0]
            roleskey = self.roleskey(*item.keys())[0]

            if not pathkey or not roleskey or \
               roleskey not in item:    # not enough info
                yield item; continue

            obj = self.context.unrestrictedTraverse(item[pathkey].lstrip('/'), None)
            if obj is None:             # path doesn't exist
                yield item; continue

            if IRoleManager.providedBy(obj):
                for principal, roles in item[roleskey].items():
                    if roles:
                        RoleAssignmentManager(obj).add_assignment(
                            SharingRoleAssignment(principal, roles))

            yield item
