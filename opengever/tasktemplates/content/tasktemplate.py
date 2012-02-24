from opengever.tasktemplates import _
from plone.directives import form
from plone.dexterity.content import Item
from zope.interface import implements
from zope import schema
from plone.formwidget.autocomplete import AutocompleteFieldWidget
from opengever.task import util
from z3c.form.browser import checkbox

# days wich are summized for calculating the main task deadline
MAIN_TASK_DEADLINE_DELTA = 5


class ITaskTemplate(form.Schema):

    form.fieldset(
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

    form.widget(issuer=AutocompleteFieldWidget)
    issuer = schema.Choice(
        title=_(u"label_issuer", default=u"Issuer"),
        description=_('help_issuer', default=u""),
        vocabulary=u'opengever.tasktemplates.IssuerVocabulary',
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

    responsible_client = schema.Choice(
        title=_(u'label_resonsible_client',
                default=u'Responsible Client'),
        description=_(u'help_responsible_client',
                      default=u''),
        vocabulary='opengever.tasktemplates.ResponsibleClientVocabulary',
        required=True)

    form.widget(responsible=AutocompleteFieldWidget)
    responsible = schema.Choice(
        title=_(u"label_responsible", default="Responsible"),
        description=_(u"help_responsible", default=""),
        vocabulary=u'opengever.tasktemplates.ResponsibleVocabulary',
        required=True,
        )

    deadline = schema.Int(
        title=_(u"label_deadline", default=u"Deadline in Days"),
        description=_('help_deadline', default=u""),
        required=True,
    )

    form.primary('text')
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
