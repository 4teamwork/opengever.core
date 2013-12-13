from sqlalchemy import Column, Integer, String, DateTime, Date, Boolean
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import relation
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.schema import Sequence
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import functions
from opengever.globalindex.model import Base


class Task(Base):
    """docstring for Task"""
    __tablename__ = 'tasks'
    __table_args__ = (UniqueConstraint('client_id', 'int_id'), {})

    task_id = Column("id", Integer, Sequence("task_id_seq"), primary_key=True)
    client_id = Column(String(20), index=True)
    int_id = Column(Integer, index=True)

    title = Column(String(256))
    breadcrumb_title = Column(String(512))
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

    assigned_client = Column(String(20), index=True)

    predecessor_id = Column(Integer, ForeignKey('tasks.id'))
    successors = relationship("Task", backref=backref('predecessor',
                                                      remote_side=task_id),
                                      cascade="delete")

    _principals = relation('TaskPrincipal', backref='task',
                     cascade='all, delete-orphan')
    principals = association_proxy('_principals', 'principal')

    def __init__(self, int_id, client_id):
        self.client_id = client_id
        self.int_id = int_id

    def __repr__(self):
        return "<Task %s@%s>" % (self.int_id, self.client_id)

    @property
    def id(self):
        return self.task_id


class TaskPrincipal(Base):
    __tablename__ = 'task_principals'

    principal = Column(String(255), primary_key=True)
    task_id = Column(Integer, ForeignKey('tasks.id'),
                     primary_key=True)

    def __init__(self, principal):
        self.principal = principal

    def __repr__(self):
        return "<TaskPrincipal %s for %s>" % (self.principal, str(self.task))
