from opengever.globalindex.oguid import Oguid
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

    def all_admin_unit_tasks(self, admin_unit):
        """Returns query which list all tasks where the assigned_org_unit
        is part of the current_admin_unit.
        """
        unit_ids = [unit.id() for unit in admin_unit.org_units]
        return self.filter(self._attribute('assigned_org_unit').in_(unit_ids))

    def all_issued_tasks(self, admin_unit):
        """List all tasks from the current_admin_unit.
        """
        return self.filter(self._attribute('admin_unit_id') == admin_unit.id())

    by_admin_unit = all_issued_tasks

    def tasks_by_ids(self, int_ids, admin_unit):
        """
        """
        query = self.filter(
            self._attribute('admin_unit_id') == admin_unit.id())
        return query.filter(self._attribute('int_id').in_(int_ids))

    def by_id(self, int_id, admin_unit_id):
        """Returns the task identified by the given int_id and admin_unit_id
        or None
        """
        return self.filter_by(
            admin_unit_id=admin_unit_id, int_id=int_id).first()

    def by_oguid(self, oguid):
        """Returns the task identified by the given int_id and admin_unit_id
        or None
        """
        return self.filter_by(oguid=Oguid(id=oguid)).first()

    def by_path(self, path, admin_unit_id):
        """Returns a task on the specified client identified by its physical
        path (which is relative to the site root!) or None.
        """
        return self.filter_by(
            admin_unit_id=admin_unit_id, physical_path=path).first()

    def by_container(self, container, admin_unit):
        url_tool = api.portal.get_tool(name='portal_url')
        path = '/'.join(url_tool.getRelativeContentPath(container))

        return self.by_admin_unit(admin_unit)\
                   .filter(self._attribute('physical_path').like(path + '%'))

    def by_brain(self, brain):
        relative_content_path = '/'.join(brain.getPath().split('/')[2:])
        return self.by_admin_unit(get_current_admin_unit())\
                   .filter(self._attribute('physical_path')==relative_content_path).one()
