from opengever.base import _
from opengever.base.browser.reporting_view import BaseReporterView
from opengever.base.interfaces import IRoleAssignmentReportsStorage
from opengever.base.reporter import XLSReporter
from opengever.sharing.browser.sharing import GEVER_ROLE_MAPPING
from opengever.sharing.browser.sharing import WORKSPACE_ROLE_MAPPING
from opengever.workspace import is_workspace_feature_enabled
from plone.app.uuid.utils import uuidToObject
from zExceptions import BadRequest
from zExceptions import NotFound
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse


class RoleAssignmentReportExcelDownload(BaseReporterView):

    implements(IPublishTraverse)

    def __init__(self, context, request):
        super(RoleAssignmentReportExcelDownload, self).__init__(context, request)
        self.params = []

    def publishTraverse(self, request, name):
        self.params.append(name)
        return self

    def __call__(self):
        storage = IRoleAssignmentReportsStorage(self.context)

        # Expects report_id as path parameter
        if not len(self.params) == 1:
            raise NotFound()

        self.report_id = self.params[0]
        try:
            report = storage.get(self.report_id)
        except KeyError:
            raise BadRequest(u"Invalid report_id '{}'".format(self.report_id))

        items = list(self.prepare_report_for_export(report))
        reporter = XLSReporter(self.request, self.columns(), items)
        return self.return_excel(reporter)

    @property
    def filename(self):
        return u'{}.xlsx'.format(self.report_id)

    def prepare_report_for_export(self, report):
        for item in report.get('items'):
            obj = uuidToObject(item.get('UID'))
            data = {u'title': obj.Title(), u'url': obj.absolute_url()}

            for role in self.available_roles():
                data[role] = bool(role in item['roles'])

            yield data

    def available_roles(self):
        return WORKSPACE_ROLE_MAPPING.keys() if is_workspace_feature_enabled() else GEVER_ROLE_MAPPING.keys()

    @property
    def _columns(self):
        columns = [{'id': 'title',
                    'title': _('label_title', default=u'Title'),
                    'hyperlink': lambda value, obj: obj.get('url')}]

        role_mapping = WORKSPACE_ROLE_MAPPING if is_workspace_feature_enabled() else GEVER_ROLE_MAPPING

        for role_id, role_title in role_mapping.items():
            columns.append({'id': role_id, 'title': role_title,
                            'transform': lambda value: 'x' if value else ''})

        return columns
