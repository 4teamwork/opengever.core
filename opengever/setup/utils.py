from pkg_resources import iter_entry_points


def get_entry_points(name):
    """Returns all entry points of group "opengever.setup" with names
    matching `name`.
    """

    for ep in iter_entry_points('opengever.setup'):
        if ep.name == name:
            yield ep


def get_ldap_configs():
    """Returns all ldap configs
    """
    for ep in get_entry_points('ldap'):
        module = ep.load()
        yield getattr(module, 'LDAP_PROFILE')
