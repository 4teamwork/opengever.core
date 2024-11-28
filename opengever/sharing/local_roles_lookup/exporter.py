from datetime import datetime
from opengever.base.browser.reporting_view import BaseReporterView
from opengever.base.reporter import XLSReporter
from opengever.sharing import _
from opengever.sharing.local_roles_lookup.reporter import RoleAssignmentReporter
from plone.app.uuid.utils import uuidToObject


class RoleAssignmentReportExcelDownload(BaseReporterView):

    def __call__(self):
        principal_ids, include_memberships, root = self.extract_query_params()

        report = RoleAssignmentReporter().excel_report_for(
            principal_ids=principal_ids,
            include_memberships=include_memberships,
            root=root)

        items = list(self.prepare_report_for_export(report))
        reporter = XLSReporter(self.request, self.columns(), items)
        return self.return_excel(reporter)

    def extract_query_params(self):
        filters = self.request.get('filters', {})

        principal_ids = filters.get("principal_ids", [])
        include_memberships = filters.get("include_memberships", False)
        root = filters.get("root")

        return principal_ids, include_memberships, root

    @property
    def filename(self):
        principal_ids, include_membership, root = self.extract_query_params()

        parts = [datetime.now().strftime('%Y-%m-%d_%H-%M')]

        if root:
            root = uuidToObject(root)
            parts.append('branch_{}'.format(root.id))

        if include_membership:
            parts.append('including_memberships')

        if principal_ids:
            parts.append('-'.join(principal_ids))

        return u'role_assignment_report_{}.xlsx'.format('_'.join(parts))

    def prepare_report_for_export(self, report):
        for report_item in report:
            item = report_item.get('item')
            principal = report_item.get('principal')
            yield {
                u'title': item.get('title'),
                u'url': item.get('@id'),
                u'portal_type': item.get('@type'),
                u'principal_id': principal.get('principal_id'),
                u'username': principal.get('username'),
                u'groupname': principal.get('groupname'),
                u'role': report_item.get('role'),
            }

    @property
    def _columns(self):
        columns = [
            {
                'id': 'title',
                'title': _('label_title', default=u'Title'),
            },
            {
                'id': 'url',
                'title': _('label_url', default=u'URL'),
                'hyperlink': lambda value, obj: obj.get('url'),
            },
            {
                'id': 'portal_type',
                'title': _('label_portal_type', default=u'Portal type'),
            },
            {
                'id': 'principal_id',
                'title': _('label_principal_id', default=u'Principal id'),
            },
            {
                'id': 'username',
                'title': _('label_user_name', default=u'User name'),
            },
            {
                'id': 'groupname',
                'title': _('label_group_name', default=u'Group name'),
            },
            {
                'id': 'role',
                'title': _('label_role', default=u'Role'),
            }
        ]

        return columns
