import logging
from zope.interface import classProvides, implements
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.utils import Expression


class LDAPSourceSection(object):
    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.context = transmogrifier.context
        self.previous = previous
        self.logger = logging.getLogger(options['blueprint'])
        self.options = options
        self.mapping = Expression(options['mapping'], transmogrifier, name, options)(self.previous)

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
            for old_k, new_k in self.mapping.items():
                v = user.getProperty(old_k)
                if isinstance(v, list):
                    v = v[0]
                temp[new_k] = v.decode('utf-8')
            yield temp
