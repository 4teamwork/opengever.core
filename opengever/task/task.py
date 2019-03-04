from AccessControl.PermissionRole import rolesForPermissionOn
from Acquisition import aq_base
from Acquisition import aq_inner
from Acquisition import aq_parent
from collective import dexteritytextindexer
from datetime import datetime
from datetime import timedelta
from ftw.datepicker.widget import DatePickerFieldWidget
from ftw.keywordwidget.widget import KeywordFieldWidget
from ftw.tabbedview.interfaces import ITabbedviewUploadable
from opengever.base.interfaces import IReferenceNumber
from opengever.base.interfaces import ISequenceNumber
from opengever.base.oguid import Oguid
from opengever.base.security import as_internal_workflow_transition
from opengever.base.source import DossierPathSourceBinder
from opengever.dossier.utils import get_containing_dossier
from opengever.globalindex.model.task import Task as TaskModel
from opengever.ogds.base.actor import Actor
from opengever.ogds.base.actor import ActorLookup
from opengever.ogds.base.sources import AllUsersInboxesAndTeamsSourceBinder
from opengever.ogds.base.sources import UsersContactsInboxesSourceBinder
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.ogds.base.utils import get_current_org_unit
from opengever.ogds.base.utils import ogds_service
from opengever.task import _
from opengever.task import FINAL_TASK_STATES
from opengever.task import TASK_STATE_PLANNED
from opengever.task import util
from opengever.task.interfaces import ITaskSettings
from opengever.task.validators import NoCheckedoutDocsValidator
from opengever.tasktemplates.interfaces import IFromSequentialTasktemplate
from opengever.tasktemplates.interfaces import IFromTasktemplateGenerated
from persistent.dict import PersistentDict
from plone import api
from plone.autoform import directives as form
from plone.dexterity.content import Container
from plone.indexer.interfaces import IIndexer
from plone.supermodel import model
from Products.CMFCore.permissions import View
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser import BrowserView
from z3c.form import validator
from z3c.form import widget
from z3c.form.interfaces import HIDDEN_MODE
from z3c.form.interfaces import IAddForm
from z3c.form.interfaces import IEditForm
from z3c.relationfield.schema import RelationChoice
from z3c.relationfield.schema import RelationList
from zope import schema
from zope.annotation.interfaces import IAnnotations
from zope.app.intid.interfaces import IIntIds
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.globalrequest import getRequest
from zope.i18n import translate
from zope.interface import implements
from zope.schema.vocabulary import getVocabularyRegistry


_marker = object()
TASKTEMPLATE_PREDECESSOR_KEY = 'tasktemplate_predecessor'
TASK_PROCESS_ORDER_KEY = 'task_process_order'


def deadline_default():
    offset = api.portal.get_registry_record(
        'deadline_timedelta',
        interface=ITaskSettings,
        )

    return (datetime.today() + timedelta(days=offset)).date()


class ITask(model.Schema):
    """Define the task schema."""

    model.fieldset(
        u'common',
        label=_(u'fieldset_common', default=u'Common'),
        fields=[
            u'title',
            u'issuer',
            u'task_type',
            u'responsible_client',
            u'responsible',
            u'is_private',
            u'deadline',
            u'text',
            u'relatedItems',
            ],
        )

    model.fieldset(
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
        max_length=256,
        )

    form.widget('issuer', KeywordFieldWidget, async=True)

    issuer = schema.Choice(
        title=_(u"label_issuer", default=u"Issuer"),
        source=UsersContactsInboxesSourceBinder(),
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
        title=_(
            u'label_resonsible_client',
            default=u'Responsible Client',
            ),
        description=_(
            u'help_responsible_client',
            default=u'',
            ),
        vocabulary='opengever.ogds.base.OrgUnitsVocabularyFactory',
        required=True,
        )

    form.widget('responsible', KeywordFieldWidget, async=True)

    responsible = schema.Choice(
        title=_(u"label_responsible", default=u"Responsible"),
        description=_(u"help_responsible", default=""),
        source=AllUsersInboxesAndTeamsSourceBinder(include_teams=True),
        required=True,
        )

    form.widget(deadline=DatePickerFieldWidget)

    is_private = schema.Bool(
        title=_(u"label_is_private", default=u"Private task"),
        description=_(u"help_is_private",
                      default="Deactivates the inbox-group permission."),
        default=False,
        )

    form.mode(IEditForm, is_private=HIDDEN_MODE)

    deadline = schema.Date(
        title=_(u"label_deadline", default=u"Deadline"),
        description=_(u"help_deadline", default=u""),
        required=True,
        defaultFactory=deadline_default,
        )

    form.widget(date_of_completion=DatePickerFieldWidget)
    form.mode(IAddForm, date_of_completion=HIDDEN_MODE)

    date_of_completion = schema.Date(
        title=_(u"label_date_of_completion", default=u"Date of completion"),
        description=_(u"help_date_of_completion", default=u""),
        required=False,
        )

    dexteritytextindexer.searchable('text')
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
                    'review_state': {'not': 'document-state-shadow'},
                    'object_provides': [
                        'opengever.dossier.behaviors.dossier.IDossierMarker',
                        'opengever.document.document.IDocumentSchema',
                        'opengever.task.task.ITask',
                        'ftw.mail.mail.IMail',
                        'opengever.meeting.proposal.IProposal',
                        ],
                    },
                ),
            ),
        required=False,
        )

    form.widget(expectedStartOfWork=DatePickerFieldWidget)

    expectedStartOfWork = schema.Date(
        title=_(u"label_expectedStartOfWork", default="Start with work"),
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
        required=False)


validator.WidgetValidatorDiscriminators(
    NoCheckedoutDocsValidator,
    field=ITask['relatedItems'],
    )


default_responsible_client = widget.ComputedWidgetAttribute(
    lambda adapter: get_current_org_unit().id(),
    field=ITask['responsible_client'],
    )


class IAddTaskSchema(ITask):
    """Define a schema for adding tasks."""
    form.widget('responsible', KeywordFieldWidget, async=True)

    model.fieldset(
        u'additional',
        fields=[u'tasktemplate_position'],
    )

    form.widget(
        'responsible',
        KeywordFieldWidget,
        async=True,
        template_selection='usersAndGroups',
        template_result='usersAndGroups',
    )

    responsible = schema.List(
        title=_(u"label_responsible", default=u"Responsible"),
        description=_(u"help_responsible", default=""),
        value_type=schema.Choice(
            source=AllUsersInboxesAndTeamsSourceBinder(include_teams=True),
            ),
        required=True,
        missing_value=[],
        default=[]
        )

    tasktemplate_position = schema.Int(
        title=_(u"label_tasktemplate_position",
                default=u"Tasktemplate Position"),
        required=False,
    )


class Task(Container):
    """Provide a container for tasks."""

    implements(ITask, ITabbedviewUploadable)

    def __init__(self, *args, **kwargs):
        super(Task, self).__init__(*args, **kwargs)

    @property
    def zipexport_title(self):
        translated_taskname = translate(_(u'Task', default=u'Task'), context=api.portal.get().REQUEST)
        return u' - '.join((translated_taskname, self.Title().decode('utf-8'), ))

    @property
    def sequence_number(self):
        return self._sequence_number

    @property
    def task_type_category(self):
        for category in [
                'unidirectional_by_reference',
                'unidirectional_by_value',
                'bidirectional_by_reference',
                'bidirectional_by_value'
            ]:
            voc = getVocabularyRegistry().get(
                self,
                ''.join(('opengever.task.', category,)),
                )

            if self.task_type in voc:
                return category

        return None

    @property
    def int_id(self):
        return getUtility(IIntIds).getId(self)

    @property
    def oguid(self):
        return Oguid(get_current_admin_unit().id(), self.int_id)

    @property
    def is_editable(self):
        current_state = api.content.get_state(self)
        return current_state in ['task-state-open', 'task-state-in-progress']

    @property
    def is_team_task(self):
        """Is true if the task responsible is a team."""
        return ActorLookup(self.responsible).is_team()

    @property
    def is_from_tasktemplate(self):
        """If the task has been generated by triggering a tasktemplatefolder.
        """
        return IFromTasktemplateGenerated.providedBy(self)

    @property
    def is_from_sequential_tasktemplate(self):
        """If the task has been generated by triggering a tasktemplatefolder.
        """
        return IFromSequentialTasktemplate.providedBy(self)

    @property
    def is_in_final_state(self):
        current_state = api.content.get_state(self)
        return current_state in FINAL_TASK_STATES

    def is_open(self):
        return api.content.get_state(self) in TaskModel.OPEN_STATES

    def get_issuer_label(self):
        return self.get_sql_object().get_issuer_label()

    def get_responsible_actor(self):
        return Actor.lookup(self.responsible)

    def get_issuer_actor(self):
        return Actor.lookup(self.issuer)

    def get_responsible_org_unit(self):
        return ogds_service().fetch_org_unit(self.responsible_client)

    def get_responsible_admin_unit(self):
        return self.get_responsible_org_unit().admin_unit

    def get_sql_object(self):
        return TaskModel.query.by_intid(
            self.int_id,
            get_current_admin_unit().id(),
            )

    @property
    def safe_title(self):
        return safe_unicode(self.title)

    def get_breadcrumb_title(self, max_length):
        # Generate and store the breadcrumb tooltip
        breadcrumb_titles = []
        breadcrumbs_view = getMultiAdapter(
            (self, self.REQUEST),
            name='breadcrumbs_view',
            )

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
        url_tool = api.portal.get_tool(name='portal_url')
        return '/'.join(url_tool.getRelativeContentPath(self))

    def get_is_subtask(self):
        parent = aq_parent(aq_inner(self))
        return parent.portal_type == 'opengever.task.task'

    def get_sequence_number(self):
        return getUtility(ISequenceNumber).get_number(self)

    def get_reference_number(self):
        return IReferenceNumber(self).get_number()

    def get_containing_dossier(self):
        return get_containing_dossier(self)

    def get_containing_dossier_title(self):
        # get the containing_dossier value directly with the indexer
        adapter = getMultiAdapter(
            (self, getToolByName(self, 'portal_catalog')),
            IIndexer, name='containing_dossier',
            )

        return adapter()

    def get_containing_subdossier(self):
        # get the containing_dossier value directly with the indexer
        adapter = getMultiAdapter(
            (self, getToolByName(self, 'portal_catalog')),
            IIndexer, name='containing_subdossier',
            )

        return adapter()

    def get_dossier_sequence_number(self):
        dossier = self.get_containing_dossier()

        if dossier:
            return dossier.get_sequence_number()

        return None

    def get_predecessor_ids(self):
        if self.predecessor:
            return self.predecessor.split(':', 1)

        return (None, None,)

    def get_principals(self):
        # index the principal which have View permission. This is according to
        # the allowedRolesAndUsers index but it does not car of global roles.
        allowed_roles = rolesForPermissionOn(View, self)
        return list(self._get_principals_for_roles(allowed_roles))

    def _get_principals_for_roles(self, allowed_roles):
        principals = set()
        parent = self

        while parent and not IPloneSiteRoot.providedBy(parent):
            for principal, roles in parent.get_local_roles():
                for role in roles:
                    if role in allowed_roles:
                        principals.add(safe_unicode(principal))

            # local roles inheritance blocked
            if getattr(aq_base(parent), '__ac_local_roles_block__', False):
                break

            parent = aq_parent(aq_inner(parent))

        return principals

    def get_task_type_label(self, language=None):
        # XXX: vocabulary is a contextsourcebinder, we cannot move it to
        # globalindex.Task for now.
        if not self.task_type:
            return ''

        if language:
            return util.get_task_type_title(self.task_type, language)

        vocabulary = util.getTaskTypeVocabulary(self)
        term = vocabulary.getTerm(self.task_type)

        return term.title

    def cancel_subtasks(self):
        for subtask in self.objectValues():
            if not ITask.providedBy(subtask):
                continue

            wftool = api.portal.get_tool('portal_workflow')
            workflow_id = wftool.getChainFor(subtask)[0]
            wftool.setStatusOf(
                workflow_id, subtask,
                {'review_state': 'task-state-cancelled',
                 'action': 'Main task cancelled',
                 'actor': api.user.get_current().getId()})

            workflow = wftool.getWorkflowById(workflow_id)
            workflow.updateRoleMappingsFor(subtask)
            subtask.reindexObject()
            subtask.get_sql_object().sync_with(subtask)

    def set_tasktemplate_order(self, subtasks):
        """Stores the order from the given list subtasks, as process order
        for the given task list.
        """
        annotations = IAnnotations(self)
        if not annotations:
            annotations = PersistentDict()

        oguids = [Oguid.for_object(task) for task in subtasks]
        annotations[TASK_PROCESS_ORDER_KEY] = oguids

        for task in subtasks:
            task.sync()

    def get_tasktemplate_order(self):
        annotations = IAnnotations(self)
        if annotations:
            return annotations.get(TASK_PROCESS_ORDER_KEY)

    def add_task_to_tasktemplate_order(self, position, task):
        subtasks = self.get_tasktemplate_order()
        subtasks.insert(position, Oguid.for_object(task))

        self.set_tasktemplate_order(
            [oguid.resolve_object() for oguid in subtasks])

    def get_tasktemplate_predecessor(self):
        if not self.is_from_sequential_tasktemplate:
            return

        if not self.get_is_subtask():
            return

        parent = aq_parent(aq_inner(self))
        order = parent.get_tasktemplate_order()
        if not order:
            return

        current_oguid = Oguid.for_object(self)
        position = order.index(current_oguid) - 1
        if position < 0:
            return

        return order[position].resolve_object()

    def open_next_task(self):
        next_task = self.get_sql_object().get_next_task()
        if not next_task:
            return

        next_task = next_task.oguid.resolve_object()
        if api.content.get_state(obj=next_task) == TASK_STATE_PLANNED:
            with as_internal_workflow_transition():
                api.content.transition(
                    obj=next_task, transition='task-transition-planned-open')

            next_task.sync()

    def sync(self):
        """Syncs the corresponding SQL task (globalindex).
        """
        return self.get_sql_object().sync_with(self)

    def set_to_planned_state(self):
        """Syncs the corresponding SQL task (globalindex).
        """
        with as_internal_workflow_transition():
            api.content.transition(
                obj=self, transition='task-transition-open-planned')
            self.sync()


def related_document(context):
    intids = getUtility(IIntIds)
    return intids.getId(context)


class DocumentRedirector(BrowserView):
    """Redirector View specific for documents created on a task
    redirect directly to the relateddocuments tab
    instead of the default documents tab
    """

    def __call__(self):
        referer = self.context.REQUEST.environ.get('HTTP_REFERER')
        if referer.endswith('++add++opengever.document.document'):
            return self.context.REQUEST.RESPONSE.redirect(
                '#'.join((self.context.absolute_url(), 'relateddocuments', )),
                )

        return self.context.REQUEST.RESPONSE.redirect(
            self.context.absolute_url(),
            )
