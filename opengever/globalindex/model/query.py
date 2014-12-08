from opengever.base.oguid import Oguid
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.ogds.models.query import BaseQuery
from plone import api


class TaskQuery(BaseQuery):

    def users_tasks(self, userid):
        """Returns query which List all tasks where the given user,
        his userid, is responsible. It queries all admin units.
        """
        return self.filter(self._attribute('responsible') == userid)

    def users_issued_tasks(self, userid):
        """Returns query which list all tasks where the given user
        is the issuer. It queries all admin units.
        """
        return self.filter(self._attribute('issuer') == userid)

    def by_assigned_org_unit(self, org_unit):
        """Returns all tasks assigned to the given orgunit."""
        return self.filter(self._attribute('assigned_org_unit') == org_unit.id())

    def by_issuing_org_unit(self, org_unit):
        """Returns all tasks issued by the given orgunit."""
        return self.filter(self._attribute('issuing_org_unit') == org_unit.id())

    def all_issued_tasks(self, admin_unit):
        """List all tasks from the current_admin_unit.
        """
        return self.filter(self._attribute('admin_unit_id') == admin_unit.id())

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
        return self.filter_by(oguid=Oguid(oguid=oguid)).first()

    def by_path(self, path, admin_unit_id):
        """Returns a task on the specified client identified by its physical
        path (which is relative to the site root!) or None.
        """
        return self.filter_by(
            admin_unit_id=admin_unit_id, physical_path=path).first()

    def by_ids(self, task_ids):
        """Returns all tasks whos task_ids are listed in `task_ids`.
        """
        return self.filter(self._attribute('task_id').in_(task_ids)).all()

    def by_container(self, container, admin_unit):
        url_tool = api.portal.get_tool(name='portal_url')
        path = '/'.join(url_tool.getRelativeContentPath(container))

        return self.by_admin_unit(admin_unit)\
                   .filter(self._attribute('physical_path').like(path + '%'))

    def by_brain(self, brain):
        relative_content_path = '/'.join(brain.getPath().split('/')[2:])
        return self.by_admin_unit(get_current_admin_unit())\
                   .filter(self._attribute('physical_path')==relative_content_path).one()

    def subtasks_by_task(self, task):
        """Queries all subtask of the given task sql object."""
        query = self.filter(
            self._attribute('admin_unit_id') == task.admin_unit_id)
        query = query.filter(self._attribute('physical_path').startswith(
            '{}/'.format(task.physical_path)))
        return query
