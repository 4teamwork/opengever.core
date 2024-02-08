from opengever.base import _
from opengever.base.behaviors.translated_title import ITranslatedTitle
from opengever.base.behaviors.translated_title import ITranslatedTitleSupport
from opengever.base.browser.reporting_view import BaseReporterView
from opengever.base.interfaces import IReferenceNumber
from opengever.base.interfaces import IRoleAssignmentReportsStorage
from opengever.base.reporter import XLSReporter
from opengever.sharing.browser.sharing import ROLE_MAPPING
from plone import api
from plone.app.uuid.utils import uuidToObject
from zExceptions import BadRequest
from zExceptions import NotFound
from zope.i18n import translate
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse


class RoleAssignmentReportExcelDownload(BaseReporterView):

    implements(IPublishTraverse)

    def __init__(self, context, request):
        super(RoleAssignmentReportExcelDownload, self).__init__(context, request)
        self.types_tool = api.portal.get_tool('portal_types')
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
        reporter = XLSReporter(
            self.request,
            self.columns(),
            items,
            sheet_title=report['principal_id'],
        )
        return self.return_excel(reporter)

    @property
    def filename(self):
        return u'{}.xlsx'.format(self.report_id)

    def prepare_report_for_export(self, report):
        for item in report.get('items'):
            obj = uuidToObject(item.get('UID'))
            data = {
                u'reference': self.get_reference_number(obj),
                u'type': self.get_type_title(obj),
                u'title': self.get_title(obj),
                u'url': obj.absolute_url(),
            }

            for role in self.available_roles():
                data[role] = bool(role in item['roles'])

            yield data

    def available_roles(self):
        return ROLE_MAPPING.keys()

    def get_title(self, obj):
        title = obj.title
        if ITranslatedTitleSupport.providedBy(obj):
            title = ITranslatedTitle(obj).translated_title()
        return title

    def get_type_title(self, obj):
        type_title = obj.portal_type
        fti = self.types_tool.get(obj.portal_type)
        if fti:
            type_title = translate(
                fti.title,
                domain=fti.i18n_domain,
                context=self.request
            )
        return type_title

    def get_reference_number(self, obj):
        refnum = IReferenceNumber(obj)
        if not refnum:
            return u''
        return refnum.get_number()

    @property
    def _columns(self):
        columns = [{
            'id': 'reference',
            'title': _('label_reference', default=u'Reference'),
        }, {
            'id': 'type',
            'title': _('label_type', default=u'Type'),
        }, {
            'id': 'title',
            'title': _('label_title', default=u'Title'),
            'hyperlink': lambda value, obj: obj.get('url'),
        }
        ]

        for role_id, role_title in ROLE_MAPPING.items():
            columns.append({'id': role_id, 'title': role_title,
                            'transform': lambda value: 'x' if value else ''})

        return columns
