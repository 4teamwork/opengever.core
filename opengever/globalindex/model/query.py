from opengever.base.model import is_oracle
from opengever.base.oguid import Oguid
from opengever.globalindex.model.task import Task
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.ogds.models.query import BaseQuery
from plone import api
from sqlalchemy import and_
from sqlalchemy import func
from sqlalchemy import or_


class TaskQuery(BaseQuery):

    def _extend_with_physical_path(self, query, field, path):
        if is_oracle():
            return query.filter(func.to_char(field) == path)

        return query.filter(field == path)

    def users_tasks(self, userid):
        """Returns query which List all tasks where the given user,
        his userid, is responsible. It queries all admin units.
        """
        return self.filter(Task.responsible == userid)

    def by_responsibles(self, responsibles):
        return self.filter(Task.responsible.in_(responsibles))

    def users_issued_tasks(self, userid):
        """Returns query which list all tasks where the given user
        is the issuer. It queries all admin units.
        """
        return self.filter(Task.issuer == userid)

    def by_assigned_org_unit(self, org_unit):
        """Returns all tasks assigned to the given orgunit."""
        return self.filter(Task.assigned_org_unit == org_unit.id())

    def by_issuing_org_unit(self, org_unit):
        """Returns all tasks issued by the given orgunit."""
        return self.filter(Task.issuing_org_unit == org_unit.id())

    def all_issued_tasks(self, admin_unit):
        """List all tasks from the current_admin_unit.
        """
        return self.filter(Task.admin_unit_id == admin_unit.id())

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
        return self._extend_with_physical_path(
            query, Task.physical_path, path).first()

    def by_ids(self, task_ids):
        """Returns all tasks whos task_ids are listed in `task_ids`.
        """
        return self.filter(Task.task_id.in_(task_ids)).all()

    def by_container(self, container, admin_unit):
        url_tool = api.portal.get_tool(name='portal_url')
        path = '/'.join(url_tool.getRelativeContentPath(container))
        path = '{}/'.format(path)

        return self.by_admin_unit(admin_unit).filter(
            Task.physical_path.startswith(path))

    def by_brain(self, brain):
        relative_content_path = '/'.join(brain.getPath().split('/')[2:])
        query = self.by_admin_unit(get_current_admin_unit())
        return self._extend_with_physical_path(
            query, Task.physical_path, relative_content_path).one()

    def subtasks_by_tasks(self, tasks):
        """Queries all subtask of the given tasks sql object."""
        query = self.filter(
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

    def in_pending_state(self):
        return self.filter(Task.review_state.in_(Task.PENDING_STATES))


Task.query_cls = TaskQuery
