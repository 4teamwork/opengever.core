from collective import dexteritytextindexer
from datetime import datetime, timedelta
from five import grok
from ftw.datepicker.widget import DatePickerFieldWidget
from opengever.base.source import DossierPathSourceBinder
from opengever.ogds.base.autocomplete_widget import AutocompleteFieldWidget
from opengever.ogds.base.interfaces import IContactInformation
from opengever.ogds.base.utils import get_client_id
from opengever.task import _
from opengever.task import util
from opengever.task.validators import NoCheckedoutDocsValidator
from plone.dexterity.content import Container
from plone.directives import form, dexterity
from z3c.form import validator
from z3c.form.interfaces import HIDDEN_MODE
from z3c.relationfield.schema import RelationChoice, RelationList
from zope import schema
from zope.app.intid.interfaces import IIntIds
from zope.component import getUtility, getMultiAdapter
from zope.component import provideAdapter
from zope.interface import implements
from zope.schema.vocabulary import getVocabularyRegistry


_marker = object()


class ITask(form.Schema):

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
            u'relatedItems',
            ],
        )

    form.fieldset(
        u'additional',
        label=_(u'fieldset_additional', u'Additional'),
        fields=[
            u'expectedStartOfWork',
            u'expectedDuration',
            u'expectedCost',
            u'effectiveDuration',
            u'effectiveCost',
            u'date_of_completion',
            ],
        )

    dexteritytextindexer.searchable('title')
    title = schema.TextLine(
        title=_(u"label_title", default=u"Title"),
        description=_('help_title', default=u""),
        required=True,
        )

    form.widget(issuer=AutocompleteFieldWidget)
    issuer = schema.Choice(
        title=_(u"label_issuer", default=u"Issuer"),
        description=_('help_issuer', default=u""),
        vocabulary=u'opengever.ogds.base.ContactsAndUsersVocabulary',
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
        vocabulary='opengever.ogds.base.ClientsVocabulary',
        required=True)

    form.widget(responsible=AutocompleteFieldWidget)
    responsible = schema.Choice(
        title=_(u"label_responsible", default=u"Responsible"),
        description=_(u"help_responsible", default=""),
        vocabulary=u'opengever.ogds.base.UsersAndInboxesVocabulary',
        required=True,
        )

    form.widget(deadline=DatePickerFieldWidget)
    deadline = schema.Date(
        title=_(u"label_deadline", default=u"Deadline"),
        description=_(u"help_deadline", default=u""),
        required=True,
        )

    form.widget(deadline=DatePickerFieldWidget)
    date_of_completion = schema.Date(
        title=_(u"label_date_of_completion", default=u"Date of completion"),
        description=_(u"help_date_of_completion", default=u""),
        required=False,
        )

    dexteritytextindexer.searchable('text')
    form.primary('text')
    text = schema.Text(
        title=_(u"label_text", default=u"Text"),
        description=_(u"help_text", default=u""),
        required=False,
        )

    relatedItems = RelationList(
        title=_(u'label_related_items', default=u'Related Items'),
        default=[],
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

    form.widget(deadline=DatePickerFieldWidget)
    expectedStartOfWork = schema.Date(
        title=_(u"label_expectedStartOfWork", default="Start with work"),
        description=_(u"help_expectedStartOfWork", default=""),
        required=False,
        )

    expectedDuration = schema.Float(
        title=_(u"label_expectedDuration", default="Expected duration", ),
        description=_(u"help_expectedDuration", default="Duration in h"),
        required=False,
        )

    expectedCost = schema.Float(
        title=_(u"label_expectedCost", default="expected cost"),
        description=_(u"help_expectedCost", default="Cost in CHF"),
        required=False,
        )

    effectiveDuration = schema.Float(
        title=_(u"label_effectiveDuration", default="effective duration"),
        description=_(u"help_effectiveDuration", default="Duration in h"),
        required=False,
        )

    effectiveCost = schema.Float(
        title=_(u"label_effectiveCost", default="effective cost"),
        description=_(u"help_effectiveCost", default="Cost in CHF"),
        required=False,
        )

    form.omitted('predecessor')
    predecessor = schema.TextLine(
        title=_(u'label_predecessor', default=u'Predecessor'),
        description=_(u'help_predecessor', default=u''),
        required=False)


validator.WidgetValidatorDiscriminators(
    NoCheckedoutDocsValidator, field=ITask['relatedItems'])
provideAdapter(NoCheckedoutDocsValidator)


# # XXX doesn't work yet.
#@form.default_value(field=ITask['issuer'])


def default_issuer(data):
    portal_state = getMultiAdapter(
        (data.context, data.request),
        name=u"plone_portal_state")
    member = portal_state.member()
    return member.getId()


class Task(Container):
    implements(ITask)

    def __init__(self, *args, **kwargs):
        super(Task, self).__init__(*args, **kwargs)

    # REMOVED UNCOMMENT unused title function
    # def Title(self):
    #     registry = queryUtility(IRegistry)
    #     proxy = registry.forInterface(ITaskSettings)
    #     title = "#%s %s"% (
    #   getUtility(ISequenceNumber).get_number(self),self.task_type)
    #     relatedItems = getattr(self,'relatedItems',[])
    #     if len(relatedItems) == 1:
    #         title += " (%s)" % self.relatedItems[0].to_object.title
    #     elif len(relatedItems) > 1:
    #         title += " (%i Dokumente)" % len(self.relatedItems)
    #     if self.text:
    #         crop_length = int(getattr(proxy,'crop_length',20))
    #         text = self.text.encode('utf8')
    #         text = self.restrictedTraverse('@@plone').cropText(
    #   text,crop_length)
    #         text = text.decode('utf8')
    #         title += ": %s" % text
    #     return title
    @property
    def sequence_number(self):
        return self._sequence_number

    @property
    def task_type_category(self):
        for category in ['unidirectional_by_reference',
                         'unidirectional_by_value',
                         'bidirectional_by_reference',
                         'bidirectional_by_value']:
            voc = getVocabularyRegistry().get(
                self, 'opengever.task.' + category)
            if self.task_type in voc:
                return category
        return None

    @property
    def client_id(self):
        return get_client_id()


@form.default_value(field=ITask['deadline'])
def deadlineDefaultValue(data):
    # To get hold of the folder, do: context = data.context
    return datetime.today() + timedelta(5)


@form.default_value(field=ITask['responsible_client'])
def responsible_client_default_value(data):
    return get_client_id()


# XXX
# setting the default value of a RelationField does not work as expected
# or we don't know how to set it.
# thus we use an add form hack by injecting the values into the request.

class AddForm(dexterity.AddForm):
    grok.name('opengever.task.task')

    def update(self):
        # put default value for relatedItems into request
        paths = self.request.get('paths', [])
        if paths:
            self.request.set('form.widgets.relatedItems', paths)
        # put default value for issuer into request
        portal_state = getMultiAdapter((self.context, self.request),
                                       name=u"plone_portal_state")
        member = portal_state.member()
        if not self.request.get('form.widgets.issuer', None):
            self.request.set('form.widgets.issuer', [member.getId()])
        super(AddForm, self).update()

        # omit the responsible_client field and adjust the field description
        # of the responsible field if there is only one client configured.
        info = getUtility(IContactInformation)
        if len(info.get_clients()) <= 1:
            self.groups[0].widgets['responsible_client'].mode = HIDDEN_MODE
            self.groups[0].widgets['responsible'].field.description = _(
                u"help_responsible_single_client_setup", default=u"")


class EditForm(dexterity.EditForm):
    """Standard EditForm, just require the Edit Task permission"""
    grok.context(ITask)
    grok.require('opengever.task.EditTask')

    def update(self):
        super(EditForm, self).update()

        # omit the responsible_client field and adjust the field description
        # of the responsible field if there is only one client configured.
        info = getUtility(IContactInformation)
        if len(info.get_clients()) <= 1:
            self.groups[0].widgets['responsible_client'].mode = HIDDEN_MODE
            self.groups[0].widgets['responsible'].field.description = _(
                u"help_responsible_single_client_setup", default=u"")


def related_document(context):
    intids = getUtility(IIntIds)
    return intids.getId(context)


class DocumentRedirector(grok.View):
    """Redirector View specific for documents created on a task
    redirect directly to the relateddocuments tab
    instead of the default documents tab
    """

    grok.name('document-redirector')
    grok.context(ITask)
    grok.require('zope2.View')

    def render(self):
        referer = self.context.REQUEST.environ.get('HTTP_REFERER')
        if referer.endswith('++add++opengever.document.document'):
            return self.context.REQUEST.RESPONSE.redirect(
                '%s#relateddocuments' % self.context.absolute_url())
        else:
            return self.context.REQUEST.RESPONSE.redirect(
                self.context.absolute_url())
