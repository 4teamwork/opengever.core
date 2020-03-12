from AccessControl import Unauthorized
from Acquisition import aq_inner
from Acquisition import aq_parent
from datetime import datetime, timedelta, date
from ftw.table import helper
from ftw.table.interfaces import ITableGenerator
from opengever.dossier.behaviors.dossier import IDossierMarker, IDossier
from opengever.ogds.base.utils import get_current_org_unit
from opengever.ogds.models.service import ogds_service
from opengever.task.activities import TaskAddedActivity
from opengever.task.interfaces import ITaskSettings
from opengever.tasktemplates import _
from opengever.tasktemplates import INTERACTIVE_USERS
from opengever.tasktemplates.interfaces import IFromTasktemplateGenerated
from plone import api
from plone.dexterity.utils import createContent, addContentToContainer
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from Products.CMFPlone.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from zope.component import queryUtility
from zope.event import notify
from zope.interface import alsoProvides
from zope.lifecycleevent import ObjectCreatedEvent


meta_data = {}
meta_data['templates'] = {
    'root': 'rows',
    'totalProperty': 'totalCount',

    'fields': [
        {'name': 'path_radiobutton', 'type': 'string', 'hideable': False},
        {'name': 'created', 'type': 'string'},
        {'name': 'Title', 'type': 'string'}
        ],

    'columns': [
        {'id': 'path_radiobutton',
         'width': 30,
         'menuDisabled': True,
         'sortable': False,
         'dataIndex': 'path_radiobutton',
         'hideable': False},

        {'id': 'Title',
         'header': 'Title',
         'sortable': True,
         'dataIndex': 'Title'},

        {'id': 'created',
         'header': 'Created',
         'width': 160,
         'sortable': True,
         'dataIndex': 'created'}
        ],
    }

meta_data['tasks'] = {
    'root': 'rows',
    'totalProperty': 'totalCount',

    'fields': [
        {'name': 'path_checkbox', 'type': 'string'},
        {'name': 'created', 'type': 'string'},
        {'name': 'Title', 'type': 'string'}
        ],

    'columns': [
        {'id': 'path_checkbox',
         'header': '',
         'width': 30,
         'sortable': False,
         'hideable': False,
         'menuDisabled': True,
         'dataIndex': 'path_checkbox'},

        {'id': 'Title',
         'header': 'Title',
         'sortable': True,
         'dataIndex': 'Title'},

        {'id': 'created',
         'header': 'Created',
         'width': 160,
         'sortable': True,
         'dataIndex': 'created'}
        ],
    }


def path_checkbox(item, value):
    preselected = item.getObject().preselected
    return """
            <input type="checkbox"
                    class="noborder selectable"
                    name="paths:list"
                    id="%s" value="%s"
                    alt="Select %s"
                    title="Select %s"
                    %s
                    >""" % (item.id,
                            item.getPath(),
                            item.Title,
                            item.Title,
                            preselected and 'checked="checked"' or None
                            )


class AddForm(BrowserView):

    template = ViewPageTemplateFile("form.pt")

    steps = {
        'templates': {
            'columns': (
                ('', helper.path_radiobutton),
                {'column': 'Title',
                 'column_title': _(u'label_title', default=u'Title')},
                {'column': 'created',
                 'column_title': _(u'label_created', default=u'Created'),
                 'transform': helper.readable_date},),
            'types': ('TaskTemplateFolder',),
            'states': ('tasktemplatefolder-state-activ',),
            },

        'tasks': {
            'columns': (
                ('', path_checkbox),
                {'column': 'Title',
                 'column_title': _(u'label_title', default=u'Title')},
                {'column': 'created',
                 'column_title': _(u'label_created', default=u'Created'),
                 'transform': helper.readable_date},),
            'types': ('TaskTemplate',),
            'states': ('tasktemplate-state-active',),

            }
        }

    def __call__(self):
        if not self.has_active_tasktemplatefolders():
            api.portal.show_message(
                _(u'msg_no_active_tasktemplatefolders',
                  default=u'Currently there are no active '
                  'task template folders registered.'),
                request=self.request,
                type='error')
            return self.request.RESPONSE.redirect(self.context.absolute_url())

        return self.template()

    def has_active_tasktemplatefolders(self):
        catalog = api.portal.get_tool('portal_catalog')
        brains = catalog(
            review_state=('tasktemplatefolder-state-activ'),
            portal_type='opengever.tasktemplates.tasktemplatefolder')

        return bool(brains)

    def listing(self, show='templates', path='/'):
        """returns a listing of either TaskTemplateFolders or TaskTemplates"""

        sort_on = self.request.get('sort', 'getObjPositionInParent')
        sort_on = {'Title': 'sortable_title'}.get(sort_on, sort_on)
        sort_order = self.request.get('dir', 'ASC')
        sort_order = {'ASC': 'asc',
                      'DESC': 'reverse'}.get(sort_order, sort_order)
        templates = self.context.portal_catalog(
            Type=self.steps[show]['types'],
            review_state=self.steps[show]['states'],
            sort_on=sort_on,
            sort_order=sort_order,
            path=path
            )

        table_options = {'auto_expand_column': 'Title'}
        generator = queryUtility(ITableGenerator, 'ftw.tablegenerator')
        return generator.generate(templates,
                                  self.steps[show]['columns'],
                                  sortable=True,
                                  selected=(sort_on, sort_order),
                                  options=table_options,
                                  output='json'
                                  )

    def load_request_parameters(self):
        """Load parameters such as page or filter from request.
        """
        # pagenumber
        self.batching_current_page = int(self.request.get('pagenumber', 1))
        # XXX eliminate self.pagenumber
        self.pagenumber = self.batching_current_page

        # pagesize
        self.batching_pagesize = self.pagesize

        # set url
        self.url = self.context.absolute_url()

        # filtering
        if 'searchable_text' in self.request:
            self.filter_text = self.request.get('searchable_text')
        # ordering
        self.sort_on = self.request.get('sort', self.sort_on)
        if self.sort_on.startswith('header-'):
            self.sort_on = self.sort_on.split('header-')[1]

        # reverse
        default_sort_order = self.sort_reverse and 'reverse' or 'asc'
        sort_order = self.request.get('dir', default_sort_order)
        self.sort_order = {'ASC': 'asc',
                           'DESC': 'reverse'}.get(sort_order, sort_order)

        self.sort_reverse = self.sort_order == 'reverse'

    def create(self, paths=[]):
        """generate the task templates"""

        if 'abort' in self.request.keys():
            return self.request.RESPONSE.redirect(self.context.absolute_url())

        templates = []

        for path in paths:
            templates.append(self.context.restrictedTraverse(path))

        if len(templates) == 0:
            IStatusMessage(self.request).addStatusMessage(
                _(u'message_no_templates_selected',
                  default=u'You have not selected any templates'), type="info")

            return self.request.RESPONSE.redirect(self.context.absolute_url())

        # Create main task
        templatefolder = aq_parent(aq_inner(templates[0]))

        highest_deadline = max([temp.deadline for temp in templates])

        deadline_timedelta = api.portal.get_registry_record(
            'deadline_timedelta', interface=ITaskSettings)

        data = dict(
            title=templatefolder.title,
            issuer=self.replace_interactive_user('current_user'),
            responsible=self.replace_interactive_user('current_user'),
            responsible_client=get_current_org_unit().id(),
            task_type='direct-execution',
            deadline=(date.today()
                      + timedelta(highest_deadline + deadline_timedelta)),
            )

        main_task = createContent('opengever.task.task', **data)
        notify(ObjectCreatedEvent(main_task))
        main_task = addContentToContainer(
            self.context, main_task, checkConstraints=True)
        ogdsservice = ogds_service()

        # set marker Interfaces
        alsoProvides(main_task, IFromTasktemplateGenerated)

        # set the main_task in to the in progress state
        wft = getToolByName(self.context, 'portal_workflow')
        wft.doActionFor(main_task, 'task-transition-open-in-progress')

        # create subtasks
        for template in templates:
            deadline = date.today() + timedelta(template.deadline)

            data = dict(
                title=template.title,
                issuer=self.replace_interactive_user(template.issuer),
                responsible=self.replace_interactive_user(
                    template.responsible),
                task_type=template.task_type,
                text=template.text,
                deadline=deadline,
                )

            if template.responsible_client == INTERACTIVE_USERS:
                responsible_assigned_org_units = ogdsservice.assigned_org_units(
                    data['responsible'])
                current_org_unit = get_current_org_unit()
                if not responsible_assigned_org_units or \
                        current_org_unit in responsible_assigned_org_units:
                    data['responsible_client'] = current_org_unit.id()
                else:
                    data['responsible_client'] = \
                        responsible_assigned_org_units[0].id()
            else:
                data['responsible_client'] = template.responsible_client

            task = createContent('opengever.task.task', **data)
            notify(ObjectCreatedEvent(task))
            task = addContentToContainer(main_task,
                                         task,
                                         checkConstraints=True)
            alsoProvides(task, IFromTasktemplateGenerated)
            task.reindexObject()

            # add activity record for subtask
            activity = TaskAddedActivity(task, self.request)
            activity.record()

        # add activity record for the main task
        activity = TaskAddedActivity(main_task, self.request)
        activity.record()

        IStatusMessage(self.request).addStatusMessage(
            _(u'message_tasks_created', default=u'tasks created'), type="info")

        return self.request.RESPONSE.redirect(
            '%s#tasks' % self.context.absolute_url())

    def replace_interactive_user(self, principal):
        """Replaces interactive users in the principal.
        """

        if principal == 'responsible':
            # find the dossier
            dossier = self.context
            while not IDossierMarker.providedBy(dossier):
                if IPloneSiteRoot.providedBy(dossier):
                    raise ValueError('Could not find dossier')
                dossier = aq_parent(aq_inner(dossier))
            # get the responsible of the dossier
            wrapped_dossier = IDossier(dossier)
            return wrapped_dossier.responsible

        elif principal == 'current_user':
            # get the current user
            mtool = getToolByName(self.context, 'portal_membership')
            member = mtool.getAuthenticatedMember()
            if not member:
                raise Unauthorized()
            return member.getId()

        else:
            return principal

    def javascript_url(self):
        """Returns the URL to the javascript file (form.js) for embedding in
        the template. It also adds the date / time as parameter when
        portal_javscript is in debug mode.
        """
        url = getToolByName(self.context, 'portal_url')()
        url += '/++resource++tasktemplates.form.js'

        # debug mode on?
        jstool = getToolByName(self.context, 'portal_javascripts')
        if jstool.getDebugMode():
            url += '?now=' + str(datetime.now())

        return url
