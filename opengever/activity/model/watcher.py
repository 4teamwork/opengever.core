from opengever.base.model import Base
from opengever.ogds.models import USER_ID_LENGTH
from opengever.ogds.models.service import OGDSService
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.schema import Sequence


class Watcher(Base):
    """Associates a user with a resource that he is watching."""

    __tablename__ = 'watchers'

    watcher_id = Column('id', Integer, Sequence('watchers_id_seq'),
                        primary_key=True)
    actorid = Column(String(USER_ID_LENGTH), nullable=False, unique=True)

    resources = association_proxy('subscriptions', 'resource')

    def __repr__(self):
        return '<Watcher {}>'.format(repr(self.actorid))

    def get_user_ids(self):
        """Returns a list of userids which represents the given watcher:

        Means for a single user, a list with the user_id and for a inbox watcher,
        a list of the userids of all inbox_group users.
        """
        # XXX Use opengever.ogds.models.actor instead of own actor differentiation.
        ogds_service = OGDSService(self.session)
        if self.actorid.startswith('inbox:'):
            org_unit_id = self.actorid.split(':', 1)[1]
            org_unit = ogds_service.fetch_org_unit(org_unit_id)
            return [user.userid for user in org_unit.inbox_group.users]

        else:
            return [self.actorid]
