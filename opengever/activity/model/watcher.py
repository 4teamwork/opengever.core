from opengever.base.model import Base
from opengever.base.model import USER_ID_LENGTH
from opengever.ogds.base.actor import ActorLookup
from opengever.ogds.models.user_settings import UserSettings
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

        Means for a single user, a list with the user_id and for an inbox
        watcher, a list of the userids of all inbox_group users who have
        notify_inbox_actions set to True.
        """
        actor_lookup = ActorLookup(self.actorid)
        representatives = [user.userid for user in
                           actor_lookup.lookup().representatives()]

        if actor_lookup.is_inbox() or actor_lookup.is_team():
            return [userid for userid in representatives
                    if UserSettings.get_setting_for_user(
                        userid, 'notify_inbox_actions')]
        return representatives
