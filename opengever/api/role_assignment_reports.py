from opengever.base.utils import safe_int
from opengever.sharing.browser.sharing import GEVER_ROLE_MAPPING
from opengever.sharing.browser.sharing import WORKSPACE_ROLE_MAPPING
from opengever.sharing.local_roles_lookup.reporter import RoleAssignmentReporter
from opengever.workspace import is_workspace_feature_enabled
from plone.restapi.batching import HypermediaBatch
from plone.restapi.services import Service
from Products.ZCatalog.Lazy import LazyMap
from zope.i18n import translate


class RoleAssignmentReportGet(Service):

    def reply(self):
        filters = self.request.get('filters', {})

        principal_ids = self.resolve_principals(filters.get("principal_ids", []))
        include_memberships = filters.get("include_memberships", False)
        root = filters.get("root")
        b_start = safe_int(self.request.form.get("b_start", 0))
        b_size = safe_int(self.request.form.get("b_size", 25))

        response = {}

        report = RoleAssignmentReporter()(
            principal_ids,
            include_memberships,
            root,
            start=b_start,
            rows=b_size
        )
        response['referenced_roles'] = self.get_referenced_roles()

        # We use the HypermediaBatch only to generate the links,
        # we therefore do not need the real sequence of objects here
        items = LazyMap(None, [], actual_result_count=report.get("total_items"))
        batch = HypermediaBatch(self.request, items)

        report_items = []

        for report_item in report.get("items"):
            item = report_item.get("item")
            role_assignment = report_item.get("role_assignments")
            for role in response['referenced_roles']:
                item["role_{}".format(role.get("id"))] = role_assignment.get(
                    role.get("id"), []
                )
            report_items.append(item)

        response['items'] = report_items
        response['items_total'] = batch.items_total
        response['@id'] = batch.canonical_url
        if batch.links:
            response['batching'] = batch.links

        return response

    def get_referenced_roles(self):
        roles = []
        role_mapping = WORKSPACE_ROLE_MAPPING if is_workspace_feature_enabled() else GEVER_ROLE_MAPPING
        for role, title in role_mapping.items():
            roles.append(
                {'id': role,
                 'title': translate(title, context=self.request)})

        return roles

    def resolve_principals(self, principal_ids):
        return [principal_id.split(':')[-1] for principal_id in principal_ids]
