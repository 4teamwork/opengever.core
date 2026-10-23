from opengever.base.model import Base
from opengever.base.model import UID_LENGTH
from opengever.base.model import UNIT_ID_LENGTH
from opengever.base.query import BaseQuery
from opengever.base.types import UnicodeCoercingText
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String
import uuid


TASK_STATUS_PENDING = u'pending'
TASK_STATUS_RUNNING = u'running'
TASK_STATUS_SUCCEEDED = u'succeeded'
TASK_STATUS_FAILED = u'failed'

TASK_STATUS_ALL = (
    TASK_STATUS_PENDING,
    TASK_STATUS_RUNNING,
    TASK_STATUS_SUCCEEDED,
    TASK_STATUS_FAILED,
)

DEFAULT_PRIORITY = 5
DEFAULT_MAX_RETRIES = 3


class BackgroundTaskQuery(BaseQuery):

    def by_admin_unit(self, admin_unit_id):
        return self.filter_by(admin_unit_id=admin_unit_id)

    def pending(self, admin_unit_id):
        return self.by_admin_unit(admin_unit_id).filter_by(
            status=TASK_STATUS_PENDING)

    def running(self, admin_unit_id):
        return self.by_admin_unit(admin_unit_id).filter_by(
            status=TASK_STATUS_RUNNING)


def default_task_id():
    return unicode(uuid.uuid4())


class BackgroundTask(Base):

    __tablename__ = u'background_tasks'

    query_cls = BackgroundTaskQuery

    task_id = Column(String(UID_LENGTH), primary_key=True, default=default_task_id)
    admin_unit_id = Column(String(UNIT_ID_LENGTH), nullable=False)
    task_type = Column(String(100), nullable=False)
    status = Column(String(20), nullable=False, default=TASK_STATUS_PENDING)
    priority = Column(Integer, nullable=False, default=DEFAULT_PRIORITY)
    scheduled_for = Column(DateTime, nullable=True)
    created = Column(DateTime, nullable=False)
    started = Column(DateTime, nullable=True)
    finished = Column(DateTime, nullable=True)
    retries = Column(Integer, nullable=False, default=0)
    max_retries = Column(Integer, nullable=False, default=DEFAULT_MAX_RETRIES)
    error_message = Column(UnicodeCoercingText, nullable=True)
    checkpoint_data = Column(UnicodeCoercingText, nullable=True)
    task_arguments = Column(UnicodeCoercingText, nullable=True)
