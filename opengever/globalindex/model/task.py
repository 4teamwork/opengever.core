from opengever.globalindex import Session
from opengever.globalindex.model import Base
from opengever.globalindex.oguid import Oguid
from opengever.ogds.base.actor import Actor
from opengever.ogds.base.utils import ogds_service
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import Date
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import backref
from sqlalchemy.orm import composite
from sqlalchemy.orm import Query
from sqlalchemy.orm import relation
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Sequence
from sqlalchemy.sql import functions


class TaskQuery(Query):
    """TaskQuery Object.
    """

    def users_tasks(self, userid):
        """Returns query which List all tasks where the given user,
        his userid, is responsible. It queries all admin units.
        """
        return self.filter(Task.responsible == userid)

    def users_issued_tasks(self, userid):
        """Returns query which list all tasks where the given user
        is the issuer. It queries all admin units.
        """
        return self.filter(Task.issuer == userid)

    def all_admin_unit_tasks(self, admin_unit):
        """Returns query which list all tasks where the assigned_org_unit
        is part of the current_admin_unit.
        """
        unit_ids = [unit.id() for unit in admin_unit.org_units]
        return self.filter(Task.assigned_org_unit.in_(unit_ids))

    def all_issued_tasks(self, admin_unit):
        """List all tasks from the current_admin_unit.
        """
        return self.filter(Task.admin_unit_id == admin_unit.id())

    def tasks_by_id(self, int_ids, admin_unit):
        """
        """
        query = self.filter(Task.admin_unit_id == admin_unit.id())
        return query.filter(Task.int_id.in_(int_ids))


class Task(Base):
    """docstring for Task"""

    query_cls = TaskQuery

    MAX_TITLE_LENGTH = 256
    MAX_BREADCRUMB_LENGTH = 512

    __tablename__ = 'tasks'
    __table_args__ = (UniqueConstraint('admin_unit_id', 'int_id'), {})

    task_id = Column("id", Integer, Sequence("task_id_seq"), primary_key=True)

    admin_unit_id = Column(String(30), index=True, nullable=False)
    int_id = Column(Integer, index=True, nullable=False)

    oguid = composite(Oguid, admin_unit_id, int_id)

    title = Column(String(MAX_TITLE_LENGTH))
    breadcrumb_title = Column(String(MAX_BREADCRUMB_LENGTH))
    physical_path = Column(String(256))
    review_state = Column(String(50))
    icon = Column(String(50))

    responsible = Column(String(32), index=True)
    issuer = Column(String(32), index=True)

    task_type = Column(String(50), index=True)
    is_subtask = Column(Boolean(), default=False)

    reference_number = Column(String(100))
    sequence_number = Column(String(10), index=True)
    dossier_sequence_number = Column(String(10))
    containing_dossier = Column(String(512))

    created = Column(DateTime, default=functions.now())
    modified = Column(DateTime)
    deadline = Column(Date)
    completed = Column(Date)

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

    def sync_with(self, plone_task):
        """Sync this task instace with its corresponding plone taks.

        """
        self.title = plone_task.safe_title
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
        self.sequence_number = str(plone_task.get_sequence_number())
        self.reference_number = plone_task.get_reference_number()
        self.containing_dossier = plone_task.get_containing_dossier()
        self.dossier_sequence_number = str(plone_task.get_dossier_sequence_number())
        self.assigned_org_unit = plone_task.responsible_client
        self.principals = plone_task.get_principals()
        self.predecessor = self.query_predecessor(
            *plone_task.get_predecessor_ids())

    def query_predecessor(self, admin_unit_id, pred_init_id):
        if not (admin_unit_id or pred_init_id):
            return None

        return Session.query(Task).filter_by(
            admin_unit_id=admin_unit_id, int_id=pred_init_id).first()

    def get_issuer_label(self):
        actor = Actor.lookup(self.issuer)
        org_unit = ogds_service().fetch_org_unit(self.issuing_org_unit)
        return org_unit.prefix_label(actor.get_link())

    @property
    def is_forwarding(self):
        return self.task_type == 'forwarding_task_type'


class TaskPrincipal(Base):
    __tablename__ = 'task_principals'

    principal = Column(String(255), primary_key=True)
    task_id = Column(Integer, ForeignKey('tasks.id'),
                     primary_key=True)

    def __init__(self, principal):
        self.principal = principal

    def __repr__(self):
        return "<TaskPrincipal %s for %s>" % (self.principal, str(self.task))
