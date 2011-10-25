from five import grok
from Products.CMFPlone.interfaces import IPloneSiteRoot
from opengever.globalindex import _
from Products.statusmessages.interfaces import IStatusMessage
from opengever.globalindex.interfaces import ITaskQuery
from zope.component import getUtility
from opengever.base.reporter import format_datetime, get_date_style
from opengever.base.reporter import readable_author
from opengever.base.reporter import StringTranslater, XLSReporter


class TaskReporter(grok.View):
    """View that generate an excel spreadsheet which list all selected
    task and their important attributes from the globalindex.
    """

    grok.context(IPloneSiteRoot)
    grok.name('task_report')
    grok.require('zope2.View')

    def render(self):

        if not self.request.get('task_ids'):
            msg = _(
                u'error_no_items', default=u'You have not selected any Items')
            IStatusMessage(self.request).addStatusMessage(msg, type='error')
            return self.request.RESPONSE.redirect(
                self.request.form['orig_template'])

        ids = self.request.get('task_ids', [])

        query = getUtility(ITaskQuery)
        tasks = query.get_tasks(ids)

        task_attributes = [
            {'id':'title', 'title':_('label_title')},
            {'id':'review_state', 'title':_('review_state'),
             'transform':StringTranslater(
                self.context.REQUEST, 'plone').translate},
            {'id':'deadline', 'title':_('label_deadline'),
             'transform':format_datetime, 'style':get_date_style()},
            {'id':'completed', 'title':_('label_completed'),
             'transform':format_datetime, 'style':get_date_style()},
            {'id':'created', 'title':_('label_created'),
             'transform':format_datetime, 'style':get_date_style()},
            {'id':'responsible', 'title':_('label_responsible'),
             'transform':readable_author},
            {'id':'issuer', 'title':_('label_issuer'),
             'transform':readable_author},
            {'id':'task_type', 'title':_('label_task_type')},
            {'id':'sequence_number', 'title':_('label_sequence_number')},
            {'id':'client_id', 'title':_('label_client_id')},
        ]

        reporter = XLSReporter(self.context.REQUEST, task_attributes, tasks)

        data = reporter()
        if not data:
            msg = _(u'Could not generate the report')
            IStatusMessage(self.request).addStatusMessage(
                msg, type='error')
            return self.request.RESPONSE.redirect(self.context.absolute_url())

        response = self.request.RESPONSE

        response.setHeader('Content-Type', 'application/vnd.ms-excel')
        response.setHeader('Content-Disposition',
                           'attachment;filename="task_report.xls"')
        return data
