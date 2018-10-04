from Acquisition import aq_inner
from Acquisition import aq_parent
from opengever.base.browser.helper import get_css_class
from opengever.globalindex.model.task import Task
from opengever.tabbedview import GeverTabMixin
from opengever.task import _
from opengever.task.task import ITask
from opengever.tasktemplates.interfaces import IFromParallelTasktemplate
from opengever.tasktemplates.interfaces import IFromSequentialTasktemplate
from plone import api
from plone.app.contentlisting.interfaces import IContentListing
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser import BrowserView


class Overview(BrowserView, GeverTabMixin):
    """Provide / override tabbedview methods for task overviews."""

    def documents(self):
        """Return containing documents and related documents."""
        def _get_documents():
            """Return documents in this task and subtasks."""
            documents = getToolByName(self.context, 'portal_catalog')(
                portal_type=['opengever.document.document', 'ftw.mail.mail', ],
                path=dict(
                    depth=2,
                    query='/'.join(self.context.getPhysicalPath())),
                )
            return [document.getObject() for document in documents]

        def _get_related_documents():
            """Return related documents in this task."""
            # Related documents
            related_documents = []

            for item in self.context.relatedItems:
                obj = item.to_object

                if obj.portal_type in [
                        'opengever.document.document',
                        'ftw.mail.mail',
                    ]:
                    obj._v__is_relation = True
                    related_documents.append(obj)

            return related_documents

        # merge and sort the two different lists
        document_list = _get_documents() + _get_related_documents()
        document_list.sort(lambda a, b: cmp(b.modified(), a.modified()))

        return IContentListing(document_list)

    def get_main_attributes(self):
        """Return a list of widgets.

        Should be displayed in the attributes box.
        """
        task = self.context.get_sql_object()

        def _format_date(date):
            if not date:
                return ''

            return api.portal.get().toLocalizedTime(date)

        def _format_description(description):
            if not description:
                return ''

            text = api.portal.get_tool(name='portal_transforms').convertTo(
                'text/html',
                description,
                mimetype='text/x-web-intelligent',
            ).getData()
            return safe_unicode(text)

        items = [
            {
                'label': _('label_task_title', u'Task title'),
                'value': task.title,
                },
            {
                'label': _('label_parent_dossier_title'),
                'value': task.containing_dossier,
                },
            {
                'label': _(u"label_text", default=u"Text"),
                'value': _format_description(task.text),
                'is_html': True,
                },
            {
                'label': _(u'label_task_type', default=u'Task Type'),
                'value': self.context.get_task_type_label(),
                },
            {
                'label': _('label_workflow_state'),
                'value': task.get_state_label(),
                'is_html': True,
                },
            {
                'label': _(u"label_deadline", default=u"Deadline"),
                'value': task.get_deadline_label(fmt="long"),
                'is_html': True,
                },
            {
                'label': _(u"label_reminder", default=u"Reminder"),
                'css_class': "taskReminderSelector",
                'value': self.context.restrictedTraverse('@@task_reminder_selector')(),
                'is_html': True,
                },
            {
                'label': _(u"label_issuer", default=u"Issuer"),
                'css_class': "issuer",
                'value': task.get_issuer_label(),
                'is_html': True,
                },
            {
                'label': _(u"label_responsible", default=u"Responsible"),
                'value': task.get_responsible_label(),
                'is_html': True,
                },
            {
                'label': _(u"label_date_of_completion",
                           default=u"Date of completion"),
                'value': _format_date(task.get_completed()),
                },

            ]

        return items

    def get_css_class(self, item):
        """Return the sprite-css-class for the given object."""
        css = get_css_class(item)
        return '%s %s' % ("rollover-breadcrumb", css)

    def get_sub_tasks(self):
        """Returns all subtasks. On sequential process tasks, it returns
        the subtask in the process order.
        """
        if self.context.is_from_sequential_tasktemplate:
            oguids = self.context.get_tasktemplate_order()
            if not oguids:
                return []

            return [Task.query.by_oguid(oguid) for oguid in oguids]

        tasks = self.context.getFolderContents(
            full_objects=True,
            contentFilter={'portal_type': 'opengever.task.task'},
        )
        return [each.get_sql_object() for each in tasks]

    def get_sequence_type(self):
        if IFromSequentialTasktemplate.providedBy(self.context):
            return u'sequential'
        elif IFromParallelTasktemplate.providedBy(self.context):
            return u'parallel'

    def get_sequence_type_label(self):
        if IFromSequentialTasktemplate.providedBy(self.context):
            return _('label_sequential_process', default=u'Sequential process')
        elif IFromParallelTasktemplate.providedBy(self.context):
            return _('label_parallel_process', default=u'Parallel process')

    def get_containing_task(self):
        """Get the parent-tasks if we have one."""
        parent = aq_parent(aq_inner(self.context))

        if ITask.providedBy(parent):
            return parent.get_sql_object()

        return None

    def get_predecessor_task(self):
        """Get the original task."""
        return self.context.get_sql_object().predecessor

    def get_successor_tasks(self):
        """Get the task from which this task was copied."""
        return self.context.get_sql_object().successors

    def render_task(self, item):
        """Render the taskobject."""
        if not item:
            return None

        return item.get_link(with_responsible_info=False)

    def is_part_of_sequential_process(self):
        return self.context.get_is_subtask() and \
            IFromSequentialTasktemplate.providedBy(self.context)

    def next_task_link(self):
        return self.render_task(self.context.get_sql_object().get_next_task())

    def previous_task_link(self):
        return self.render_task(self.context.get_sql_object().get_previous_task())
