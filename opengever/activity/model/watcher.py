from opengever.base.model import Base
from opengever.base.model import USER_ID_LENGTH
from opengever.ogds.base.actor import Actor
from opengever.ogds.base.actor import ActorLookup
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
        actor_lookup = ActorLookup(self.actorid)
        if actor_lookup.is_inbox() or actor_lookup.is_team():
            return [user.userid for user in
                    Actor.lookup(self.actorid).representatives()]

        return [self.actorid]
