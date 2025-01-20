from datetime import date
from DateTime import DateTime as ZopeDateTime
from opengever.base.exceptions import InvalidOguidIntIdPart
from opengever.base.model import Base
from opengever.base.model import create_session
from opengever.base.model import is_oracle
from opengever.base.model import Session
from opengever.base.model import UNIT_ID_LENGTH
from opengever.base.model import USER_ID_LENGTH
from opengever.base.model import WORKFLOW_STATE_LENGTH
from opengever.base.oguid import Oguid
from opengever.base.query import BaseQuery
from opengever.base.types import UnicodeCoercingText
from opengever.base.utils import escape_html
from opengever.globalindex.model.reminder_settings import ReminderSetting
from opengever.inbox import FINAL_FORWARDING_STATES
from opengever.inbox import FORWARDING_TASK_TYPE_ID
from opengever.ogds.base.actor import Actor
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.ogds.models.service import ogds_service
from opengever.task import FINAL_TASK_STATES
from plone import api
from Products.CMFPlone.utils import safe_unicode
from sqlalchemy import and_
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import Date
from sqlalchemy import DateTime
from sqlalchemy import event
from sqlalchemy import ForeignKey
from sqlalchemy import func
from sqlalchemy import Index
from sqlalchemy import Integer
from sqlalchemy import literal
from sqlalchemy import or_
from sqlalchemy import String
from sqlalchemy import UniqueConstraint
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import backref
from sqlalchemy.orm import composite
from sqlalchemy.orm import relation
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Sequence
from sqlalchemy.sql import functions
from zope.globalrequest import getRequest
from zope.i18n import translate


class Task(Base):
    """docstring for Task"""

    MAX_TITLE_LENGTH = 256
    MAX_DOSSIER_TITLE_LENGTH = 512
    MAX_BREADCRUMB_LENGTH = 512

    OVERDUE_INDEPENDENT_STATES = [
        'task-state-cancelled',
        'task-state-rejected',
        'task-state-tested-and-closed',
        'task-state-resolved',
        'forwarding-state-closed',
    ]

    OPEN_STATES = [
        'task-state-open',
        'forwarding-state-open',
    ]

    PENDING_STATES = [
        'task-state-open',
        'task-state-in-progress',
        'task-state-resolved',
        'task-state-rejected',
        'forwarding-state-open',
        'forwarding-state-refused',
    ]

    __tablename__ = 'tasks'
    __table_args__ = (UniqueConstraint('admin_unit_id', 'int_id'), {})

    task_id = Column("id", Integer, Sequence("task_id_seq"), primary_key=True)

    admin_unit_id = Column(String(UNIT_ID_LENGTH), index=True, nullable=False)
    int_id = Column(Integer, index=True, nullable=False)

    oguid = composite(Oguid, admin_unit_id, int_id)

    title = Column(String(MAX_TITLE_LENGTH))
    text = Column(UnicodeCoercingText())
    breadcrumb_title = Column(String(MAX_BREADCRUMB_LENGTH))
    physical_path = Column(UnicodeCoercingText)
    review_state = Column(String(WORKFLOW_STATE_LENGTH))
    icon = Column(String(50))

    responsible = Column(String(USER_ID_LENGTH), index=True)
    issuer = Column(String(USER_ID_LENGTH), index=True)
    is_private = Column(Boolean(), default=False)

    task_type = Column(String(50), index=True)
    is_subtask = Column(Boolean(), default=False)

    reference_number = Column(String(100))
    sequence_number = Column(Integer, index=True, nullable=False)
    dossier_sequence_number = Column(Integer, index=True)
    containing_dossier = Column(String(MAX_DOSSIER_TITLE_LENGTH))
    containing_subdossier = Column(String(MAX_DOSSIER_TITLE_LENGTH))

    created = Column(DateTime, default=functions.now())
    modified = Column(DateTime)
    deadline = Column(Date)
    completed = Column(Date)

    # XXX shit, this should be ...org_unit_ID
    issuing_org_unit = Column(
        String(UNIT_ID_LENGTH),
        index=True,
        nullable=False,
    )

    assigned_org_unit = Column(
        String(UNIT_ID_LENGTH),
        index=True,
        nullable=False,
    )

    predecessor_id = Column(Integer, ForeignKey('tasks.id'), index=True)
    successors = relationship(
        "Task",
        foreign_keys=[predecessor_id],
        backref=backref('predecessor', remote_side=task_id),
        cascade="delete",
    )

    tasktemplate_predecessor_id = Column(Integer, ForeignKey('tasks.id'))
    tasktemplate_successor = relationship(
        "Task",
        foreign_keys=[tasktemplate_predecessor_id],
        backref=backref('tasktemplate_predecessor', remote_side=task_id),
        cascade="delete",
        uselist=False
    )

    _principals = relation(
        'TaskPrincipal',
        backref='task',
        cascade='all, delete-orphan',
    )

    principals = association_proxy('_principals', 'principal')

    def __init__(self, int_id, admin_unit_id, **kwargs):
        super(Task, self).__init__(**kwargs)
        self.admin_unit_id = admin_unit_id
        self.int_id = int_id
        self.predecessor = None

    def __repr__(self):
        return "<Task %s@%s>" % (self.int_id, self.admin_unit_id)

    @property
    def id(self):
        return self.task_id

    def is_open(self):
        return self.review_state in self.OPEN_STATES

    @property
    def is_completed(self):
        return self.review_state in FINAL_TASK_STATES \
            or self.review_state in FINAL_FORWARDING_STATES

    @property
    def issuer_actor(self):
        return Actor.lookup(self.issuer)

    @property
    def responsible_actor(self):
        return Actor.lookup(self.responsible)

    @property
    def is_successor(self):
        return bool(self.predecessor)

    @property
    def issuing_org_unit_label(self):
        return self.get_issuing_org_unit().label()

    @property
    def content_type(self):
        """Figure out a tasks content type from the task_type column.

        We don't store the content type in globalindex but task_type is
        distinct and we can use it to figure out the content type.
        """
        if self.task_type == FORWARDING_TASK_TYPE_ID:
            return 'opengever.inbox.forwarding'
        return 'opengever.task.task'

    def get_admin_unit(self):
        return ogds_service().fetch_admin_unit(self.admin_unit_id)

    def get_issuing_org_unit(self):
        return ogds_service().fetch_org_unit(self.issuing_org_unit)

    def get_assigned_org_unit(self):
        return ogds_service().fetch_org_unit(self.assigned_org_unit)

    def sync_with(self, plone_task, graceful=False):
        """Sync this task instace with its corresponding plone taks."""
        self.title = plone_task.safe_title
        self.text = ""
        if plone_task.text:
            if isinstance(plone_task.text, unicode):
                self.text = plone_task.text
            else:
                self.text = plone_task.text.output
        self.breadcrumb_title = plone_task.get_breadcrumb_title(
            self.MAX_BREADCRUMB_LENGTH,
        )

        self.physical_path = plone_task.get_physical_path()
        self.review_state = plone_task.get_review_state()
        self.icon = plone_task.getIcon()
        self.responsible = plone_task.responsible
        self.is_private = plone_task.is_private
        self.issuer = plone_task.issuer
        self.deadline = plone_task.deadline
        self.completed = plone_task.date_of_completion

        # we need to have python datetime objects for make it work with sqlite
        self.modified = plone_task.modified().asdatetime().replace(tzinfo=None)
        self.task_type = plone_task.task_type
        self.is_subtask = plone_task.get_is_subtask()
        self.sequence_number = plone_task.get_sequence_number()
        self.reference_number = plone_task.get_reference_number()

        self.containing_dossier = self.safe_truncated_string(
            plone_task.get_containing_dossier_title(), self.MAX_DOSSIER_TITLE_LENGTH)

        self.dossier_sequence_number = plone_task.get_dossier_sequence_number()
        self.assigned_org_unit = plone_task.responsible_client
        self.principals = plone_task.get_principals()

        self.predecessor = self.query_predecessor(
            *plone_task.get_predecessor_ids()
        )

        self.containing_subdossier = self.safe_truncated_string(
            plone_task.get_containing_subdossier(), self.MAX_DOSSIER_TITLE_LENGTH)

        try:
            predecessor = plone_task.get_tasktemplate_predecessor()
        except InvalidOguidIntIdPart:
            # When moving a dossier with a task_process it is not guaranteed
            # that the objects are moved in the tasktemplate order, so it can
            # happen, that the predecessor does not yet exists. Because the
            # intid stays the same after move, its safe to not updated the predecessor.
            if not graceful:
                raise

            predecessor = None

        if predecessor:
            self.tasktemplate_predecessor = predecessor.get_sql_object()

        self.sync_reminders(plone_task)

    @staticmethod
    def safe_truncated_string(string, max_length):
        string = safe_unicode(string)
        if string:
            return string[:max_length]
        return string

    @classmethod
    def physical_path_to_char_if_oracle(cls):
        if is_oracle():
            return func.to_char(cls.physical_path)
        return cls.physical_path

    def sync_reminders(self, plone_task):
        reminders = plone_task.get_reminders()

        for sql_setting in self.reminder_settings:

            # If the setting already exists, we only update the deadline
            if sql_setting.actor_id in reminders:
                setting = reminders[sql_setting.actor_id]
                sql_setting.option_type = setting.option_type
                sql_setting.remind_day = setting.calculate_trigger_date(
                    plone_task.deadline)
                reminders.pop(sql_setting.actor_id)

            # delete no longer existing settings
            else:
                self.session.delete(sql_setting)

        # Add new reminder settings
        for actor_id, reminder in reminders.items():
            setting = ReminderSetting(
                task=self, actor_id=actor_id, option_type=reminder.option_type,
                remind_day=reminder.calculate_trigger_date(plone_task.deadline))
            self.session.add(setting)

    # XXX move me to task query
    def query_predecessor(self, admin_unit_id, pred_init_id):
        if not (admin_unit_id or pred_init_id):
            return None

        return Session.query(Task).filter_by(
            admin_unit_id=admin_unit_id, int_id=pred_init_id).first()

    # XXX rename me, this should be get_issuer_link
    def get_issuer_label(self):
        actor = Actor.lookup(self.issuer)
        org_unit = ogds_service().fetch_org_unit(self.issuing_org_unit)
        return org_unit.prefix_label(actor.get_link())

    @property
    def is_forwarding(self):
        return self.task_type == FORWARDING_TASK_TYPE_ID

    @property
    def is_overdue(self):
        if self.deadline < date.today():
            if self.review_state not in Task.OVERDUE_INDEPENDENT_STATES:
                return True

        return False

    # XXX rename me, this should be get_responsible_link
    def get_responsible_label(self, linked=True):
        actor = Actor.lookup(self.responsible)
        org_unit = ogds_service().fetch_org_unit(self.assigned_org_unit)

        if not linked:
            return org_unit.prefix_label(actor.get_label())

        return org_unit.prefix_label(actor.get_link())

    def get_state_label(self):
        return u"<span class=wf-{}>{}</span>".format(
            self.review_state,
            translate(
                self.review_state,
                domain='plone',
                context=api.portal.get().REQUEST,
            ),
        )

    def get_deadline_label(self, fmt="medium"):
        if not self.deadline:
            return u''

        if self.is_overdue:
            label = u'<span class="task-overdue">{}</span>'

        else:
            label = u'<span>{}</span>'

        formatter = getRequest().locale.dates.getFormatter("date", fmt)
        formatted_date = formatter.format(self.deadline)

        return label.format(formatted_date.strip())

    def _date_to_zope_datetime(self, _date):
        if not _date:
            return None

        return ZopeDateTime(_date.year, _date.month, _date.day)

    def get_deadline(self):
        return self._date_to_zope_datetime(self.deadline)

    @property
    def is_remote_task(self):
        """Returns true for tasks, where issuing and responsible
        admin_unit (assign org unit's admin_unit) are not equal.__add__()
        """
        return self.get_assigned_org_unit().admin_unit != self.get_admin_unit()

    @property
    def has_remote_predecessor(self):
        if self.predecessor:
            return self.predecessor.admin_unit_id != self.admin_unit_id
        return False

    @property
    def has_remote_successor(self):
        for successor in self.successors:
            if successor.admin_unit_id != self.admin_unit_id:
                return True
        return False

    @property
    def is_part_of_remote_predecessor_successor_pair(self):
        return self.has_remote_successor or self.has_remote_predecessor

    @property
    def has_sequential_successor(self):
        if self.tasktemplate_successor:
            return True

        # This is the case if `self` is a cross-admin-unit copy of a task
        # in a sequential chain.
        # The next sequential task in the chain on the *other* side then is
        # self.predecessor.tasktemplate_successor
        elif self.predecessor and self.predecessor.tasktemplate_successor:
            return True

        return False

    def get_previous_task(self):
        """If the task is part of a sequence it returns previous task of the
        sequence otherwise None."""

        return self.tasktemplate_predecessor

    def get_next_task(self):
        """If the task is part of a sequence it returns the next task of the
        sequence otherwise None."""

        return self.tasktemplate_successor

    def all_predecessors_are_skipped(self):
        previous_task = self.get_previous_task()
        if not previous_task:
            return True
        if previous_task.review_state != 'task-state-skipped':
            return False
        return previous_task.all_predecessors_are_skipped()

    def adding_a_previous_task_is_possible(self):
        """Check if adding a new task as previous task to the process is possible.
        It checks if the current task is not yet started.
        """
        return self.review_state == 'task-state-planned'

    def get_css_class(self):
        """Returns css_class for the special task icons:

        - Forwarding
        - Regular Task
        - Subtask
        - Remotetask
        """
        if self.is_forwarding:
            css_class = 'contenttype-opengever-inbox-forwarding'

        elif self.is_subtask and self.is_remote_task:
            if self.admin_unit_id == get_current_admin_unit().id():
                css_class = 'contenttype-opengever-task-sub-task'

            else:
                css_class = 'contenttype-opengever-task-remote-task'

        elif self.is_subtask:
            css_class = 'contenttype-opengever-task-sub-task'

        elif self.is_remote_task:
            css_class = 'contenttype-opengever-task-remote-task'

        else:
            css_class = 'contenttype-opengever-task-task'

        return css_class

    def get_completed(self):
        return self._date_to_zope_datetime(self.completed)

    def has_access(self, member):
        if not member:
            return False

        roles = api.user.get_roles(user=member)

        if {'Administrator', 'LimitedAdmin', 'Manager'} & set(roles):
            return True

        principals = set(member.getGroups() + [member.getId()])
        allowed_principals = set(self.principals)

        return len(principals & allowed_principals) > 0

    def absolute_url(self):
        admin_unit = self.get_admin_unit()

        if not admin_unit:
            return ''

        return '/'.join((admin_unit.public_url, self.physical_path))

    def get_link(self, with_state_icon=True, with_responsible_info=True):
        title = escape_html(self.title)
        admin_unit = self.get_admin_unit()

        if not admin_unit:
            return u'<span class="{}">{}</span>'.format(
                self.get_css_class(),
                title,
            )

        url = self.absolute_url()

        breadcrumb_titles = u"[{}] > {}".format(
            admin_unit.title,
            escape_html(self.breadcrumb_title),
        )

        responsible_info = u' <span class="discreet">({})</span>'.format(
            self.get_responsible_label(linked=False),
        )

        link_content = u'<span class="{}">{}</span>'.format(
            self.get_css_class(),
            title,
        )

        # If the target is on a different client we need to make a popup
        if self.admin_unit_id != get_current_admin_unit().id():
            link_target = u' target="_blank"'

        else:
            link_target = u''

        # Render the full link if we have acccess
        if self.has_access(api.user.get_current()):
            link = u'<a href="{}"{} title="{}">{}</a>'.format(
                url,
                link_target,
                breadcrumb_titles,
                link_content,
            )

        else:
            link = link_content

        if with_responsible_info:
            link = u'{} {}'.format(link, responsible_info)

        # wrapped it into span tag
        if with_state_icon:
            link = self._task_state_wrapper(link)

        else:
            link = u'<span>%s</span>' % (link)

        return link

    def _task_state_wrapper(self, text):
        """Wrap a span-tag around the text with the status-css class."""
        return u'<span class="wf-%s">%s</span>' % (self.review_state, text)

    def get_containing_dossier_title(self):
        """containing dossier title encoded as utf-8 to mirror the behavior
        of opengever.task.task.Task"""
        return self.containing_dossier.encode('utf-8')

    def get_containing_subdossier(self):
        """containing subdossier title encoded as utf-8 to mirror the behavior
        of opengever.task.task.Task"""
        return self.containing_subdossier.encode('utf-8')

    def get_main_task(self):
        if not self.is_subtask:
            return None

        query = Task.query.restrict().filter(
            literal(self.physical_path).contains(Task.physical_path))
        query = query.order_by(func.length(Task.physical_path))
        return query.first()

    def get_main_task_title(self):
        main_task = self.get_main_task()
        if main_task:
            return main_task.title


AVOID_DUPLICATES_STRATEGY_LOCAL = 'local'
AVOID_DUPLICATES_STRATEGY_SUCCESSOR_TASK = 'successor_task'
AVOID_DUPLICATES_STRATEGY_PREDECESSOR_TASK = 'predecessor_task'


class TaskQuery(BaseQuery):

    roles_allowed_to_see_tasks = ('Manager', 'Administrator', 'LimitedAdmin', 'Reader')

    def restrict(self):
        member = api.user.get_current()

        # Check for global roles. Global Administrators, Readers and
        # Managers are always able to access a task, so no need to restrict.
        global_roles = set(member.getRoles())
        if not set(self.roles_allowed_to_see_tasks).isdisjoint(global_roles):
            return self

        principals = member.getGroupIds() + [member.getId()]

        # Oracle does not support DISTINCT with SELECTs that have CLOB
        # type columns. But the task model uses CLOB for the physical_path
        # and text column. So we need to use a subquery instead.
        # Because PostgreSQL optimize the subquery too we don't need to avoid
        # the subquery and use the same query for PostgreSQL backends too.
        principal_query = self.session.query(
            TaskPrincipal.task_id).filter(
                TaskPrincipal.principal.in_(principals))
        return self.filter(Task.task_id.in_(principal_query))

    def avoid_duplicates(self, strategy=AVOID_DUPLICATES_STRATEGY_LOCAL):
        """Avoid duplicates and only list one task if a task has a successor.

        Available strategies are:

        local (default):
        If a task has a successor task, list only the task that is on the
        current admin unit. Hence, for tasks with a successor, the query
        will by default only return tasks that are on the local admin unit.

        successor_task:
        If a task has a successor task, always return the successor task

        predecessor_task:
        If a task has a predecessor, always return the predecessor task
        """
        if strategy == AVOID_DUPLICATES_STRATEGY_LOCAL:
            return self.filter(
                or_(
                    and_(Task.predecessor == None, Task.successors == None),  # noqa
                    Task.admin_unit_id == get_current_admin_unit().id()
                )
            )

        if strategy == AVOID_DUPLICATES_STRATEGY_SUCCESSOR_TASK:
            return self.filter(
                or_(
                    and_(Task.predecessor == None, Task.successors == None),  # noqa
                    Task.predecessor != None  # noqa
                )
            )

        elif strategy == AVOID_DUPLICATES_STRATEGY_PREDECESSOR_TASK:
            return self.filter(
                or_(
                    and_(Task.predecessor == None, Task.successors == None),  # noqa
                    Task.successors != None  # noqa
                )
            )

        else:
            raise NotImplementedError()

    def users_tasks(self, userid):
        """Returns query which List all tasks where the given user,
        his userid, is responsible. It queries all admin units.
        """
        return self.restrict().filter(Task.responsible == userid)

    def by_responsibles(self, responsibles):
        return self.restrict().filter(Task.responsible.in_(responsibles))

    def users_issued_tasks(self, userid):
        """Returns query which list all tasks where the given user
        is the issuer. It queries all admin units.
        """
        return self.restrict().filter(Task.issuer == userid)

    def by_assigned_org_unit(self, org_unit):
        """Returns all tasks assigned to the given orgunit."""
        return self.restrict().filter(Task.assigned_org_unit == org_unit.id())

    def by_issuing_org_unit(self, org_unit):
        """Returns all tasks issued by the given orgunit."""
        return self.restrict().filter(Task.issuing_org_unit == org_unit.id())

    def all_issued_tasks(self, admin_unit):
        """List all tasks from the current_admin_unit.
        """
        return self.restrict().filter(Task.admin_unit_id == admin_unit.id())

    by_admin_unit = all_issued_tasks

    def by_intid(self, int_id, admin_unit_id):
        """Returns the task identified by the given int_id and admin_unit_id
        or None
        """
        return self.filter_by(
            admin_unit_id=admin_unit_id, int_id=int_id).first()

    def by_oguid(self, oguid):
        """Returns the task identified by the given int_id and admin_unit_id
        or None
        """
        if isinstance(oguid, basestring):
            oguid = Oguid.parse(oguid)
        return self.filter_by(oguid=oguid).first()

    def by_path(self, path, admin_unit_id):
        """Returns a task on the specified client identified by its physical
        path (which is relative to the site root!) or None.
        """
        query = self.filter_by(admin_unit_id=admin_unit_id)
        return query.filter(Task.physical_path_to_char_if_oracle() == path).first()

    def by_paths(self, paths, admin_unit_id=None):
        """Returns all tasks whos physical_path is listed in `paths`.
        """
        admin_unit_id = admin_unit_id or get_current_admin_unit().id()
        query = self.restrict().filter_by(admin_unit_id=admin_unit_id)
        return query.filter(Task.physical_path_to_char_if_oracle().in_(paths)).all()

    def by_ids(self, task_ids):
        """Returns all tasks whos task_ids are listed in `task_ids`.
        """
        return self.restrict().filter(Task.task_id.in_(task_ids)).all()

    def by_container(self, container, admin_unit):
        url_tool = api.portal.get_tool(name='portal_url')
        path = '/'.join(url_tool.getRelativeContentPath(container))
        path = '{}/'.format(path)

        return self.restrict().by_admin_unit(admin_unit).filter(
            Task.physical_path.startswith(path))

    def by_brain(self, brain):
        relative_content_path = '/'.join(brain.getPath().split('/')[2:])
        query = self.by_admin_unit(get_current_admin_unit())
        return query.filter(
            Task.physical_path_to_char_if_oracle() == relative_content_path).one()

    def subtasks_by_tasks(self, tasks):
        """Queries all subtask of the given tasks sql object."""

        query = self.restrict().filter(
            or_(
                and_(
                    Task.admin_unit_id == task.admin_unit_id,
                    Task.physical_path.startswith(
                        '{}/'.format(task.physical_path)),
                )
                for task in tasks
            )
        )
        return query

    def subtasks_by_task(self, task):
        """Queries all subtask of the given task sql object."""
        return self.subtasks_by_tasks([task])

    def parent_task_for_task(self, task):
        parent_task_path = '/'.join(task.physical_path.split('/')[:-1])
        return self.by_path(parent_task_path, task.admin_unit_id)

    def in_state(self, states):
        return self.filter(Task.review_state.in_(states))

    def in_pending_state(self):
        return self.in_state(Task.PENDING_STATES)


Task.query_cls = TaskQuery


class TaskPrincipal(Base):
    """Define relations for task principals."""

    __tablename__ = 'task_principals'

    principal = Column(String(USER_ID_LENGTH), primary_key=True)

    task_id = Column(
        Integer,
        ForeignKey('tasks.id'),
        primary_key=True,
    )

    def __init__(self, principal):
        self.principal = principal

    def __repr__(self):
        return "<TaskPrincipal %s for %s>" % (self.principal, str(self.task))


@event.listens_for(TaskPrincipal.__table__, 'after_create')
def create_principals_index(target, connection, **kw):
    if is_oracle():
        task_principals_ix = Index(
            'task_principals_ix',
            func.nlssort(TaskPrincipal.principal, 'NLS_SORT=GERMAN_CI'))

        task_principals_ix.create(create_session().bind)


@event.listens_for(Task.__table__, 'after_create')
def create_review_state_index(target, connection, **kw):
    if is_oracle():
        ix_tasks_review_state = Index(
            'ix_tasks_review_state',
            func.nlssort(Task.review_state, 'NLS_SORT=GERMAN_CI'))
        ix_tasks_review_state.create(create_session().bind)
