from opengever.ogds.base.actor import Actor
from opengever.ogds.models.service import ogds_service
from plone import api


def get_users_by_group(groupname):
    group = ogds_service().fetch_group(groupname)
    if not group:
        return []
    return group.users


def actor_link():
    return Actor.lookup(api.user.get_current().id).get_link()
