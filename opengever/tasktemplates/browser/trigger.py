from AccessControl import Unauthorized
from Acquisition import aq_inner
from Acquisition import aq_parent
from datetime import date
from datetime import timedelta
from five import grok
from opengever.base.browser.wizard import BaseWizardStepForm
from opengever.base.browser.wizard.interfaces import IWizardDataStorage
from opengever.base.oguid import Oguid
from opengever.dossier.behaviors.dossier import IDossier
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.ogds.base.utils import get_current_org_unit
from opengever.ogds.base.utils import ogds_service
from opengever.task.activities import TaskAddedActivity
from opengever.tasktemplates import _
from opengever.tasktemplates.content.tasktemplate import MAIN_TASK_DEADLINE_DELTA
from opengever.tasktemplates.interfaces import IFromTasktemplateGenerated
from plone import api
from plone.dexterity.utils import createContent, addContentToContainer
from plone.directives import form
from plone.z3cform.layout import FormWrapper
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from Products.CMFPlone.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage
from z3c.form.browser import checkbox
from z3c.form.browser import radio
from z3c.form.button import buttonAndHandler
from z3c.form.field import Fields
from z3c.form.form import Form
from z3c.form.interfaces import INPUT_MODE
from zope import schema
from zope.component import getUtility
from zope.event import notify
from zope.interface import alsoProvides
from zope.interface import provider
from zope.lifecycleevent import ObjectCreatedEvent
from zope.schema.interfaces import IContextAwareDefaultFactory


TRIGGER_TASKTEMPLATE_STEPS = (
    ('select-tasktemplatefolder',
     _(u'label_tasktemplatefolder_selection',
       default=u'Tasktemplatefolder selection')),

    ('select-tasktemplate',
     _(u'label_tasktemplate_selection', default=u'Tasktemplate selection'))
)


def get_datamanger_key(dossier):
    """Return the wizard-storage key used to store the selected data."""

    return 'trigger_tasktemplatefolder:{}'.format(Oguid.for_object(dossier).id)


def get_wizard_data(context, key):
    """Return the wizard-storage data with the given key."""
    dm = getUtility(IWizardDataStorage)
    return dm.get(get_datamanger_key(context), key)


class ISelectTaskTemplateFolder(form.Schema):

    tasktemplatefolder = schema.Choice(
        title=_('label_tasktemplatefolder', default=u'Tasktemplatefolder'),
        source='opengever.tasktemplates.active_tasktemplatefolders',
        required=True
    )


class SelectTaskTemplateFolderWizardStep(BaseWizardStepForm, Form):
    step_name = 'select-tasktemplatefolder'
    label = _('label_select_tasktemplatefolder',
              default=u'Select tasktemplatefolder')

    steps = TRIGGER_TASKTEMPLATE_STEPS
    fields = Fields(ISelectTaskTemplateFolder)

    def update(self):
        if not self.has_active_tasktemplates():
            api.portal.show_message(
                _(u'msg_no_active_tasktemplatefolders',
                  default=u'Currently there are no active task template '
                  'folders registered.'), self.request, type='error')
            return self.request.RESPONSE.redirect(self.context.absolute_url())

        self.fields['tasktemplatefolder'].widgetFactory[INPUT_MODE] = radio.RadioFieldWidget
        return super(SelectTaskTemplateFolderWizardStep, self).update()

    @buttonAndHandler(_(u'button_continue', default=u'Continue'), name='save')
    def handle_continue(self, action):
        data, errors = self.extractData()
        if errors:
            return

        dm = getUtility(IWizardDataStorage)
        dm.update(get_datamanger_key(self.context), data)

        return self.request.RESPONSE.redirect(
            '{}/select-tasktemplates'.format(self.context.absolute_url()))

    @buttonAndHandler(_(u'button_cancel', default=u'Cancel'))
    def handle_cancel(self, action):
        return self.request.RESPONSE.redirect(self.context.absolute_url())

    def has_active_tasktemplates(self):
        return bool(api.content.find(
            portal_type='opengever.tasktemplates.tasktemplatefolder',
            review_state='tasktemplatefolder-state-activ'))


class TriggerTaskTemlateFolderView(FormWrapper, grok.View):
    """View to render the form to create a new period."""

    grok.context(IDossierMarker)
    # grok.name('trigger-tasktemplatefolder')
    grok.name('add-tasktemplate')
    grok.require('cmf.AddPortalContent')
    form = SelectTaskTemplateFolderWizardStep

    def __init__(self, *args, **kwargs):
        FormWrapper.__init__(self, *args, **kwargs)
        grok.View.__init__(self, *args, **kwargs)


@provider(IContextAwareDefaultFactory)
def get_preselected_tasktemplates(context):
    uid = get_wizard_data(context, 'tasktemplatefolder')
    templatefolder = api.content.get(UID=uid)
    templates = api.content.find(
        context=templatefolder,
        portal_type='opengever.tasktemplates.tasktemplate')
    return [template.UID for template in templates
            if template.getObject().preselected]


class ISelectTaskTemplates(form.Schema):

    tasktemplates = schema.List(
        title=_('label_tasktemplates', default=u'Tasktemplates'),
        required=True,
        value_type=schema.Choice(
            source='opengever.tasktemplates.tasktemplates',
        ),
        defaultFactory=get_preselected_tasktemplates
    )


class SelectTaskTemplatesWizardStep(BaseWizardStepForm, Form):
    step_name = 'select-tasktemplates'
    label = _('label_select_tasktemplates',
              default=u'Select tasktemplates')

    steps = TRIGGER_TASKTEMPLATE_STEPS
    fields = Fields(ISelectTaskTemplates)

    def update(self):
        self.fields['tasktemplates'].widgetFactory[INPUT_MODE] = checkbox.CheckBoxFieldWidget
        return super(SelectTaskTemplatesWizardStep, self).update()

    def get_preselected_tasktemplates(self):
        templates = api.content.find(
            context=self.get_selected_task_templatefolder(),
            portal_type='opengever.tasktemplates.tasktemplate')

        return [template.UID for template in templates
                if template.getObject().preselected]

    def get_selected_task_templatefolder(self):
        uid = get_wizard_data(self.context, 'tasktemplatefolder')
        return api.content.get(UID=uid)

    @buttonAndHandler(_(u'button_trigger', default=u'Trigger'), name='trigger')
    def handle_continue(self, action):
        data, errors = self.extractData()
        if errors:
            return

        catalog = api.portal.get_tool('portal_catalog')
        tasktemplatefolder = self.get_selected_task_templatefolder()
        templates = [brain.getObject() for brain in
                     catalog(UID=data.get('tasktemplates'))]

        main_task = self.create_main_task(tasktemplatefolder, templates)
        self.create_subtasks(main_task, templates)

        IStatusMessage(self.request).addStatusMessage(
            _(u'message_tasks_created', default=u'tasks created'), type="info")
        return self.request.RESPONSE.redirect(
            '%s#tasks' % self.context.absolute_url())

    def create_main_task(self, templatefolder, selected_templates):
        highest_deadline = max(
            [template.deadline for template in selected_templates])

        data = dict(
            title=templatefolder.title,
            issuer=self.replace_interactive_user('current_user'),
            responsible=self.replace_interactive_user('current_user'),
            responsible_client=get_current_org_unit().id(),
            task_type='direct-execution',
            deadline=date.today() +
            timedelta(highest_deadline + MAIN_TASK_DEADLINE_DELTA),
        )

        main_task = createContent('opengever.task.task', **data)
        notify(ObjectCreatedEvent(main_task))
        main_task = addContentToContainer(
            self.context, main_task, checkConstraints=True)

        # set marker Interfaces
        alsoProvides(main_task, IFromTasktemplateGenerated)

        # set the main_task in to the in progress state
        wft = getToolByName(self.context, 'portal_workflow')
        wft.doActionFor(main_task, 'task-transition-open-in-progress')

        return main_task

    def create_subtasks(self, main_task, selected_templates):
        for template in selected_templates:
            self.create_subtask(main_task, template)

    def create_subtask(self, main_task, template):
        data = dict(
            title=template.title,
            issuer=self.replace_interactive_user(template.issuer),
            responsible=self.replace_interactive_user(
                template.responsible),
            task_type=template.task_type,
            text=template.text,
            deadline=date.today() + timedelta(template.deadline),
        )

        if template.responsible_client == 'interactive_users':
            responsible_assigned_org_units = ogds_service().assigned_org_units(
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
        activity = TaskAddedActivity(task, self.request, self.context)
        activity.record()

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

    @buttonAndHandler(_(u'button_cancel', default=u'Cancel'))
    def handle_cancel(self, action):
        return self.request.RESPONSE.redirect(self.context.absolute_url())


class SelectTaskTemplatesView(FormWrapper, grok.View):
    grok.context(IDossierMarker)
    grok.name('select-tasktemplates')
    grok.require('cmf.AddPortalContent')
    form = SelectTaskTemplatesWizardStep

    def __init__(self, *args, **kwargs):
        FormWrapper.__init__(self, *args, **kwargs)
        grok.View.__init__(self, *args, **kwargs)
