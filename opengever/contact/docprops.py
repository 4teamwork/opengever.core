class PrefixableDocPropertyProvider(object):
    """Baseclass for PrefixableDocPropertyProvider.

    Contains utility methods to create a dict of doc-properties. Allows
    definition of a prefix that will be inserted in the namespace after the
    application part.
    """

    NS_APP = 'ogg'

    def __init__(self, prefix):
        self.prefix = prefix

    def _add_property(self, properties, kind, name, value):
        """Add single property to collection of properties."""
        if not value:
            return
        key = '.'.join((self.NS_APP, self.prefix, kind, name))
        properties[key] = value

    def get_properties(self):
        return {}


class ContactDocPropertyProvider(PrefixableDocPropertyProvider):

    def __init__(self, contact, prefix):
        super(ContactDocPropertyProvider, self).__init__(prefix=prefix)
        self.contact = contact

    def get_properties(self):
        properties = {}

        self._add_property(properties, 'contact', 'title',
                           self.contact.get_title())
        self._add_property(properties, 'contact', 'description',
                           self.contact.description)

        return properties


class PersonDocPropertyProvider(ContactDocPropertyProvider):

    def __init__(self, person, prefix):
        super(PersonDocPropertyProvider, self).__init__(person, prefix=prefix)
        self.person = person

    def get_properties(self):
        properties = super(PersonDocPropertyProvider, self).get_properties()

        self._add_property(properties, 'person', 'salutation',
                           self.person.salutation)
        self._add_property(properties, 'person', 'academic_title',
                           self.person.academic_title)
        self._add_property(properties, 'person', 'firstname',
                           self.person.firstname)
        self._add_property(properties, 'person', 'lastname',
                           self.person.lastname)

        return properties


class OrganizationDocPropertProvider(ContactDocPropertyProvider):

    def __init__(self, organization, prefix):
        super(OrganizationDocPropertProvider, self).__init__(
            organization, prefix=prefix)
        self.organization = organization

    def get_properties(self):
        properties = super(OrganizationDocPropertProvider, self).get_properties()

        self._add_property(properties, 'organization', 'name',
                           self.organization.name)

        return properties
