from opengever.globalindex import Session
from opengever.globalindex.model import Base
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import Date
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import backref
from sqlalchemy.orm import relation
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Sequence
from sqlalchemy.sql import functions


class Task(Base):
    """docstring for Task"""

    MAX_TITLE_LENGTH = 256
    MAX_BREADCRUMB_LENGTH = 512

    __tablename__ = 'tasks'
    __table_args__ = (UniqueConstraint('admin_unit_id', 'int_id'), {})

    task_id = Column("id", Integer, Sequence("task_id_seq"), primary_key=True)
    admin_unit_id = Column(String(30), index=True, nullable=False)

    int_id = Column(Integer, index=True, nullable=False)

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
        self.sequence_number = plone_task.get_sequence_number()
        self.reference_number = plone_task.get_reference_number()
        self.containing_dossier = plone_task.get_containing_dossier()
        self.dossier_sequence_number = plone_task.get_dossier_sequence_number()
        self.assigned_org_unit = plone_task.responsible_client
        self.principals = plone_task.get_principals()
        self.predecessor = self.query_predecessor(
            *plone_task.get_predecessor_ids())

    def query_predecessor(self, pred_client_id, pred_init_id):
        if not (pred_client_id or pred_init_id):
            return None

        return Session.query(Task).filter_by(
            client_id=pred_client_id, int_id=pred_init_id).first()


class TaskPrincipal(Base):
    __tablename__ = 'task_principals'

    principal = Column(String(255), primary_key=True)
    task_id = Column(Integer, ForeignKey('tasks.id'),
                     primary_key=True)

    def __init__(self, principal):
        self.principal = principal

    def __repr__(self):
        return "<TaskPrincipal %s for %s>" % (self.principal, str(self.task))
