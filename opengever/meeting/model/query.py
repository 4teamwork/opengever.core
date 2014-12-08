from opengever.base.oguid import Oguid
from opengever.ogds.models.query import BaseQuery
from plone import api


class ProposalQuery(BaseQuery):

    def get_by_oguid(self, oguid):
        """Return the proposal identified by the given int_id and
        admin_unit_id or None if no such proposal exists.

        """
        return self.filter_by(oguid=Oguid(oguid=oguid)).first()

    def by_container(self, container, admin_unit):
        # XXX same as TaskQuery
        url_tool = api.portal.get_tool(name='portal_url')
        path = '/'.join(url_tool.getRelativeContentPath(container))

        return self.by_admin_unit(admin_unit)\
                   .filter(self._attribute('physical_path').like(path + '%'))

    def by_admin_unit(self, admin_unit):
        """List all proposals for admin_unit."""

        return self.filter(self._attribute('admin_unit_id') == admin_unit.id())
