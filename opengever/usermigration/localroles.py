from opengever.base.role_assignments import RoleAssignmentManager
from zope.annotation.interfaces import IAnnotatable


def migrate_localroles(context, mapping, mode='move', replace=False):
    """Recursively migrate local roles on the given context.

    This method customizes  ftw.usermigration.localroles.migrate_localroles by
    changing the way the local roles are updated. Instead of using the
    manage_<set|del>LocalRoles method we use the corresponding methods from the
    RoleAssignmentManager.
    """

    # Statistics
    moved = []
    copied = []
    deleted = []

    # Paths needing reindexing of security
    reindex_paths = set()

    if replace:
        raise NotImplementedError(
            "Local roles migration only supports 'replace=False' as of yet")

    if mode not in ('move', 'copy', 'delete'):
        raise

    def is_reindexing_ancestor(path):
        """Determine if an ancestor of the given path is already in
           reindex_paths."""
        path_parts = path.split('/')
        for i, part in enumerate(path_parts):
            subpath = '/'.join(path_parts[:i + 1])
            if subpath in reindex_paths:
                return True
        return False

    def migrate_and_recurse(context):
        """This function is based on ftw.usermigration but customized for
        GEVER as follows:

        - It does not recurse into and handle objects that do not support
          IAnnotations. IAnnotations are needed by the RoleAssignmentManager.
          This is mostly an issue when starting at plone-site level and iterate
          some portal_<name> objects via objectValues.
        - It uses RoleAssignmentManager instead of the manage_<op>LocalRoles
          methods to modify local roles as we must do so in GEVER.
        """
        if not IAnnotatable.providedBy(context):
            return

        manager = RoleAssignmentManager(context)
        path = '/'.join(context.getPhysicalPath())

        for old_id, new_id in mapping.items():
            assignments = manager.get_assignments_by_principal_id(old_id)
            if not assignments:
                continue

            for old_assignment in assignments:
                if mode in ['move', 'copy']:
                    manager.add_or_update(
                        new_id,
                        old_assignment.roles,
                        old_assignment.cause,
                        old_assignment.reference,
                        reindex=False)
                    if not is_reindexing_ancestor(path):
                        reindex_paths.add(path)
                if mode in ['move', 'delete']:
                    # Even though the kw argument is named `userids`,
                    # these are in fact principal IDs (groups or users)
                    manager.clear(
                        old_assignment.cause,
                        old_assignment.principal,
                        old_assignment.reference,
                        reindex=False)
                    if not is_reindexing_ancestor(path):
                        reindex_paths.add(path)
            if mode == 'move':
                moved.append((path, old_id, new_id))
            elif mode == 'copy':
                copied.append((path, old_id, new_id))
            elif mode == 'delete':
                deleted.append((path, old_id, None))

        for obj in context.objectValues():
            migrate_and_recurse(obj)

    migrate_and_recurse(context)

    for path in reindex_paths:
        obj = context.unrestrictedTraverse(path)
        obj.reindexObjectSecurity()

    return(dict(moved=moved, copied=copied, deleted=deleted))
