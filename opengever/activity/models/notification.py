from opengever.ogds.models import BASE
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy.orm import relationship


class Notification(BASE):

    __tablename__ = 'notifications'

    notification_id = Column('id', Integer, primary_key=True)

    watcher_id = Column(Integer, ForeignKey('watchers.id'))
    watcher = relationship("Watcher", backref="notifications")

    activiy_id = Column(Integer, ForeignKey('activities.id'))
    activity = relationship("Activity", backref="notifications")

    read = Column(Boolean(), default=False, nullable=False)
