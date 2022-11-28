from datetime import datetime
from opengever.base.browser.reporting_view import BaseReporterView
from opengever.base.reporter import DATE_NUMBER_FORMAT
from opengever.base.reporter import readable_actor
from opengever.base.reporter import StringTranslater
from opengever.base.reporter import XLSReporter
from opengever.globalindex import _
from opengever.globalindex.utils import get_selected_items
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.task.helper import task_type_value_helper
from Products.statusmessages.interfaces import IStatusMessage
from zope.i18n import translate


def get_link(value, task):
    return task.absolute_url()


class TaskReporter(BaseReporterView):
    """View that generate an excel spreadsheet which list all selected
    task and their important attributes from the globalindex.
    """

    filename = 'task_report.xlsx'

    @property
    def _columns(self):
        return [
            {'id': 'title', 'title': _('label_title'), 'hyperlink': get_link},
            {'id': 'review_state', 'title': _('review_state'),
             'transform': StringTranslater(
                 self.context.REQUEST, 'plone').translate},
            {'id': 'deadline', 'title': _('label_deadline'),
             'number_format': DATE_NUMBER_FORMAT},
            {'id': 'completed', 'title': _('label_completed'),
             'number_format': DATE_NUMBER_FORMAT},
            {'id': 'containing_dossier', 'title': _('label_dossier')},
            {'id': 'get_main_task_title', 'callable': True,
             'title': _('label_main_task', default=u'Main task')},
            {'id': 'issuer', 'title': _('label_issuer'),
             'transform': readable_actor},
            {'id': 'issuing_org_unit_label',
             'title': _('label_issuing_org_unit')},
            {'id': 'responsible', 'title': _('label_responsible'),
             'transform': readable_actor},
            {'id': 'task_type', 'title': _('label_task_type'),
             'transform': task_type_value_helper},
            {'id': 'admin_unit_id', 'title': _('label_admin_unit_id')},
            {'id': 'sequence_number', 'title': _('label_sequence_number')},
            {'id': 'text', 'title': _('label_description', default=u'Description')},
        ]

    def __call__(self):
        tasks = get_selected_items(self.context, self.request)
        tasks = [tt for tt in tasks]

        if not tasks:
            msg = _(
                u'error_no_items', default=u'You have not selected any items.')
            IStatusMessage(self.request).addStatusMessage(msg, type='error')
            if self.request.get('orig_template'):
                return self.request.RESPONSE.redirect(
                    self.request.form['orig_template'])
            else:
                return self.request.RESPONSE.redirect(
                    self.context.absolute_url())

        reporter = XLSReporter(
            self.context.REQUEST,
            self.columns(),
            tasks,
            sheet_title=translate(
                _('label_tasks', default=u'Tasks'), context=self.request),
            footer='%s %s' % (
                datetime.now().strftime('%d.%m.%Y %H:%M'),
                get_current_admin_unit().id())
        )

        return self.return_excel(reporter)
