"""Miscellaneous test helpers.
"""


def get_title(item):
    title = item.get('title_de', item.get('title'))
    if not title:
        # fallback for ogds_users
        title = item.get('userid')

    return title


def get_portal_type(item):
    _type = item['_type']
    return _type.split('.')[-1]
