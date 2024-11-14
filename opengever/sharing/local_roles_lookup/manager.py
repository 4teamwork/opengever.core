from opengever.base.model import create_session
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.sharing.local_roles_lookup.model import LocalRoles


class LocalRolesLookupManager(object):
    """Responsible for tracking principals on objects which have a any of the
    whitelisted local roles on the given context.
    """

    MANAGED_ROLES = ('Reader',
                     'Contributor',
                     'Editor',
                     'Reviewer',
                     'Publisher',
                     'DossierManager',
                     'TaskResponsible',
                     'Role Manager',
                     'WorkspaceGuest',
                     'WorkspaceMember',
                     'WorkspaceAdmin',
                     )

    MANAGED_PORTAL_TYPES = (
        'opengever.dossier.businesscasedossier',
        'opengever.repository.repositoryfolder',
        'opengever.repository.repositoryroot',
        'opengever.workspace.folder',
        'opengever.workspace.workspace',
    )

    def __init__(self):
        self.model_cls = LocalRoles

    @property
    def local_unit_id(self):
        return get_current_admin_unit().unit_id

    def add(self, principal_id, uid, roles):
        """Adds a new modification entry for the given principal_id and object_uid
        if it does not exist yet.

        Will be skipped, if there is already such an entry.
        """
        if self.has_entry_for(principal_id, uid):
            return False

        item = self.model_cls(
            admin_unit_id=self.local_unit_id,
            principal_id=principal_id,
            object_uid=uid,
            roles=roles,
        )

        session = create_session()
        session.add(item)
        return True

    def delete_all_by_uid(self, uid):
        return self.get_by_uid_query(uid).delete()

    def update_lookup_table(self, context):
        """Checks the local roles of the given context and adds or removes
        principals to the lookup table if necessary.
        """
        if context.portal_type not in self.MANAGED_PORTAL_TYPES:
            return

        self.delete_all_by_uid(context.UID())

        for principal, roles in context.get_local_roles():
            managed_roles = list(set(roles).intersection(self.MANAGED_ROLES))
            if not managed_roles:
                continue

            self.add(principal, context.UID(), managed_roles)

    def has_entry_for(self, principal_id, uid):
        filters = {
            'uids_filter': [uid] if uid else None,
            'principal_ids_filter': [principal_id] if principal_id else None
        }
        return bool(self.get_entries_query(**filters).one_or_none())

    def get_by_principals_query(self, principal_ids):
        return self.model_cls.query.filter_by(
            admin_unit_id=self.local_unit_id).filter(
                self.model_cls.principal_id.in_(principal_ids))

    def get_distinct_uids_by_principals(self, principal_ids):
        query = self.get_by_principals_query(principal_ids)
        query = query.with_entities(self.model_cls.object_uid).distinct()
        return [item[0] for item in query]

    def get_distinct_uids(self):
        query = self.model_cls.query.filter_by(admin_unit_id=self.local_unit_id)
        query = query.with_entities(self.model_cls.object_uid).distinct()
        return [item[0] for item in query]

    def get_by_uid_query(self, uid):
        return self.model_cls.query.filter_by(
            admin_unit_id=self.local_unit_id,
            object_uid=uid)

    def get_distinct_principal_ids_by_uid(self, uid):
        query = self.get_by_uid_query(uid)
        query = query.with_entities(self.model_cls.principal_id).distinct()
        return [item[0] for item in query]

    def get_entries_query(self, uids_filter=None, principal_ids_filter=None):
        query = self.model_cls.query.filter_by(admin_unit_id=self.local_unit_id)

        if uids_filter:
            query = query.filter(
                self.model_cls.object_uid.in_(uids_filter))

        if principal_ids_filter:
            query = query.filter(
                self.model_cls.principal_id.in_(principal_ids_filter))

        return query

    def get_entries(self, *args, **kwargs):
        return self.get_entries_query(*args, **kwargs).all()
