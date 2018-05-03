from AccessControl.users import nobody
from datetime import date
from datetime import timedelta
from ftw.keywordwidget.widget import KeywordWidget
from opengever.base.browser.wizard import BaseWizardStepForm
from opengever.base.browser.wizard.interfaces import IWizardDataStorage
from opengever.base.oguid import Oguid
from opengever.base.source import DossierPathSourceBinder
from opengever.dossier.behaviors.dossier import IDossier
from opengever.ogds.base.utils import get_current_org_unit
from opengever.ogds.base.utils import ogds_service
from opengever.task.activities import TaskAddedActivity
from opengever.task.interfaces import ITaskSettings
from opengever.tasktemplates import _
from opengever.tasktemplates.content.tasktemplate import ITaskTemplate
from opengever.tasktemplates.interfaces import IFromTasktemplateGenerated
from plone import api
from plone.autoform.widgets import ParameterizedWidget
from plone.dexterity.utils import addContentToContainer
from plone.dexterity.utils import createContent
from plone.supermodel import model
from plone.z3cform.interfaces import IDeferSecurityCheck
from plone.z3cform.layout import FormWrapper
from z3c.form.browser import checkbox
from z3c.form.browser import radio
from z3c.form.button import buttonAndHandler
from z3c.form.field import Field
from z3c.form.field import Fields
from z3c.form.form import Form
from z3c.form.interfaces import INPUT_MODE
from z3c.relationfield.relation import RelationValue
from z3c.relationfield.schema import RelationChoice
from z3c.relationfield.schema import RelationList
from zope import schema
from zope.app.intid.interfaces import IIntIds
from zope.component import getAdapter
from zope.component import getUtility
from zope.event import notify
from zope.i18n import translate
from zope.interface import alsoProvides
from zope.interface import provider
from zope.lifecycleevent import ObjectCreatedEvent
from zope.schema.interfaces import IContextAwareDefaultFactory
import copy
import re


TRIGGER_TASKTEMPLATE_STEPS = (
    ('select-tasktemplatefolder',
     _(u'label_tasktemplatefolder_selection',
       default=u'Tasktemplatefolder selection')),

    ('select-tasktemplate',
     _(u'label_tasktemplate_selection', default=u'Tasktemplate selection')),

    ('select-responsibles',
     _(u'label_responsibles_selection', default=u'Responsibles selection'))
)


def get_datamanger_key(dossier):
    """Return the wizard-storage key used to store the selected data."""

    return 'trigger_tasktemplatefolder:{}'.format(Oguid.for_object(dossier).id)


def get_wizard_data(context, key):
    """Return the wizard-storage data with the given key."""
    dm = getUtility(IWizardDataStorage)
    return dm.get(get_datamanger_key(context), key)


class ISelectTaskTemplateFolder(model.Schema):

    tasktemplatefolder = schema.Choice(
        title=_('label_tasktemplatefolder', default=u'Tasktemplatefolder'),
        source='opengever.tasktemplates.active_tasktemplatefolders',
        required=True
    )

    related_documents = RelationList(
        title=_(u'label_related_documents', default=u'Related documents'),
        default=[],
        missing_value=[],
        value_type=RelationChoice(
            title=u"Related",
            source=DossierPathSourceBinder(
                portal_type=("opengever.document.document", "ftw.mail.mail"),
                navigation_tree_query={
                    'object_provides':
                    ['opengever.dossier.behaviors.dossier.IDossierMarker',
                     'opengever.document.document.IDocumentSchema',
                     'opengever.task.task.ITask',
                     'ftw.mail.mail.IMail', ],
                }),
            ),
        required=False,
    )


class SelectTaskTemplateFolderWizardStep(BaseWizardStepForm, Form):
    step_name = 'select-tasktemplatefolder'
    label = _('label_select_tasktemplatefolder',
              default=u'Select tasktemplatefolder')

    steps = TRIGGER_TASKTEMPLATE_STEPS
    fields = Fields(ISelectTaskTemplateFolder)

    def update(self):
        # ignore unauthorized checks (they're called by the contenttree widget)
        if api.user.get_current() == nobody:
            pass

        elif not self.has_active_tasktemplates():
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


class TriggerTaskTemlateFolderView(FormWrapper):
    """View to render the form to create a new period."""

    form = SelectTaskTemplateFolderWizardStep


@provider(IContextAwareDefaultFactory)
def get_preselected_tasktemplates(context):
    uid = get_wizard_data(context, 'tasktemplatefolder')
    templatefolder = api.content.get(UID=uid)
    templates = api.content.find(
        context=templatefolder,
        portal_type='opengever.tasktemplates.tasktemplate')
    return [template.UID for template in templates
            if template.getObject().preselected]


class ISelectTaskTemplates(model.Schema):

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

    def get_selected_related_documents(self):
        intids = getUtility(IIntIds)
        value = get_wizard_data(self.context, 'related_documents')
        return [RelationValue(intids.getId(obj)) for obj in value]

    @buttonAndHandler(_(u'button_continue', default=u'Continue'), name='continue')
    def handle_continue(self, action):
        data, errors = self.extractData()
        if errors:
            return

        dm = getUtility(IWizardDataStorage)
        dm.update(get_datamanger_key(self.context), data)

        return self.request.RESPONSE.redirect(
            '{}/select-responsibles'.format(self.context.absolute_url()))

    @buttonAndHandler(_(u'button_cancel', default=u'Cancel'))
    def handle_cancel(self, action):
        return self.request.RESPONSE.redirect(self.context.absolute_url())

    def get_responsible_client(self, template, responsible):
        if template.responsible_client == 'interactive_users':
            current_org_unit = get_current_org_unit()
            responsible_org_units = ogds_service().assigned_org_units(responsible)

            if current_org_unit in responsible_org_units or \
               not responsible_org_units:
                return current_org_unit.id()
            else:
                return responsible_org_units[0].id()

        return template.responsible_client


class SelectTaskTemplatesView(FormWrapper):
    form = SelectTaskTemplatesWizardStep


class SelectResponsiblesWizardStep(BaseWizardStepForm, Form):
    step_name = 'select-responsibles'
    label = _('label_select_responsibles',
              default=u'Select responsibles')

    steps = TRIGGER_TASKTEMPLATE_STEPS

    @property
    def fields(self):
        """Dynamically generate a responsible field with the Keywordwidget
        for each selected template.
        """

        # When using the keywordwidget autocomplete search, the widget is
        # traversing anonymously. Therefore we're not able to get the selected
        # templates and generate all fields correctly.
        # Therefore we handle all responsible widget traversals "manually".
        responsible_field_match = re.match(
            r'^{}(.*?)\.responsible$'.format(re.escape('++widget++form.widgets.')),
            self.request._steps[-1])
        if IDeferSecurityCheck.providedBy(self.request) and responsible_field_match:
            field = Field(ITaskTemplate['responsible'],
                          prefix=responsible_field_match.group(1),)
            field.widgetFactory[INPUT_MODE] = ParameterizedWidget(
                KeywordWidget, async=True)
            return Fields(field)

        self.fallback_field = ITaskTemplate['responsible']
        fields = []
        for template in self.get_selected_tasktemplates():
            schema_field = copy.copy(ITaskTemplate['responsible'])
            field = Field(schema_field, prefix=template.id)
            field.field.required = True
            field.widgetFactory[INPUT_MODE] = ParameterizedWidget(
                KeywordWidget, async=True)
            fields.append(field)

        return Fields(*fields)

    def updateWidgets(self):
        """Change the label of the dynamically generated responsible fields.
        """
        super(SelectResponsiblesWizardStep, self).updateWidgets()
        if IDeferSecurityCheck.providedBy(self.request):
            return

        for name in self.widgets:
            if not name.endswith('responsible'):
                continue
            widget = self.widgets[name]
            template_id = self.fields[name].prefix
            template = self.get_selected_task_templatefolder().get(template_id)
            widget.label = translate(
                _('label_responsible_for_task',
                  default=u'Responsible \xab${template_title}\xbb',
                  mapping={'template_title': template.title}),
                context=self.request)

            if template.responsible:
                widget.value = (u'{}:{}'.format(
                    template.responsible_client, template.responsible), )

    def get_selected_task_templatefolder(self):
        uid = get_wizard_data(self.context, 'tasktemplatefolder')
        return api.content.get(UID=uid)

    def get_selected_related_documents(self):
        intids = getUtility(IIntIds)
        value = get_wizard_data(self.context, 'related_documents')
        return [RelationValue(intids.getId(obj)) for obj in value]

    def get_selected_tasktemplates(self):
        tasktemplates = get_wizard_data(self.context, 'tasktemplates')
        catalog = api.portal.get_tool('portal_catalog')
        return [brain.getObject() for brain in catalog(UID=tasktemplates)]

    @buttonAndHandler(_(u'button_trigger', default=u'Trigger'), name='trigger')
    def handle_continue(self, action):
        data, errors = self.extractData()
        if errors:
            return

        tasktemplatefolder = self.get_selected_task_templatefolder()
        related_documents = self.get_selected_related_documents()
        templates = self.get_selected_tasktemplates()
        self.responsibles = data

        main_task = self.create_main_task(tasktemplatefolder, templates)
        self.create_subtasks(
            main_task, templates, related_documents, responsibles=data)

        api.portal.show_message(
            _(u'message_tasks_created', default=u'tasks created'),
            self.request, type="info")

        return self.request.RESPONSE.redirect(
            '{}#tasks'.format(self.context.absolute_url()))

    @buttonAndHandler(_(u'button_cancel', default=u'Cancel'))
    def handle_cancel(self, action):
        return self.request.RESPONSE.redirect(self.context.absolute_url())

    def create_main_task(self, templatefolder, selected_templates):
        highest_deadline = max(
            [template.deadline for template in selected_templates])

        deadline_timedelta = api.portal.get_registry_record(
            'deadline_timedelta', interface=ITaskSettings)

        data = dict(
            title=templatefolder.title,
            issuer=self.replace_interactive_user('current_user'),
            responsible=self.replace_interactive_user('current_user'),
            responsible_client=get_current_org_unit().id(),
            task_type='direct-execution',
            deadline=date.today() +
            timedelta(highest_deadline + deadline_timedelta),
        )

        main_task = createContent('opengever.task.task', **data)
        notify(ObjectCreatedEvent(main_task))
        main_task = addContentToContainer(
            self.context, main_task, checkConstraints=True)

        self.mark_as_generated_from_tasktemplate(main_task)

        # set the main_task in to the in progress state
        api.content.transition(obj=main_task,
                               transition='task-transition-open-in-progress')

        return main_task

    def create_subtasks(self, main_task,
                        selected_templates, related_documents, responsibles):

        for template in selected_templates:
            self.create_subtask(main_task, template, related_documents)

    def create_subtask(self, main_task, template, related_documents):
        responsible, responsible_client = self.get_responsible(template)
        data = dict(
            title=template.title,
            issuer=self.replace_interactive_user(template.issuer),
            responsible=self.replace_interactive_user(responsible),
            responsible_client=responsible_client,
            task_type=template.task_type,
            text=template.text,
            relatedItems=related_documents,
            deadline=date.today() + timedelta(template.deadline),
        )

        task = createContent('opengever.task.task', **data)
        notify(ObjectCreatedEvent(task))
        task = addContentToContainer(main_task, task, checkConstraints=True)
        self.mark_as_generated_from_tasktemplate(task)

        task.reindexObject()

        # add activity record for subtask
        activity = TaskAddedActivity(task, self.request, self.context)
        activity.record()

    def get_responsible(self, template):
        form_identifier = '{}.responsible'.format(template.id)
        value = self.responsibles.get(form_identifier)
        responsible_client, responsible = value.split(':')

        if responsible_client == 'interactive_users':
            responsible_client = get_current_org_unit().id()
            responsible = self.replace_interactive_user(responsible)

        return responsible, responsible_client

    def replace_interactive_user(self, principal):
        """The current systems knows two interactive users:

        `responsible`: the reponsible of the main dossier.
        `current_user`: the currently logged in user.
        """

        if principal == 'responsible':
            finder = getAdapter(self.context, name='parent-dossier-finder')
            return IDossier(finder.find_dossier()).responsible

        elif principal == 'current_user':
            return api.user.get_current().getId()

        else:
            return principal

    def get_responsible_client(self, template, responsible):
        if template.responsible_client == 'interactive_users':
            current_org_unit = get_current_org_unit()
            responsible_org_units = ogds_service().assigned_org_units(responsible)

            if current_org_unit in responsible_org_units or \
               not responsible_org_units:
                return current_org_unit.id()
            else:
                return responsible_org_units[0].id()

        return template.responsible_client

    def mark_as_generated_from_tasktemplate(self, task):
        alsoProvides(task, IFromTasktemplateGenerated)


class SelectResponsiblesView(FormWrapper):
    form = SelectResponsiblesWizardStep
