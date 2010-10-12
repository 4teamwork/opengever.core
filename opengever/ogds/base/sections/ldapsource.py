import logging
import ldap
from zope.interface import classProvides, implements
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.utils import Expression

class LDAPSourceSection(object):
    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.logger = logging.getLogger(options['blueprint'])
        self.options = options
        self.mapping = Expression(options['mapping'], transmogrifier, name, options)(self.previous)

    def __iter__(self):

        for item in self.previous:
            yield item

        # connecting to the ldap
        con = ldap.initialize(self.options.get('dsn', ''))
        con.start_tls_s()
        con.simple_bind_s(self.options.get('bind_dn'), self.options.get('bind_pw'))
        res = con.search(self.options.get('base_dn'), 3, self.options.get('filter'))

        while True:
            code, data = con.result(res, all=False)
            if code != 100:
                break
            temp = {}
            for k, v in data[0][1].items():
                if self.mapping.get(k, None):
                    temp[self.mapping[k]] = v
                else:
                    temp[k] = v
            yield temp
