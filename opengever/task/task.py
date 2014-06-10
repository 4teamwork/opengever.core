from AccessControl.PermissionRole import rolesForPermissionOn
from Acquisition import aq_inner
from Acquisition import aq_parent
from collective import dexteritytextindexer
from datetime import datetime
from datetime import timedelta
from five import grok
from ftw.datepicker.widget import DatePickerFieldWidget
from opengever.base.interfaces import IReferenceNumber
from opengever.base.interfaces import ISequenceNumber
from opengever.base.source import DossierPathSourceBinder
from opengever.globalindex.interfaces import ITaskQuery
from opengever.ogds.base.autocomplete_widget import AutocompleteFieldWidget
from opengever.ogds.base.utils import get_client_id
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.ogds.base.utils import get_current_org_unit
from opengever.ogds.base.utils import ogds_service
from opengever.task import _
from opengever.task import util
from opengever.task.validators import NoCheckedoutDocsValidator
from plone.dexterity.content import Container
from plone.directives import form, dexterity
from plone.indexer.interfaces import IIndexer
from Products.CMFCore.permissions import View
from Products.CMFCore.utils import _mergedLocalRoles
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from z3c.form import validator
from z3c.form.interfaces import HIDDEN_MODE
from z3c.relationfield.schema import RelationChoice
from z3c.relationfield.schema import RelationList
from zope import schema
from zope.app.intid.interfaces import IIntIds
from zope.component import getMultiAdapter
from zope.component import getUtility
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
        vocabulary='opengever.ogds.base.OrgUnitsVocabularyFactory',
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

    @property
    def safe_title(self):
        return safe_unicode(self.title)

    def get_sql_object(self):
        query = getUtility(ITaskQuery)
        return query.get_task(
            getUtility(IIntIds).getId(self), get_current_admin_unit().id())

    def get_breadcrumb_title(self, max_length):
        # Generate and store the breadcrumb tooltip
        breadcrumb_titles = []
        breadcrumbs_view = getMultiAdapter((self, self.REQUEST),
                                           name='breadcrumbs_view')
        for elem in breadcrumbs_view.breadcrumbs():
            breadcrumb_titles.append(safe_unicode(elem.get('Title')))

        # we prevent to raise database-error, if we have a too long string
        # Shorten the breadcrumb_title to: mandant1 > repo1 > ...
        join_value = ' > '
        end_value = '...'

        max_length -= len(end_value)

        breadcrumb_title = breadcrumb_titles
        actual_length = 0

        for i, breadcrumb in enumerate(breadcrumb_titles):
            add_length = len(breadcrumb) + len(join_value) + len(end_value)
            if (actual_length + add_length) > max_length:
                breadcrumb_title = breadcrumb_titles[:i]
                breadcrumb_title.append(end_value)
                break

            actual_length += len(breadcrumb) + len(join_value)
        return join_value.join(breadcrumb_title)

    def get_review_state(self):
        wftool = getToolByName(self, 'portal_workflow')
        return wftool.getInfoFor(self, 'review_state')

    def get_physical_path(self):
        url_tool = self.unrestrictedTraverse('@@plone_tools').url()
        return '/'.join(url_tool.getRelativeContentPath(self))

    def get_is_subtask(self):
        parent = aq_parent(aq_inner(self))
        return parent.portal_type == 'opengever.task.task'

    def get_sequence_number(self):
        return getUtility(ISequenceNumber).get_number(self)

    def get_reference_number(self):
        return IReferenceNumber(self).get_number()

    def get_containing_dossier(self):
        #get the containing_dossier value directly with the indexer
        catalog = getToolByName(self, 'portal_catalog')
        return getMultiAdapter(
            (self, catalog), IIndexer, name='containing_dossier')()

    def get_dossier_sequence_number(self):
        # the dossier_sequence_number index is required for generating lists
        # of tasks as PDFs (LaTeX) as defined by the customer.
        dossier_marker = 'opengever.dossier.behaviors.dossier.IDossierMarker'

        path = self.getPhysicalPath()[:-1]

        portal = getToolByName(self, 'portal_url').getPortalObject()
        portal_path = '/'.join(portal.getPhysicalPath())
        catalog = getToolByName(self, 'portal_catalog')

        while path and '/'.join(path) != portal_path:
            brains = catalog({'path': {'query': '/'.join(path),
                                       'depth': 0},
                              'object_provides': dossier_marker})

            if len(brains):
                if brains[0].sequence_number:
                    return brains[0].sequence_number
                else:
                    return ''
            else:
                path = path[:-1]

        return ''

    def get_predecessor_ids(self):
        if self.predecessor:
            return self.predecessor.split(':', 1)
        else:
            return (None, None,)

    def get_principals(self):
        # index the principal which have View permission. This is according to the
        # allowedRolesAndUsers index but it does not car of global roles.
        allowed_roles = rolesForPermissionOn(View, self)
        principals = []
        for principal, roles in _mergedLocalRoles(self).items():
            for role in roles:
                if role in allowed_roles:
                    principals.append(safe_unicode(principal))
                    break
        return principals


@form.default_value(field=ITask['deadline'])
def deadlineDefaultValue(data):
    # To get hold of the folder, do: context = data.context
    return datetime.today() + timedelta(5)


@form.default_value(field=ITask['responsible_client'])
def responsible_client_default_value(data):
    return get_current_org_unit().id()


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
        # of the responsible field if there is only one orgunit configured.
        if not ogds_service().has_multiple_org_units():
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
        if not ogds_service().has_multiple_org_units():
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
