from datetime import datetime
from Products.CMFCore.utils import getToolByName
import pytz


DEFAULT_TZ = pytz.timezone('Europe/Zurich')


def localized_datetime(*args, **kwargs):
    """Localize timezone naive datetime to default timezone."""

    if args or kwargs:
        dt = datetime(*args, **kwargs)
    else:
        dt = datetime.now()

    return DEFAULT_TZ.localize(dt)


def create_plone_user(portal, userid, password='demo09'):
    acl_users = getToolByName(portal, 'acl_users')
    acl_users.source_users.addUser(userid, userid, password)


def obj2brain(obj, unrestricted=False):
    catalog = getToolByName(obj, 'portal_catalog')
    query = {'path': {'query': '/'.join(obj.getPhysicalPath()), 'depth': 0}}

    if unrestricted:
        brains = catalog.unrestrictedSearchResults(query)
    else:
        brains = catalog(query)

    if len(brains) == 0:
        raise Exception('Not in catalog: %s' % obj)

    return brains[0]


def index_data_for(obj):
    catalog = getToolByName(obj, 'portal_catalog')
    return catalog.getIndexDataForRID(obj2brain(obj).getRID())
