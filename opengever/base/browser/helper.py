from opengever.ogds.base.interfaces import IContactInformation
from zope.component import getUtility


def client_title_helper(item, value):
    """Returns the client title out of the client id (`value`).
    """

    if not value:
        return value

    info = getUtility(IContactInformation)
    client = info.get_client_by_id(value)

    if client:
        return client.title

    else:
        return value

