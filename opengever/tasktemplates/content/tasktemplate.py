from datetime import date
from ftw.keywordwidget.widget import KeywordFieldWidget
from opengever.base.utils import get_date_with_delta_excluding_weekends
from opengever.ogds.base.utils import get_current_org_unit
from opengever.task import util
from opengever.task.util import update_reponsible_field_data
from opengever.tasktemplates import _
from opengever.tasktemplates.sources import TaskResponsibleSourceBinder
from opengever.tasktemplates.sources import TaskTemplateIssuerSourceBinder
from plone.autoform import directives as form
from plone.dexterity.browser.add import DefaultAddForm
from plone.dexterity.browser.add import DefaultAddView
from plone.dexterity.browser.edit import DefaultEditForm
from plone.dexterity.content import Item
from plone.supermodel import model
from z3c.form import widget
from z3c.form.browser import checkbox
from zope import schema
from zope.interface import implements


class ITaskTemplate(model.Schema):

    model.fieldset(
        u'common',
        label=_(u'fieldset_common', default=u'Common'),
        fields=[
            u'title',
            u'issuer',
            u'task_type',
            u'responsible_client',
            u'responsible',
            u'deadline',
            u'text',
            u'preselected'
        ],
    )

    title = schema.TextLine(
        title=_(u"label_title", default=u"Title"),
        description=_('help_title', default=u""),
        required=True,
    )

    form.widget('issuer', KeywordFieldWidget, async=True)
    issuer = schema.Choice(
        title=_(u"label_issuer", default=u"Issuer"),
        description=_('help_issuer', default=u""),
        source=TaskTemplateIssuerSourceBinder(),
        required=True,
    )

    form.widget(task_type='z3c.form.browser.radio.RadioFieldWidget')
    task_type = schema.Choice(
        title=_(u'label_task_type', default=u'Task Type'),
        description=_('help_task_type', default=u''),
        required=True,
        readonly=False,
        default=None,
        missing_value=None,
        source=util.getTaskTypeVocabulary,
    )

    form.mode(responsible_client='hidden')
    responsible_client = schema.Choice(
        title=_(u'label_resonsible_client',
                default=u'Responsible Client'),
        description=_(u'help_responsible_client',
                      default=u''),
        vocabulary='opengever.ogds.base.OrgUnitsVocabularyFactory',
        required=False)

    form.widget('responsible', KeywordFieldWidget, async=True)
    responsible = schema.Choice(
        title=_(u"label_responsible", default="Responsible"),
        description=_(u"help_responsible", default=""),
        source=TaskResponsibleSourceBinder(include_teams=True),
        required=False,
    )

    deadline = schema.Int(
        title=_(u"label_deadline", default=u"Deadline in workdays"),
        description=_('help_deadline', default=u""),
        required=True,
    )

    # Bad naming: comments is more appropriated
    model.primary('text')
    text = schema.Text(
        title=_(u"label_text", default=u"Text"),
        description=_(u"help_text", default=u""),
        required=False,
    )

    form.widget(preselected=checkbox.SingleCheckBoxFieldWidget)
    preselected = schema.Bool(
        title=_(u'label_preselected', default='Preselect'),
        description=_(u'help_preselected', default=''),
        required=False,
    )


class TaskTemplate(Item):
    implements(ITaskTemplate)

    def get_absolute_deadline(self):
        return get_date_with_delta_excluding_weekends(date.today(), self.deadline)


default_responsible_client = widget.ComputedWidgetAttribute(
    lambda adapter: get_current_org_unit().id(),
    field=ITaskTemplate['responsible_client'])


class TaskTemplateAddForm(DefaultAddForm):

    def createAndAdd(self, data):
        update_reponsible_field_data(data)
        return super(TaskTemplateAddForm, self).createAndAdd(data)


class TaskTemplateAddView(DefaultAddView):
    form = TaskTemplateAddForm


class TaskTemplateEditForm(DefaultEditForm):
    def applyChanges(self, data):
        update_reponsible_field_data(data)
        return super(TaskTemplateEditForm, self).applyChanges(data)
