from opengever.globalindex.oguid import Oguid
from opengever.ogds.models.query import BaseQuery


class ProposalQuery(BaseQuery):

    def get_by_oguid(self, oguid):
        """Return the proposal identified by the given int_id and
        admin_unit_id or None if no such proposal exists.

        """
        return self.filter_by(oguid=Oguid(id=oguid)).first()
