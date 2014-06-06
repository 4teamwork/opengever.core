from Acquisition import aq_inner
from Acquisition import aq_parent
from five import grok
from opengever.base.browser.helper import client_title_helper
from opengever.base.browser.helper import get_css_class
from opengever.globalindex.model.task import Task
from opengever.ogds.base.interfaces import IContactInformation
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.ogds.base.utils import ogds_service
from opengever.tabbedview.browser.tabs import OpengeverTab
from opengever.tabbedview.helper import _breadcrumbs_from_item
from opengever.task import _
from opengever.task.interfaces import ISuccessorTaskController
from opengever.task.task import ITask
from plone.directives.dexterity import DisplayForm
from Products.CMFCore.utils import getToolByName
from z3c.form.field import Field
from z3c.form.interfaces import DISPLAY_MODE, IFieldWidget
from z3c.form.interfaces import IContextAware, IField
from zope.component import getUtility, getMultiAdapter
from zope.component import queryAdapter
from zope.component import queryUtility
from zope.i18n import translate
from zope.interface import alsoProvides


def get_field_widget(obj, field):
    """Returns the field widget of a field in display mode without
    touching any form.
    The `field` should be a z3c form field, not a zope schema field.

    copied from collective.dexteritytextindexer
    """
    assert IField.providedBy(field), 'field is not a form field'

    if field.widgetFactory.get(DISPLAY_MODE) is not None:
        factory = field.widgetFactory.get(DISPLAY_MODE)
        widget = factory(field.field, obj.REQUEST)
    else:
        widget = getMultiAdapter(
            (field.field, obj.REQUEST), IFieldWidget)
    widget.name = '' + field.__name__  # prefix not needed
    widget.id = widget.name.replace('.', '-')
    widget.context = obj
    alsoProvides(widget, IContextAware)
    widget.mode = DISPLAY_MODE
    widget.ignoreRequest = True
    widget.update()
    return widget


class Overview(DisplayForm, OpengeverTab):
    grok.context(ITask)
    grok.name('tabbedview_view-overview')
    grok.template('overview')

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

    def boxes(self):
        """ Return the boxes in the overview splittet in two columns
        """
        items = [
            [dict(id='main_attributes',
                  label=_(u'label_main_attributes', default="Main Atrributes"),
                  content=self.get_main_attributes()),
             dict(id='documents',
                  label=_(u'label_documents', default="Documents"),
                  content=self.documents()),
            ],
            [dict(id='containing_task',
                  label=_(u'label_containing_task',
                          default="Containing tasks"),
                  content=self.get_containing_task()),
             dict(id='sub_task',
                  label=_(u'label_sub_task', default="Sub tasks"),
                  content=self.get_sub_tasks()),
             dict(id='predecessor_task',
                  label=_(u'label_predecessor_task',
                          default="Predecessor task"),
                  content=self.get_predecessor_task()),
             dict(id='successor_tasks',
                  label=_(u'label_successor_task', default="Successor task"),
                  content=self.get_successor_tasks()),
            ],
            ]
        return items

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

        def _get_state():
            state = getToolByName(self.context, 'portal_workflow').getInfoFor(
                self.context, 'review_state')

            return "<span class=wf-%s>%s</span>" % (
                state,
                translate(state, domain='plone', context=self.request),
            )

        def _get_parent_dossier_title():
            finder = queryAdapter(self.context, name='parent-dossier-finder')
            if not finder:
                return

            dossier = finder.find_dossier()
            if not dossier:
                return None

            return dossier.Title()

        def _get_issuer():
            info = getUtility(IContactInformation)
            task = ITask(self.context)

            if not ogds_service().has_multiple_org_units():
                return info.render_link(task.issuer)

            sql_task = self.context.get_sql_object()
            issuing_org_unit = sql_task.issuing_org_unit
            predecessors = self.get_predecessor_task()

            if predecessors and \
                predecessors[0].task_type != 'forwarding_task_type':
                issuing_org_unit = predecessors[0].issuing_org_unit

            issuing_org_unit = ogds_service().fetch_org_unit(issuing_org_unit)

            return issuing_org_unit.label() + ' / ' + info.render_link(task.issuer)

        def _get_task_widget_value(attr):
            field = ITask.get(attr)
            field = Field(field, interface=field.interface, prefix='')
            return get_field_widget(self.context, field).render()

        items = [
            {
                'label': _('label_task_title'),
                'value': _get_task_widget_value('title'),
            },
            {
                'label': _('label_parent_dossier_title'),
                'value': _get_parent_dossier_title(),
            },
            {
                'label': _(u"label_text", default=u"Text"),
                'value': _get_task_widget_value('text'),
            },
            {
                'label': _(u'label_task_type', default=u'Task Type'),
                'value': _get_task_widget_value('task_type'),
            },
            {
                'label': _('label_workflow_state'),
                'value': _get_state(),
            },
            {
                'label': _(u"label_deadline", default=u"Deadline"),
                'value': _get_task_widget_value('deadline'),
            },
            {
                'label': _(u"label_issuer", default=u"Issuer"),
                'css_class': "issuer",
                'value': _get_issuer(),
            },
            {
                'label': _(u"label_responsible", default=u"Responsible"),
                'value': self.get_task_info(self.context),
            },
            {
                'label': _(u"label_date_of_completion",
                           default=u"Date of completion"),
                'value': _get_task_widget_value('date_of_completion'),
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
        return tasks

    def get_containing_task(self):
        """ Get the parent-tasks if we have one
        """
        parent = aq_parent(aq_inner(self.context))
        if ITask.providedBy(parent):
            return [parent]
        return []

    def get_predecessor_task(self):
        """ Get the original task
        """
        controller = ISuccessorTaskController(self.context)
        task = controller.get_predecessor()
        # box rendering need a list
        if not task:
            return []
        return [task]

    def get_successor_tasks(self):
        """ Get the task from which this task was copied
        """
        controller = ISuccessorTaskController(self.context)
        return controller.get_successors()

    def get_task_info(self, item):
        """ return some task attributes for objects:
            Responsible client ID /  responsible
        """
        if not ITask.providedBy(item):
            return ''

        info = getUtility(IContactInformation)

        if not item.responsible_client or len(info.get_clients()) <= 1:
            # No responsible client is set yet or we have a single client
            # setup.
            return info.describe(item.responsible)

        # Client
        client = client_title_helper(item, item.responsible_client)

        taskinfo = "%s / %s" % (
            client,
            info.render_link(item.responsible),
        )

        return taskinfo.encode('utf-8')

    def render_task(self, item):
        """ Render the taskobject
        """
        if isinstance(item, Task):
            # Its a task stored in sql
            return self._sqlalchemy_task_link(item)

        elif ITask.providedBy(item):
            # Its a normal task object
            return self._object_task_link(item)

        else:
            return None

    def _object_task_link(self, item):
        """ Renders a task object with a link to the effective task
        We have two different types of a task. task-object from the sql-db is
        handled in the _sqlalchemy_task_link-method.
        """
        breadcrumb_titles = "[%s] > %s" % (
            client_title_helper(item, item.responsible_client).encode('utf-8'),
            ' > '.join(_breadcrumbs_from_item(item)))

        info_html = self.get_task_info(item)
        task_html = \
            '<a href="%s" title="%s"><span class="%s">%s</span></a>' % (
                item.absolute_url(),
                breadcrumb_titles,
                self.get_css_class(item),
                item.Title(),
            )
        inner_html = '%s <span class="discreet">(%s)</span>' % (
            task_html, info_html)

        return self._task_state_wrapper(item, inner_html)

    def _sqlalchemy_task_link(self, item):
        """Renders a indexed task item (globalindex sqlalchemy object) either
        with a link to the effective task (if the user has access) or just with
        the title.
        We have two different types of a task. task-object providing the
        ITask-interface is handled in the _object_task_link.
        """

        css_class = self.get_css_class(item)

        info = queryUtility(IContactInformation)
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
        info_html = ' <span class="discreet">(%s / %s)</span>' % (
            assigned_org_unit.label(),
            info.render_link(item.responsible),
        )

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
        if isinstance(item, Task):
            # Its a sql-task-object
            state = item.review_state
        elif ITask.providedBy(item):
            # Its a task-object
            state = getToolByName(self.context, 'portal_workflow').getInfoFor(
                item, 'review_state')
        else:
            return ''
        return '<span class="wf-%s">%s</span>' % (state, text)
