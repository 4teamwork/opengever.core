from collections import defaultdict
from ftw.solr.interfaces import ISolrSearch
from ftw.solr.query import make_filters
from opengever.base.solr import batched_solr_results
from opengever.base.solr import OGSolrDocument
from opengever.ogds.models.group import Group
from opengever.ogds.models.user import User
from opengever.sharing.local_roles_lookup.manager import LocalRolesLookupManager
from opengever.sharing.local_roles_lookup.model import LocalRoles
from plone.app.uuid.utils import uuidToObject
from zope.component import getUtility


class RoleAssignmentReporter(object):
    """Responsible for generating role assignment report data.
    """

    field_list = [
        'UID',
        'path',
        'Title',
        'Description',
        'review_state',
        'portal_type',
        'reference',
        'is_leafnode',
    ]

    sort_order = 'path asc'

    def __init__(self):
        self.solr_service = SolrQueryService()
        self.local_roles_manager = LocalRolesLookupManager()

    def __call__(self, *args, **kwargs):
        return self.report_for(*args, **kwargs)

    def report_for(self,
                   principal_ids=[],
                   include_memberships=False,
                   root=None,
                   start=0,
                   rows=25):
        """Generates a report of objects with custom local role assignments.

        The report contains a dictionary with:
        - `items`: A list of objects, each containing:
            - A serialized Solr document representing the object.
            - A dictionary mapping local roles to the list of principals assigned
                to each role.
        - `total_items`: The total number of objects included in the report.

        Example:
            {
                "items": [
                    {
                        "item": {"@id": "..."},
                        "role_assignments": {
                            "role1": ["principal1", "principal2"],
                            "role2": ["principal1"],
                        }
                    }
                ],
                "total_items": 1
            }
        """
        principal_ids = self.expand_principal_ids(principal_ids,
                                                  include_memberships)
        uids = self.get_distinct_uids(principal_ids)

        if not uids:
            return {'total_items': 0, 'items': []}

        filters = self.build_filters(uids, root)
        role_assignments = self.role_assignments_by_uid(uids, principal_ids)

        items, total_items = self.solr_service.search(
            filters, self.field_list, self.sort_order, start, rows)

        items = [{
            'item': self.serialize_solr_doc(item),
            'role_assignments': role_assignments.get(item.get('UID'), {}),
        } for item in items]

        return {'total_items': total_items, 'items': items}

    def excel_report_for(self,
                         principal_ids=[],
                         include_memberships=False,
                         root=None):
        """Generates a report of objects with custom local role assignments optimized
        to export in excel.

        Caution: This function will return unbatched results.

        Example:
            [
                {
                    "item": {"@id": "..."},
                    "role": "Editor",
                    "principal": {
                        "principal_id": "principal-1"
                        "username": "username or empty string",
                        "groupname": "groupname or empty string",
                        }
                }
            ]
        """
        principal_ids = self.expand_principal_ids(principal_ids,
                                                  include_memberships)
        uids = self.get_distinct_uids(principal_ids)

        if not uids:
            return

        filters = self.build_filters(uids, root)
        local_role_entries_by_uid = self.local_role_entries_by_uid(uids, principal_ids)

        solr_items, total_items = self.solr_service.fetch_all(
            filters, self.field_list, self.sort_order)

        for solr_item in solr_items:
            serialized_solr_item = self.serialize_solr_doc(solr_item)
            for local_role_entry in local_role_entries_by_uid.get(solr_item.get('UID'), []):
                local_role_item, username, groupname = local_role_entry
                for role in local_role_item.roles:
                    yield {
                        'item': serialized_solr_item,
                        'role': role,
                        'principal': {
                            'principal_id': local_role_item.principal_id,
                            'username': username,
                            'groupname': groupname,
                        }
                    }

    def serialize_solr_doc(self, doc):
        item = OGSolrDocument(doc)
        serialized_item = {
            '@id': item.getURL(),
            '@type': item.portal_type,
            'UID': item.UID,
            'title': item.Title,
            'description': item.Description,
            'review_state': item.review_state,
            'reference': item.reference,
            'is_leafnode': item.is_leafnode,
        }
        return serialized_item

    def build_filters(self, uids, root):
        """Builds the filters for Solr queries."""
        return (SolrFilterBuilder()
                .with_portal_types(self.local_roles_manager.MANAGED_PORTAL_TYPES)
                .with_uids(uids)
                .with_path(root)
                .build())

    def expand_principal_ids(self, principal_ids, include_memberships=False):
        """Returns a list of principal IDs, including memberships if requested.
        """
        if not principal_ids:
            return set()

        expanded_principal_ids = set(principal_ids)

        if include_memberships:
            for principal_id in principal_ids:
                expanded_principal_ids.update(
                    self.resolve_user_memberships(principal_id))

        return expanded_principal_ids

    def resolve_user_memberships(self, principal_id):
        ogds_user = User.query.filter_by(userid=principal_id).one_or_none()
        if not ogds_user:
            return []
        return [group.groupid for group in ogds_user.groups if group.active]

    def get_distinct_uids(self, principal_ids):
        if principal_ids:
            return self.local_roles_manager.get_distinct_uids_by_principals(principal_ids)
        else:
            return self.local_roles_manager.get_distinct_uids()

    def role_assignments_by_uid(self, uids_filter=None, principal_ids_filter=None):
        """Returns a dict of uids containing local role assignments.

        {
          "uid1": {
            "role1": ["principal_1", "principal_2]
            "role2": ["principal_1"]
          }
        }
        """
        uids = defaultdict(lambda: defaultdict(list))
        for entry in self.local_roles_manager.get_entries(
                uids_filter=uids_filter,
                principal_ids_filter=principal_ids_filter):
            for role in entry.roles:
                uids[entry.object_uid][role].append(entry.principal_id)
        return uids

    def local_role_entries_by_uid(self, uids_filter=None, principal_ids_filter=None):
        """Returns a dict of uids containing a list of local role items and
        principal details:

        {
          "uid1": [
                entry_with_principal_details1,
                entry_with_principal_details2,
            ]
        }
        """
        uids = defaultdict(list)
        for entry in self.get_entries_with_principal_details(
                uids_filter=uids_filter,
                principal_ids_filter=principal_ids_filter):
            uids[entry[0].object_uid].append(entry)

        return uids

    def get_entries_with_principal_details(
            self, uids_filter=None, principal_ids_filter=None):
        query = self.local_roles_manager.get_entries_query(
            uids_filter=uids_filter,
            principal_ids_filter=principal_ids_filter)

        query = query.outerjoin(User, LocalRoles.principal_id == User.userid)
        query = query.outerjoin(Group, LocalRoles.principal_id == Group.groupid)
        query = query.with_entities(LocalRoles, User.username, Group.groupname)
        return query.all()


class SolrFilterBuilder:
    """Builds Solr filters for querying."""

    def __init__(self):
        self.filters = {}

    def with_portal_types(self, portal_types):
        self.filters['portal_type'] = portal_types
        return self

    def with_uids(self, uids):
        if uids:
            self.filters['UID'] = uids
        return self

    def with_path(self, root):
        if root:
            self.filters['path'] = {
                'query': '/'.join(uuidToObject(root).getPhysicalPath()),
                'depth': -1,
            }
        return self

    def build(self):
        return make_filters(**self.filters)


class SolrQueryService:
    def __init__(self):
        self.solr = getUtility(ISolrSearch)

    def search(self, filters, fields, sort, start, rows):
        response = self.solr.search(filters=filters,
                                    fl=fields,
                                    sort=sort,
                                    start=start,
                                    rows=rows)
        return response.docs, response.num_found

    def fetch_all(self, filters, fields, sort):
        items = []
        for batch in batched_solr_results(filters=filters, fl=fields, sort=sort):
            items.extend(batch)
        return items, len(items)
