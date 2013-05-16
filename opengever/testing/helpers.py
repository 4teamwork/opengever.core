from Products.CMFCore.utils import getToolByName


def create_plone_user(portal, userid, password='demo09'):
    acl_users = getToolByName(portal, 'acl_users')
    acl_users.source_users.addUser(userid, userid, password)


def obj2brain(obj):
    catalog = getToolByName(obj, 'portal_catalog')
    query = {'path':
             {'query': '/'.join(obj.getPhysicalPath()),
              'depth': 0}}
    brains = catalog(query)
    if len(brains) == 0:
        raise Exception('Not in catalog: %s' % obj)
    else:
        return brains[0]
