import logging
from zope.interface import classProvides, implements
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.interfaces import ISection


LDAP_CHARSET = 'latin1'

class LDAPUserSourceSection(object):
    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.context = transmogrifier.context
        self.previous = previous
        self.logger = logging.getLogger(options['blueprint'])
        self.options = options
        #self.mapping = Expression(options['mapping'], transmogrifier, name, options)(self.previous)

    def __iter__(self):

        for item in self.previous:
            yield item

        # get all the attributes from the ldap plugin
        ldap_name = self.options.get('ldap_name', 'ldap')
        ldap_folder = self.context.acl_users.get(ldap_name).get('acl_users')

        #iterate over the users in the ldap_userfolder
        for uid in ldap_folder.getUserIds():
            try:
                user = ldap_folder.getUserById(uid)
            except UnicodeDecodeError:
                print "The User with the uid %s can't be imported (UnicodeDecodeError)" % uid

            temp = {}

            for attr in ldap_folder.getSchemaDict():
                v = user.getProperty(attr.get('ldap_name'))
                if isinstance(v, list):
                    v = v[0]
                temp[attr.get('public_name')] = v.decode(LDAP_CHARSET)
            yield temp


class LDAPGroupSourceSection(LDAPUserSourceSection):
    classProvides(ISectionBlueprint)
    implements(ISection)


    def __iter__(self):

        for item in self.previous:
            yield item

        # get all the attributes from the ldap plugin
        ldap_name = self.options.get('ldap_name', 'ldap')
        ldap_folder = self.context.acl_users.get(ldap_name).get('acl_users')

        # #iterate over the groups in the ldap_userfolder
        for group_data in ldap_folder.getGroups():
            groupid = group_data[0]
            try:
                group = ldap_folder.getGroupById(groupid)
            except UnicodeDecodeError:
                print "The Group with the groupid %s can't be imported (UnicodeDecodeError)" % groupid
        
            temp = {}
            if groupid.startswith('og_'):
                temp['groupid'] = group.getId()
                temp['title'] = group.getName()
                temp['_users'] = group.getMemberIds()

                yield temp
