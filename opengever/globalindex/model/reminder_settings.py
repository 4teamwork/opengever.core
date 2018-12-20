from opengever.base.date_time import utcnow_tz_aware
from opengever.base.model import Base
from opengever.base.model import USER_ID_LENGTH
from opengever.base.model import UTCDateTime
from opengever.task.reminder import TASK_REMINDER_OPTIONS
from sqlalchemy import Column
from sqlalchemy import Date
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Sequence


class ReminderSetting(Base):

    __tablename__ = 'reminder_settings'

    reminder_setting_id = Column('id', Integer,
                                 Sequence('reminder_setting_id_seq'),
                                 primary_key=True)

    task_id = Column(Integer, ForeignKey('tasks.id'), nullable=False)
    task = relationship("Task", backref="reminder_settings")

    actor_id = Column(String(USER_ID_LENGTH), index=True, nullable=False)

    option_type = Column(String(255), nullable=False)
    remind_day = Column(Date, nullable=False)
    created = Column(UTCDateTime(timezone=True), default=utcnow_tz_aware)

    def __repr__(self):
        return u'<ReminderSetting {} for {} for {} on {} >'.format(
            self.reminder_setting_id,
            self.actor_id,
            repr(self.task),
            self.remind_day)

    def update_remind_day(self):
        option = TASK_REMINDER_OPTIONS[self.option_type]
        self.remind_day = option.calculate_remind_on(self.task.deadline)
