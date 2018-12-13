from opengever.base.model import Session
from opengever.base.sqlsyncer import SqlSyncer
from opengever.globalindex.model.task import Task
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.ogds.base.utils import get_current_org_unit
from zope.container.interfaces import IContainerModifiedEvent
import logging


logger = logging.getLogger('opengever.globalindex')


class TaskSqlSyncer(SqlSyncer):

    def get_sql_task(self):
        admin_unit_id = get_current_admin_unit().id()
        current_org_unit_id = get_current_org_unit().id()
        sequence_number = self.obj.get_sequence_number()
        assigned_org_unit = self.obj.responsible_client

        task = Session.query(Task).filter_by(
            admin_unit_id=admin_unit_id, int_id=self.obj_id).first()
        if task is None:
            task = Task(self.obj_id, admin_unit_id,
                        issuing_org_unit=current_org_unit_id,
                        assigned_org_unit=assigned_org_unit,
                        sequence_number=sequence_number,
                        created=self.obj.created().asdatetime())
            Session.add(task)
        return task

    def sync_with_sql(self):
        task = self.get_sql_task()
        task.sync_with(self.obj)
        logger.info('Task {!r} (modified:{}) has been successfully synchronized '
                    'to globalindex ({!r}).'.format(
                        self.obj,
                        self.obj.modified().asdatetime().replace(tzinfo=None),
                        task))


def sync_task(obj, event):
    """Index the given task in opengever.globalindex.
    """
    if IContainerModifiedEvent.providedBy(event):
        return

    TaskSqlSyncer(obj, event).sync()
