from Acquisition import aq_inner
from Acquisition import aq_parent
from five import grok
from opengever.base.browser.helper import get_css_class
from opengever.tabbedview.browser.base import OpengeverTab
from opengever.task import _
from opengever.task.task import ITask
from plone import api
from plone.directives.dexterity import DisplayForm
from Products.CMFCore.utils import getToolByName


class Overview(DisplayForm, OpengeverTab):
    grok.context(ITask)
    grok.name('tabbedview_view-overview')
    grok.template('overview')

    def documents(self):
        """ Return containing documents and related documents
        """

        def _get_documents():
            """ Return documents in this task and subtasks
            """
            documents = getToolByName(self.context, 'portal_catalog')(
                portal_type=['opengever.document.document', 'ftw.mail.mail', ],
                path=dict(
                    depth=2,
                    query='/'.join(self.context.getPhysicalPath())),
                )
            return [document.getObject() for document in documents]

        def _get_related_documents():
            """ Return related documents in this task
            """
            # Related documents
            related_documents = []
            for item in self.context.relatedItems:
                obj = item.to_object
                if obj.portal_type in [
                        'opengever.document.document', 'ftw.mail.mail']:
                    obj._v__is_relation = True
                    related_documents.append(obj)
            return related_documents

        # merge and sort the two different lists
        document_list = _get_documents() + _get_related_documents()
        document_list.sort(lambda a, b: cmp(b.modified(), a.modified()))

        return document_list

    def get_main_attributes(self):
        """ return a list of widgets,
        which should be displayed in the attributes box
        """

        task = self.context.get_sql_object()

        def _format_date(date):
            if not date:
                return ''
            return api.portal.get().toLocalizedTime(task.get_deadline())

        items = [
            {
                'label': _('label_task_title'),
                'value': task.title,
            },
            {
                'label': _('label_parent_dossier_title'),
                'value': task.containing_dossier,
            },
            {
                'label': _(u"label_text", default=u"Text"),
                'value': task.text,
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
                'value': task.get_deadline_label(),
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
        """Return the sprite-css-class for the given object.
        """
        css = get_css_class(item)
        return '%s %s' % ("rollover-breadcrumb", css)

    def get_sub_tasks(self):
        """ Return the subtasks
        """
        tasks = self.context.getFolderContents(
            full_objects=True,
            contentFilter={'portal_type': 'opengever.task.task'},
            )
        return [each.get_sql_object() for each in tasks]

    def get_containing_task(self):
        """ Get the parent-tasks if we have one
        """
        parent = aq_parent(aq_inner(self.context))
        if ITask.providedBy(parent):
            return parent.get_sql_object()
        return None

    def get_predecessor_task(self):
        """ Get the original task
        """
        return self.context.get_sql_object().predecessor

    def get_successor_tasks(self):
        """ Get the task from which this task was copied
        """
        return self.context.get_sql_object().successors

    def render_task(self, item):
        """ Render the taskobject."""

        if not item:
            return None

        return item.get_link()
