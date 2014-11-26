from datetime import date
from DateTime import DateTime as ZopeDateTime
from opengever.base.oguid import Oguid
from opengever.core.model import Base
from opengever.core.model import Session
from opengever.globalindex.model.query import TaskQuery
from opengever.ogds.base.actor import Actor
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.ogds.base.utils import ogds_service
from plone import api
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import Date
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import UniqueConstraint
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import backref
from sqlalchemy.orm import composite
from sqlalchemy.orm import relation
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Sequence
from sqlalchemy.sql import functions
from zope.i18n import translate


class Task(Base):
    """docstring for Task"""

    query_cls = TaskQuery

    MAX_TITLE_LENGTH = 256
    MAX_BREADCRUMB_LENGTH = 512

    OVERDUE_INDEPENDENT_STATES = ['task-state-cancelled',
                                  'task-state-rejected',
                                  'task-state-tested-and-closed',
                                  'forwarding-state-closed']

    __tablename__ = 'tasks'
    __table_args__ = (UniqueConstraint('admin_unit_id', 'int_id'), {})

    task_id = Column("id", Integer, Sequence("task_id_seq"), primary_key=True)

    admin_unit_id = Column(String(30), index=True, nullable=False)
    int_id = Column(Integer, index=True, nullable=False)

    oguid = composite(Oguid, admin_unit_id, int_id)

    title = Column(String(MAX_TITLE_LENGTH))
    text = Column(Text)
    breadcrumb_title = Column(String(MAX_BREADCRUMB_LENGTH))
    physical_path = Column(String(256))
    review_state = Column(String(50))
    icon = Column(String(50))

    responsible = Column(String(32), index=True)
    issuer = Column(String(32), index=True)

    task_type = Column(String(50), index=True)
    is_subtask = Column(Boolean(), default=False)

    reference_number = Column(String(100))
    sequence_number = Column(Integer, index=True, nullable=False)
    dossier_sequence_number = Column(Integer, index=True)
    containing_dossier = Column(String(512))
    containing_subdossier = Column(String(512))

    created = Column(DateTime, default=functions.now())
    modified = Column(DateTime)
    deadline = Column(Date)
    completed = Column(Date)

    # XXX shit, this should be ...org_unit_ID
    issuing_org_unit = Column(String(30), index=True, nullable=False)
    assigned_org_unit = Column(String(30), index=True, nullable=False)

    predecessor_id = Column(Integer, ForeignKey('tasks.id'))
    successors = relationship(
        "Task",
        backref=backref('predecessor', remote_side=task_id),
        cascade="delete")

    _principals = relation('TaskPrincipal', backref='task',
                           cascade='all, delete-orphan')
    principals = association_proxy('_principals', 'principal')

    def __init__(self, int_id, admin_unit_id, **kwargs):
        super(Task, self).__init__(**kwargs)
        self.admin_unit_id = admin_unit_id
        self.int_id = int_id

    def __repr__(self):
        return "<Task %s@%s>" % (self.int_id, self.admin_unit_id)

    @property
    def id(self):
        return self.task_id

    @property
    def issuer_actor(self):
        return Actor.lookup(self.issuer)

    @property
    def responsible_actor(self):
        return Actor.lookup(self.responsible)

    def get_admin_unit(self):
        return ogds_service().fetch_admin_unit(self.admin_unit_id)

    def get_issuing_org_unit(self):
        return ogds_service().fetch_org_unit(self.issuing_org_unit)

    def get_assigned_org_unit(self):
        return ogds_service().fetch_org_unit(self.assigned_org_unit)

    def sync_with(self, plone_task):
        """Sync this task instace with its corresponding plone taks.

        """
        self.title = plone_task.safe_title
        self.text = plone_task.text
        self.breadcrumb_title = plone_task.get_breadcrumb_title(
            self.MAX_BREADCRUMB_LENGTH)
        self.physical_path = plone_task.get_physical_path()
        self.review_state = plone_task.get_review_state()
        self.icon = plone_task.getIcon()
        self.responsible = plone_task.responsible
        self.issuer = plone_task.issuer
        self.deadline = plone_task.deadline
        self.completed = plone_task.date_of_completion
        # we need to have python datetime objects for make it work with sqlite
        self.modified = plone_task.modified().asdatetime().replace(tzinfo=None)
        self.task_type = plone_task.task_type
        self.is_subtask = plone_task.get_is_subtask()
        self.sequence_number = plone_task.get_sequence_number()
        self.reference_number = plone_task.get_reference_number()
        self.containing_dossier = plone_task.get_containing_dossier()
        self.dossier_sequence_number = plone_task.get_dossier_sequence_number()
        self.assigned_org_unit = plone_task.responsible_client
        self.principals = plone_task.get_principals()
        self.predecessor = self.query_predecessor(
            *plone_task.get_predecessor_ids())
        self.containing_subdossier = plone_task.get_containing_subdossier()

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
        return self.task_type == 'forwarding_task_type'

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
        return "<span class=wf-{}>{}</span>".format(
            self.review_state,
            translate(self.review_state, domain='plone',
                      context=api.portal.get().REQUEST))

    def get_deadline_label(self):
        if not self.deadline:
            return u''

        if self.is_overdue:
            label = '<span class="overdue">{}</span>'
        else:
            label = '<span>{}</span>'

        return label.format(
            self.deadline.strftime('%d.%m.%Y'))

    def _date_to_zope_datetime(self, date):
        if not date:
            return None
        return ZopeDateTime(date.year, date.month, date.day)

    def get_deadline(self):
        return self._date_to_zope_datetime(self.deadline)

    @property
    def is_remote_task(self):
        """Returns true for tasks, where issuing and responsible
        admin_unit (assign org unit's admin_unit) are not equal.__add__()

        """
        return self.get_assigned_org_unit().admin_unit != self.get_admin_unit()

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
                css_class = 'icon-task-subtask'
            else:
                css_class = 'icon-task-remote-task'

        elif self.is_subtask:
            css_class = 'icon-task-subtask'

        elif self.is_remote_task:
            css_class = 'icon-task-remote-task'
        else:
            css_class = 'contenttype-opengever-task-task'

        return css_class

    def get_completed(self):
        return self._date_to_zope_datetime(self.completed)

    def has_access(self, member):
        if not member:
            return False

        principals = set(member.getGroups() + [member.getId()])
        allowed_principals = set(self.principals)
        return len(principals & allowed_principals) > 0

    def get_link(self, with_state_icon=True, with_responsible_info=True):
        admin_unit = self.get_admin_unit()
        if not admin_unit:
            return u'<span class="{}">{}</span>'.format(
                self.get_css_class(), self.title)

        url = '/'.join((admin_unit.public_url, self.physical_path))
        breadcrumb_titles = u"[{}] > {}".format(
            admin_unit.title, self.breadcrumb_title)
        responsible_info = u' <span class="discreet">({})</span>'.format(
            self.get_responsible_label(linked=False))
        link_content = u'<span class="{}">{}</span>'.format(
            self.get_css_class(), self.title)

        # If the target is on a different client we need to make a popup
        if self.admin_unit_id != get_current_admin_unit().id():
            link_target = u' target="_blank"'
        else:
            link_target = u''

        # Render the full link if we have acccess
        if self.has_access(api.user.get_current()):
            link = u'<a href="{}"{} title="{}">{}</a>'.format(
                url, link_target, breadcrumb_titles, link_content)
        else:
            link = link_content

        if with_responsible_info:
            link = u'{} {}'.format(link, responsible_info)

        # wrapped it into span tag
        if with_state_icon:
            link = self._task_state_wrapper(link)
        else:
            link = u'<span>%s</span>' % (link)

        transformer = api.portal.get_tool('portal_transforms')
        link = transformer.convertTo('text/x-html-safe', link).getData()

        return link

    def _task_state_wrapper(self, text):
        """ Wrap a span-tag around the text with the status-css class
        """
        return u'<span class="wf-%s">%s</span>' % (self.review_state, text)


class TaskPrincipal(Base):
    __tablename__ = 'task_principals'

    principal = Column(String(255), primary_key=True)
    task_id = Column(Integer, ForeignKey('tasks.id'),
                     primary_key=True)

    def __init__(self, principal):
        self.principal = principal

    def __repr__(self):
        return "<TaskPrincipal %s for %s>" % (self.principal, str(self.task))
