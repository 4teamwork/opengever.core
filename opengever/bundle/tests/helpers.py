"""Miscellaneous test helpers.
"""


def get_title(item):
    title = item.get('title_de')
    if not title:
        title = item['title']
    return title


def get_portal_type(item):
    _type = item['_type']
    return _type.split('.')[-1]
