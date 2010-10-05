from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.schema import Sequence
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import functions
from opengever.globalindex.model import Base


class Task(Base):
    """docstring for Task"""
    __tablename__='tasks'
    __table_args__ = (UniqueConstraint('client_id', 'int_id'), {})

    task_id = Column("id", Integer, Sequence("task_id_seq"), primary_key=True)
    client_id = Column(String(20), index=True)
    int_id = Column(Integer, index=True)

    title = Column(String(256))
    physical_path = Column(String(256))
    review_state = Column(String(50))
    icon = Column(String(50))

    responsible = Column(String(32), index=True)
    issuer = Column(String(32), index=True)
    
    task_type = Column(String(50), index=True)
    sequence_number = Column(String(10), index=True)
    
    created = Column(DateTime, default=functions.now())
    modified = Column(DateTime)
    deadline = Column(DateTime)
    completed = Column(DateTime)

    assigned_client = Column(String(20), index=True)

    predecessor_id = Column(Integer, ForeignKey('tasks.id'))
    successors = relationship("Task", backref=backref('predecessor',
        remote_side=task_id))

    def __init__(self, int_id, client_id):
        self.client_id = client_id
        self.int_id = int_id

    def __repr__(self):
        return "<Task %s@%s>" % (self.int_id, self.client_id)
