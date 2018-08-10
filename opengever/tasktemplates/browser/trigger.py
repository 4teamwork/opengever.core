from AccessControl.users import nobody
from ftw.keywordwidget.widget import KeywordWidget
from opengever.base.browser.wizard import BaseWizardStepForm
from opengever.base.browser.wizard.interfaces import IWizardDataStorage
from opengever.base.oguid import Oguid
from opengever.base.source import DossierPathSourceBinder
from opengever.dossier.behaviors.dossier import IDossier
from opengever.ogds.base.actor import ActorLookup
from opengever.ogds.base.utils import get_current_org_unit
from opengever.ogds.base.utils import ogds_service
from opengever.task.util import update_reponsible_field_data
from opengever.tasktemplates import _
from opengever.tasktemplates import INTERACTIVE_USERS
from opengever.tasktemplates.content.tasktemplate import ITaskTemplate
from plone import api
from plone.app.uuid.utils import uuidToObject
from plone.autoform.widgets import ParameterizedWidget
from plone.supermodel import model
from plone.z3cform.interfaces import IDeferSecurityCheck
from plone.z3cform.layout import FormWrapper
from z3c.form.browser import checkbox
from z3c.form.browser import radio
from z3c.form.button import buttonAndHandler
from z3c.form.field import Field
from z3c.form.field import Fields
from z3c.form.form import Form
from z3c.form.interfaces import HIDDEN_MODE
from z3c.form.interfaces import INPUT_MODE
from z3c.relationfield.relation import RelationValue
from z3c.relationfield.schema import RelationChoice
from z3c.relationfield.schema import RelationList
from zope import schema
from zope.app.intid.interfaces import IIntIds
from zope.component import getUtility
from zope.i18n import translate
import copy
import re


TRIGGER_TASKTEMPLATE_STEPS = (
    ('select-tasktemplatefolder',
     _(u'label_tasktemplatefolder_selection',
       default=u'Tasktemplatefolder selection')),

    ('select-tasktemplates',
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
        dm = getUtility(IWizardDataStorage)
        dm.drop_data(get_datamanger_key(self.context))
        return self.request.RESPONSE.redirect(self.context.absolute_url())

    def has_active_tasktemplates(self):
        return bool(api.content.find(
            portal_type='opengever.tasktemplates.tasktemplatefolder',
            review_state='tasktemplatefolder-state-activ'))


class TriggerTaskTemlateFolderView(FormWrapper):
    """View to render the form to create a new period."""

    form = SelectTaskTemplateFolderWizardStep


class ISelectTaskTemplates(model.Schema):

    tasktemplates = schema.List(
        title=_('label_tasktemplates', default=u'Tasktemplates'),
        required=True,
        value_type=schema.Choice(
            source='opengever.tasktemplates.tasktemplates',
        ),
        missing_value=[]
    )

    start_immediately = schema.Bool(
        title=_(u'label_start_immediately', default=u'Start immediately'),
        description=_(u'description_start_immediately', default=u'Immediately '
                      'open the first task after creation.'),
        default=True,
        required=True,
    )


class SelectTaskTemplatesWizardStep(BaseWizardStepForm, Form):
    step_name = 'select-tasktemplates'
    label = _('label_select_tasktemplates',
              default=u'Select tasktemplates')

    steps = TRIGGER_TASKTEMPLATE_STEPS
    fields = Fields(ISelectTaskTemplates)

    fields['tasktemplates'].widgetFactory[INPUT_MODE] = checkbox.CheckBoxFieldWidget
    fields['start_immediately'].widgetFactory[INPUT_MODE] = checkbox.SingleCheckBoxFieldWidget  # noqa

    def updateWidgets(self):
        super(SelectTaskTemplatesWizardStep, self).updateWidgets()
        if not self.get_selected_task_templatefolder().is_sequential:
            self.widgets['start_immediately'].mode = HIDDEN_MODE

        self.widgets['tasktemplates'].value = self.get_preselected_tasktemplates()

    def updateActions(self):
        super(SelectTaskTemplatesWizardStep, self).updateActions()
        self.actions['continue'].addClass("context")

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
        dm = getUtility(IWizardDataStorage)
        dm.drop_data(get_datamanger_key(self.context))
        return self.request.RESPONSE.redirect(self.context.absolute_url())

    def get_responsible_client(self, template, responsible):
        if template.responsible_client == INTERACTIVE_USERS:
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

    def updateActions(self):
        super(SelectResponsiblesWizardStep, self).updateActions()
        self.actions['trigger'].addClass("context")

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
                widget.value = self.get_responsible_widget_value(template)

    def get_responsible_widget_value(self, template):
        org_unit_id, responsible = self.replace_interactive_actors(template)
        actor_lookup = ActorLookup(responsible)
        if actor_lookup.is_inbox() or actor_lookup.is_team():
            return (u'{}'.format(actor_lookup.identifier), )
        else:
            return (u'{}:{}'.format(org_unit_id, actor_lookup.identifier), )

    def replace_interactive_actors(self, template):
        """The current systems knows two interactive users:

        `responsible`: the reponsible of the main dossier.
        `current_user`: the currently logged in user.
        """
        if template.responsible_client == INTERACTIVE_USERS:
            if template.responsible == 'responsible':
                principal = IDossier(self.context.get_main_dossier()).responsible
            elif template.responsible == 'current_user':
                principal = api.user.get_current().getId()

            return get_current_org_unit().id(), principal

        return template.responsible_client, template.responsible

    def get_selected_task_templatefolder(self):
        uid = get_wizard_data(self.context, 'tasktemplatefolder')
        return api.content.get(UID=uid)

    def get_selected_related_documents(self):
        intids = getUtility(IIntIds)
        value = get_wizard_data(self.context, 'related_documents')
        return [RelationValue(intids.getId(obj)) for obj in value]

    def get_selected_tasktemplates(self):
        tasktemplates = get_wizard_data(self.context, 'tasktemplates')
        return [uuidToObject(uid) for uid in tasktemplates]

    @buttonAndHandler(_(u'button_trigger', default=u'Trigger'), name='trigger')
    def handle_continue(self, action):
        data, errors = self.extractData()
        if errors:
            return
        tasktemplatefolder = self.get_selected_task_templatefolder()
        related_documents = self.get_selected_related_documents()
        start_immediately = get_wizard_data(self.context, 'start_immediately')
        templates = self.get_selected_tasktemplates()
        responsibles = {}

        for template in templates:
            responsible_client, responsible = self.get_responsible(template, data)
            responsibles[template.id] = {
                'responsible': responsible,
                'responsible_client': responsible_client}

        tasktemplatefolder.trigger(self.context, templates, related_documents,
                                   responsibles, start_immediately)

        api.portal.show_message(
            _(u'message_tasks_created', default=u'tasks created'),
            self.request, type="info")
        return self.request.RESPONSE.redirect(
            '{}#tasks'.format(self.context.absolute_url()))

    @buttonAndHandler(_(u'button_cancel', default=u'Cancel'))
    def handle_cancel(self, action):
        dm = getUtility(IWizardDataStorage)
        dm.drop_data(get_datamanger_key(self.context))
        return self.request.RESPONSE.redirect(self.context.absolute_url())

    def get_responsible(self, template, data):
        form_identifier = '{}.responsible'.format(template.id)
        data = {"responsible": data.get(form_identifier)}
        update_reponsible_field_data(data)
        return data['responsible_client'], data['responsible']


class SelectResponsiblesView(FormWrapper):
    form = SelectResponsiblesWizardStep
