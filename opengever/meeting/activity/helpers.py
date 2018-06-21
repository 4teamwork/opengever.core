from opengever.ogds.base.utils import ogds_service


def get_users_by_group(groupname):
    group = ogds_service().fetch_group(groupname)
    if not group:
        return []
    return group.users
