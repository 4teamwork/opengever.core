from AccessControl.PermissionRole import rolesForPermissionOn
from Acquisition import aq_base
from Acquisition import aq_inner
from Acquisition import aq_parent
from collective import dexteritytextindexer
from datetime import date
from DateTime import DateTime
from ftw.datepicker.widget import DatePickerFieldWidget
from ftw.keywordwidget.widget import KeywordFieldWidget
from ftw.tabbedview.interfaces import ITabbedviewUploadable
from opengever.base.interfaces import IReferenceNumber
from opengever.base.interfaces import ISequenceNumber
from opengever.base.oguid import Oguid
from opengever.base.response import IResponseSupported
from opengever.base.security import as_internal_workflow_transition
from opengever.base.security import elevated_privileges
from opengever.base.source import DossierPathSourceBinder
from opengever.base.utils import get_date_with_delta_excluding_weekends
from opengever.dossier.utils import get_containing_dossier
from opengever.dossier.utils import get_main_dossier
from opengever.globalindex.model.task import Task as TaskModel
from opengever.ogds.base.actor import Actor
from opengever.ogds.base.actor import ActorLookup
from opengever.ogds.base.sources import AllUsersAndGroupsSourceBinder
from opengever.ogds.base.sources import AllUsersInboxesAndTeamsSourceBinder
from opengever.ogds.base.sources import UsersContactsInboxesSourceBinder
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.ogds.base.utils import get_current_org_unit
from opengever.ogds.models.service import ogds_service
from opengever.task import _
from opengever.task import FINAL_TASK_STATES
from opengever.task import is_optional_task_permissions_revoking_enabled
from opengever.task import is_private_task_feature_enabled
from opengever.task import TASK_STATE_IN_PROGRESS
from opengever.task import TASK_STATE_OPEN
from opengever.task import TASK_STATE_PLANNED
from opengever.task import TASK_STATE_REJECTED
from opengever.task import TASK_STATE_RESOLVED
from opengever.task import TASK_STATE_SKIPPED
from opengever.task import util
from opengever.task.interfaces import ITaskSettings
from opengever.task.reminder.reminder import TaskReminderSupport
from opengever.task.validators import NoCheckedoutDocsValidator
from opengever.tasktemplates.interfaces import IContainParallelProcess
from opengever.tasktemplates.interfaces import IContainProcess
from opengever.tasktemplates.interfaces import IContainSequentialProcess
from opengever.tasktemplates.interfaces import IFromTasktemplateGenerated
from opengever.tasktemplates.interfaces import IPartOfSequentialProcess
from persistent.dict import PersistentDict
from persistent.list import PersistentList
from plone import api
from plone.api.exc import InvalidParameterError
from plone.app.textfield import RichText
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
from zope.i18n import translate
from zope.interface import alsoProvides
from zope.interface import implements
from zope.interface import Invalid
from zope.interface import invariant
from zope.schema.vocabulary import getVocabularyRegistry


_marker = object()
TASKTEMPLATE_PREDECESSOR_KEY = 'tasktemplate_predecessor'
TASK_PROCESS_ORDER_KEY = 'task_process_order'
TASK_FORMER_RESPONSIBLES_KEY = 'task_former_responsibles'

TASK_TYPE_APPROVAL = 'approval'


def deadline_default():
    offset = api.portal.get_registry_record(
        'deadline_timedelta',
        interface=ITaskSettings,
    )

    return get_date_with_delta_excluding_weekends(date.today(), offset)


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
            u'informed_principals',
            u'is_private',
            u'revoke_permissions',
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

    form.widget(
        'informed_principals',
        KeywordFieldWidget,
        async=True,
        template_selection='usersAndGroups',
        template_result='usersAndGroups',
    )

    informed_principals = schema.List(
        title=_(u"label_informed_principals", default=u"Info at"),
        description=_(u"help_informed_principals", default=u""),
        value_type=schema.Choice(
            source=AllUsersAndGroupsSourceBinder(),
        ),
        required=False,
        missing_value=[],
        default=[]
    )

    form.widget(deadline=DatePickerFieldWidget)

    is_private = schema.Bool(
        title=_(u"label_is_private", default=u"Private task"),
        description=_(u"help_is_private",
                      default="Deactivates the inbox-group permission."),
        default=False,
    )

    form.mode(IEditForm, is_private=HIDDEN_MODE)

    revoke_permissions = schema.Bool(
        title=_(u"label_revoke_permissions",
                default=u"Revoke permissions."),
        description=_(u"help_revoke_permissions",
                      default="Revoke permissions when closing or reassigning task."),
        default=True,
        required=False,
    )

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
    text = RichText(
        title=_(u'label_text', default='Text'),
        description=_(u"help_text", default=u""),
        required=False,
        default_mime_type='text/html',
        output_mime_type='text/x-html-safe')

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

    @invariant
    def private_task_is_not_changed_when_disabled(data):
        if not is_private_task_feature_enabled() and data.is_private:

            # Because the z3c.form.validator.Data object has implemented a
            # getattr fallback, which fetches the value from the context, we
            # need to check if the is_private value was part of the input-data.
            if 'is_private' in data._Data_data___:
                raise Invalid(_(u'error_private_task_feature_is_disabled',
                                default=u'The private task feature is disabled'))

    @invariant
    def revoke_permissions_is_not_changed_when_disabled(data):
        if not is_optional_task_permissions_revoking_enabled():
            # Because the z3c.form.validator.Data object has implemented a
            # getattr fallback, which fetches the value from the context, we
            # need to check if the revoke_permissions value was part of the input-data.
            if 'revoke_permissions' in data._Data_data___ and not data.revoke_permissions:
                raise Invalid(_(u'error_revoke_permissions_feature_is_disabled',
                                default=u'The revoke permissions feature is disabled'))


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


class Task(Container, TaskReminderSupport):
    """Provide a container for tasks."""

    implements(ITask, ITabbedviewUploadable, IResponseSupported)

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
        return current_state in ['task-state-open',
                                 'task-state-in-progress',
                                 'task-state-planned',
                                 'task-state-resolved']

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
    def is_part_of_sequential_process(self):
        """If the task has been generated by triggering a tasktemplatefolder.
        """
        return IPartOfSequentialProcess.providedBy(self)

    def is_sequential_main_task(self):
        """If the task is the main task of a sequential process.
        """
        return IContainSequentialProcess.providedBy(self)

    def is_approval_task(self):
        return self.task_type == TASK_TYPE_APPROVAL

    @property
    def is_in_final_state(self):
        current_state = api.content.get_state(self)
        return current_state in FINAL_TASK_STATES

    def is_open(self):
        return api.content.get_state(self) in TaskModel.OPEN_STATES

    def is_pending(self):
        return api.content.get_state(self) in TaskModel.PENDING_STATES

    def get_issuer_label(self):
        return self.get_sql_object().get_issuer_label()

    def get_responsible_actor(self):
        return Actor.lookup(self.responsible)

    def is_current_user_responsible(self):
        """Checks if the current user is the responsible itself or it belongs
        to representive group."""
        representatives = Actor.lookup(self.responsible).representatives()
        current_user_id = api.user.get_current().id
        return current_user_id in [user.userid for user in representatives]

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
        """Returns the first parent dossier or inbox"""
        return get_containing_dossier(self)

    def get_main_dossier(self):
        """Returns the main dossier or inbox"""
        return get_main_dossier(self)

    def get_containing_dossier_title(self):
        """Title of the main dossier or inbox"""
        # get the containing_dossier value directly with the indexer
        adapter = getMultiAdapter(
            (self, getToolByName(self, 'portal_catalog')),
            IIndexer, name='containing_dossier',
        )

        return adapter()

    def get_containing_subdossier(self):
        """Title of the containing subdossier or empty string if it is
        contained directly in a dossier"""
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

    def get_former_responsibles(self, create_if_missing=False):
        annotations = IAnnotations(self)
        if create_if_missing and TASK_FORMER_RESPONSIBLES_KEY not in annotations:
            annotations[TASK_FORMER_RESPONSIBLES_KEY] = PersistentList()

        return annotations.get(TASK_FORMER_RESPONSIBLES_KEY, [])

    def add_former_responsible(self, respoonsible_id):
        responsibles = self.get_former_responsibles(create_if_missing=True)
        if respoonsible_id not in responsibles:
            responsibles.append(respoonsible_id)

    def reset_former_responsibles(self):
        IAnnotations(self)[TASK_FORMER_RESPONSIBLES_KEY] = PersistentList()

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
            subtask.cancel_subtasks()

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
            task.reindexObject(idxs=['UID', 'getObjPositionInParent'])
            task.sync()

    def get_tasktemplate_order(self):
        annotations = IAnnotations(self)
        if annotations:
            return annotations.get(TASK_PROCESS_ORDER_KEY)

    def add_task_to_tasktemplate_order(self, position, task):
        alsoProvides(task, IPartOfSequentialProcess)
        subtasks = self.get_tasktemplate_order()
        subtasks.insert(position, Oguid.for_object(task))

        self.set_tasktemplate_order(
            [oguid.resolve_object() for oguid in subtasks])

    def get_tasktemplate_predecessor(self):
        if not self.is_part_of_sequential_process:
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
        next_task = self.get_next_planned_task()

        if not next_task:
            return

        # There is no guarantee that the current user has any permissions
        # on next task, we therefore need to use elevated_privileges here.
        with elevated_privileges():
            next_task._open_planned_task()
            next_task.start_subprocess()

    def _open_planned_task(self):
        if api.content.get_state(self) != 'task-state-planned':
            return

        with as_internal_workflow_transition():
            api.content.transition(
                obj=self, transition='task-transition-planned-open')

        self.sync()

    def _set_in_progress(self):
        if api.content.get_state(self) != 'task-state-open':
            return

        with as_internal_workflow_transition():
            api.content.transition(
                obj=self, transition='task-transition-open-in-progress')

        self.sync()

    def start_subprocess(self):
        self._start_subprocess(self)

    def _start_subprocess(self, obj):
        if not IContainProcess.providedBy(obj):
            return

        obj._open_planned_task()
        obj._set_in_progress()
        for subtask in self._get_subtasks_to_start(obj):
            subtask._open_planned_task()
            subtask.start_subprocess()

    def _get_subtasks_to_start(self, obj):
        if IContainParallelProcess.providedBy(obj):
            for child in obj.objectValues():
                if ITask.providedBy(child):
                    yield child

                    for subchild in self._get_subtasks_to_start(child):
                        yield subchild

        elif IContainSequentialProcess.providedBy(obj):
            for child in obj.objectValues():
                if ITask.providedBy(child):
                    yield child

                    for subchild in self._get_subtasks_to_start(child):
                        yield subchild

                    # start only the first task if sequential
                    break

    def close_main_task(self):
        parent = aq_parent(aq_inner(self))
        if not parent:
            return
        with elevated_privileges():
            if api.content.get_state(parent) != 'task-state-in-progress':
                return

            api.content.transition(
                obj=parent, transition='task-transition-in-progress-tested-and-closed')

    def maybe_start_parent_task(self):
        with elevated_privileges():
            parent = aq_parent(aq_inner(self))
            if not parent:
                return

            if api.content.get_state(parent) != 'task-state-open':
                return

            parent._set_in_progress()

    def get_next_planned_task(self):
        next_task = self.get_sql_object().get_next_task()
        if not next_task:
            return

        next_task = next_task.oguid.resolve_object()
        if api.content.get_state(obj=next_task) == TASK_STATE_SKIPPED:
            return next_task.get_next_planned_task()

        if api.content.get_state(obj=next_task) == TASK_STATE_PLANNED:
            return next_task

        return None

    def may_be_started(self):
        """Whether a sequential task may be started.
        (Transitioned from 'planned' to 'open')
        """
        if not self.is_part_of_sequential_process:
            return False

        parent_state = api.content.get_state(aq_parent(aq_inner(self)))
        if parent_state != TASK_STATE_IN_PROGRESS:
            return False

        return self.all_predecessors_are_skipped()

    def all_predecessors_are_skipped(self):
        return self.get_sql_object().all_predecessors_are_skipped()

    def sync(self):
        """Syncs the corresponding SQL task (globalindex).
        """
        return self.get_sql_object().sync_with(self)

    def sync_reminders(self):
        """Syncs the corresponding SQL task (globalindex).
        """
        return self.get_sql_object().sync_reminders(self)

    def set_to_planned_state(self):
        """Syncs the corresponding SQL task (globalindex).
        """
        with as_internal_workflow_transition():
            api.content.transition(
                obj=self, transition='task-transition-open-planned')
            self.sync()

    def task_documents(self):
        """Returns contained documents and related documents."""
        def _get_documents():
            """Return documents in this task and subtasks."""
            documents = getToolByName(self, 'portal_catalog')(
                portal_type=['opengever.document.document', 'ftw.mail.mail', ],
                path=dict(
                    depth=2,
                    query='/'.join(self.getPhysicalPath())),
            )
            return [document.getObject() for document in documents]

        def _get_related_documents():
            """Return related documents in this task."""
            # Related documents
            related_documents = []

            for item in self.relatedItems:
                obj = item.to_object

                if obj.portal_type in [
                        'opengever.document.document',
                        'ftw.mail.mail',
                ]:
                    obj._v__is_relation = True
                    related_documents.append(obj)

            return related_documents

        return _get_documents() + _get_related_documents()

    def _fix_review_state_mismatch(self):
        """Check if there is a review_state mismatch between the predecessor
        and successor pair and fix it.

        Returns true if there was a mismatch to fix.
        """
        sql_task = self.get_sql_object()

        # predecessor
        if sql_task.has_remote_predecessor:
            if sql_task.predecessor.review_state != sql_task.review_state:
                self._set_review_state(sql_task.predecessor.review_state)
                return True

        if sql_task.has_remote_successor:
            # When having a remote successor there can only be one predecessor,
            # so it's safe to get the state from the first one
            if sql_task.successors[0].review_state != sql_task.review_state:
                self._set_review_state(sql_task.successors[0].review_state)
                return True

        return False

    def _set_review_state(self, review_state):
        wftool = api.portal.get_tool('portal_workflow')
        wf_id = wftool.getWorkflowsFor(self)[0].id
        wftool.setStatusOf(wf_id, self,
                           {'review_state': review_state,
                            'action': review_state,
                            'actor': 'zopemaster',
                            'time': DateTime(),
                            'comments': 'Review state mismatch synchronisation'})
        wftool.getWorkflowsFor(self)[0].updateRoleMappingsFor(self)

        self.sync()
        self.reindexObject()

    def force_finish_task(self):
        """This method is used to forcefully close a task, including all its subtasks,
        when a dossier is being closed and active tasks still exist.

        The need for this method arises from a business requirement where dossiers
        must be allowed to close even if some of their tasks are still open or in progress.
        Rather than preventing the dossier from closing, we force each task into a
        valid terminal state based on its current state.

        This method is recursive, ensuring that all subtasks are also finished in the same way,
        """
        if api.content.get_state(self) == TASK_STATE_REJECTED:
            api.content.transition(obj=self, transition='task-transition-rejected-open')

        if api.content.get_state(self) == TASK_STATE_OPEN:
            api.content.transition(obj=self, transition='task-transition-open-cancelled')
            # Cancel a task will automatically cancel all subtasks.
            return

        for subtask in self.objectValues():
            if ITask.providedBy(subtask):
                subtask.force_finish_task()

        if api.content.get_state(self) == TASK_STATE_IN_PROGRESS:
            # Depending on the task type, some transitions are not possible. We
            # do not try to understand the businesslogic here and naivily do
            # the expected transitions.
            try:
                # We first try to directly close it.
                api.content.transition(obj=self, transition='task-transition-resolved-tested-and-closed')
            except InvalidParameterError:
                # If it does not work, we try to resolve it first.
                api.content.transition(obj=self, transition='task-transition-in-progress-resolved')

        if api.content.get_state(self) == TASK_STATE_RESOLVED:
            api.content.transition(obj=self, transition='task-transition-resolved-tested-and-closed')


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
