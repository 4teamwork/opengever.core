from ftw.builder import builder_registry


USER_TEMPLATE = {
    'displayName': 'Sekretariat1 Mandant1',
    'email': 'sk1m1@example.com',
    'facsimileTelephoneNumber': ['031 305 90 25'],
    'firstname': 'Sekretariat1',
    'fullname': 'Sekretariat1 Mandant1',
    'l': ['Bern'],
    'labeledURI': ['http://example.com'],
    'lastname': 'Mandant1',
    'mobile': ['012 345 6789'],
    'o': ['4teamwork GmbH'],
    'objectClass': ['top', 'person', 'organizationalPerson', 'inetOrgPerson'],
    'ou': ['St-maurice'],
    'postalCode': ['3012'],
    'street': ['Engehaldenstrasse 53'],
    'telephoneNumber': ['031 305 90 24'],
    'userid': 'sk1m1'
}

USER_DN_TEMPLATE = "{},ou=Users,ou=Dev,ou=OneGovGEVER,dc=4teamwork,dc=ch"


class LDAPUserBuilder(object):

    def __init__(self, session):
        self.session = session
        self.arguments = {}

    def having(self, **kwargs):
        self.arguments.update(kwargs)
        return self

    def named(self, userid):
        self.arguments['userid'] = userid
        return self

    def create(self, **kwargs):
        attributes = USER_TEMPLATE.copy()
        # Overlay specified arguments on top over default attributes
        attributes.update(self.arguments)

        # Calculate some computed values based on merged attributes
        attributes['fullname'] = ' '.join([attributes['firstname'],
                                           attributes['lastname']])
        attributes['displayName'] = attributes['fullname']
        attributes['email'] = "{}@example.com".format(attributes['userid'])

        # Overlay arguments again to make sure specified values take precedence
        attributes.update(self.arguments)
        dn = USER_DN_TEMPLATE.format(attributes['userid'])
        obj = (dn, attributes)
        return obj


builder_registry.register('ldapuser', LDAPUserBuilder)


GROUP_TEMPLATE = {
    'cn': 'og_mandant1_users',
    'objectClass': ['groupOfUniqueNames', 'top'],
    'uniqueMember': [
        'cn=Sekretariat1 Mandant1,ou=Users,ou=Dev,ou=OneGovGEVER,dc=4teamwork,dc=ch',
        'cn=Sekretariat2 Mandant1,ou=Users,ou=Dev,ou=OneGovGEVER,dc=4teamwork,dc=ch',
    ]
}

GROUP_DN_TEMPLATE = "cn={},ou=Groups,ou=Dev,ou=OneGovGEVER,dc=4teamwork,dc=ch"


class LDAPGroupBuilder(object):

    def __init__(self, session):
        self.session = session
        self.arguments = {}

    def having(self, **kwargs):
        self.arguments.update(kwargs)
        return self

    def named(self, groupid):
        self.arguments['cn'] = groupid
        return self

    def with_members(self, members):
        self.arguments['uniqueMember'] = []
        for member in members:
            if isinstance(member, tuple):
                dn = member[0]
            elif isinstance(member, basestring):
                dn = member
            else:
                raise ValueError(
                    "members must be either user tuples or userid strings")
            self.arguments['uniqueMember'].append(dn)
        return self

    def create(self, **kwargs):
        attributes = GROUP_TEMPLATE.copy()
        attributes.update(self.arguments)
        dn = GROUP_DN_TEMPLATE.format(attributes['cn'])
        obj = (dn, attributes)
        return obj


builder_registry.register('ldapgroup', LDAPGroupBuilder)
