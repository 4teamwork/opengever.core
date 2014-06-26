from Acquisition import aq_inner
from Acquisition import aq_parent
from five import grok
from opengever.base.browser.helper import get_css_class
from opengever.globalindex.model.task import Task
from opengever.ogds.base.actor import Actor
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.ogds.base.utils import ogds_service
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

    #XXX remove me
    def get_type(self, item):
        """differ the object typ and return the type as string
        """
        if not item:
            return None
        elif isinstance(item, dict):
            return 'dict'
        elif isinstance(item, Task) or ITask.providedBy(item):
            return 'task'
        else:
            return 'obj'

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
            },
            {
                'label': _(u"label_deadline", default=u"Deadline"),
                'value': _format_date(task.get_deadline()),
            },
            {
                'label': _(u"label_issuer", default=u"Issuer"),
                'css_class': "issuer",
                'value': task.get_issuer_label(),
            },
            {
                'label': _(u"label_responsible", default=u"Responsible"),
                'value': task.get_responsible_label(),
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

        #XXX remove this ceck
        if ITask.providedBy(item):
            item = item.get_sql_object()
        if not item:
            return None
        return self._sqlalchemy_task_link(item)

    def _sqlalchemy_task_link(self, item):
        """Renders a indexed task item (globalindex sqlalchemy object) either
        with a link to the effective task (if the user has access) or just with
        the title.
        We have two different types of a task. task-object providing the
        ITask-interface is handled in the _object_task_link.
        """

        css_class = self.get_css_class(item)

        admin_unit = ogds_service().fetch_admin_unit(item.admin_unit_id)
        if not admin_unit:
            return '<span class="%s">%s</span>' % (css_class, item.title)

        # has the user access to the target task?
        has_access = False
        mtool = getToolByName(self.context, 'portal_membership')
        member = mtool.getAuthenticatedMember()

        if member:
            principals = set(member.getGroups() + [member.getId()])
            allowed_principals = set(item.principals)
            has_access = len(principals & allowed_principals) > 0

        # If the target is on a different client we need to make a popup
        if item.admin_unit_id != get_current_admin_unit().id():
            link_target = ' target="_blank"'
            url = '%s/%s' % (admin_unit.public_url, item.physical_path)
        else:
            link_target = ''
            url = admin_unit.public_url + '/' + item.physical_path

        # create breadcrumbs including the (possibly remote) client title
        breadcrumb_titles = "[%s] > %s" % (admin_unit.title, item.breadcrumb_title)

        # Client and user info
        assigned_org_unit = ogds_service().fetch_org_unit(item.assigned_org_unit)
        info_html = ' <span class="discreet">({})</span>'.format(
            assigned_org_unit.prefix_label(
                Actor.lookup(item.responsible).get_label()))

        # Link to the task object
        task_html = '<span class="%s">%s</span>' % \
                        (css_class, item.title)

        # Render the full link if we have acccess
        if has_access:
            inner_html = '<a href="%s"%s title="%s">%s</a> %s' % (
                url,
                link_target,
                breadcrumb_titles,
                task_html,
                info_html)
        else:
            inner_html = '%s %s' % (task_html, info_html)

        # Add the task-state css and return it
        return self._task_state_wrapper(item, inner_html)

    def _task_state_wrapper(self, item, text):
        """ Wrap a span-tag around the text with the status-css class
        """
        return '<span class="wf-%s">%s</span>' % (item.review_state, text)
