from plone import api
from plone.api.exc import GroupNotFoundError


def get_users_by_group(groupname):
    try:
        return api.user.get_users(groupname)
    except GroupNotFoundError:
        return []
