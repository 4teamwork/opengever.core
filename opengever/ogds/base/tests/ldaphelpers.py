from opengever.ogds.base.interfaces import ILDAPSearch
from Products.LDAPMultiPlugins.interfaces import ILDAPMultiPlugin
from zope.component import adapts
from zope.interface import implements
from zope.interface import Interface
import ldap


class IFakeLDAPUserFolder(Interface):
    pass


class FakeLDAPUserFolder(object):

    implements(IFakeLDAPUserFolder)

    _uid_attr = 'uid'

    def __init__(self):
        self.users = []
        self.groups = []

    def getSchemaDict(self):
        return (
            {'binary': False,
             'friendly_name': 'Canonical Name',
             'ldap_name': 'cn',
             'multivalued': False,
             'public_name': 'fullname'},
            {'binary': False,
             'friendly_name': 'Email address',
             'ldap_name': 'mail',
             'multivalued': False,
             'public_name': 'email'},
            {'binary': False,
             'friendly_name': 'First name',
             'ldap_name': 'givenName',
             'multivalued': False,
             'public_name': 'firstname'},
            {'binary': False,
             'friendly_name': 'Last Name',
             'ldap_name': 'sn',
             'multivalued': False,
             'public_name': 'lastname'},
            {'binary': False,
             'friendly_name': 'User id',
             'ldap_name': 'uid',
             'multivalued': False,
             'public_name': 'userid'})


class FakeLDAPPlugin(object):

    implements(ILDAPMultiPlugin)

    def __init__(self, userfolder):
        self.userfolder = userfolder

    def _getLDAPUserFolder(self):
        return self.userfolder


class FakeLDAPSearchUtility(object):

    implements(ILDAPSearch)
    adapts(IFakeLDAPUserFolder)

    is_ad = False

    def __init__(self, userfolder):
        self.userfolder = userfolder

    def get_users(self):
        return self.userfolder.users

    def get_groups(self):
        return self.userfolder.groups

    def get_group_members(self, groupinfo):
        return groupinfo['uniqueMember']

    def entry_by_dn(self, dn):
        entries = self.userfolder.users + self.userfolder.groups
        for entry in entries:
            if entry[0] == dn:
                return entry
        raise ldap.NO_SUCH_OBJECT(dn)
