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
        if value is None:
            value = ''
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
                           self.contact.get_title(with_former_id=False))
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


class OrgRoleDocPropertyProvider(PrefixableDocPropertyProvider):
    """Provides doc-properties for an org-role and its associated person."""

    def __init__(self, org_role, prefix):
        super(OrgRoleDocPropertyProvider, self).__init__(prefix)
        self.org_role = org_role

    def get_properties(self):
        person_provider = self.org_role.person.get_doc_property_provider(self.prefix)
        properties = person_provider.get_properties()

        self._add_property(properties, 'orgrole', 'function',
                           self.org_role.function)
        self._add_property(properties, 'orgrole', 'description',
                           self.org_role.description)
        self._add_property(properties, 'orgrole', 'department',
                           self.org_role.department)

        return properties


class AddressDocPropertyProvider(PrefixableDocPropertyProvider):
    """Provides doc-properties for an address."""

    def __init__(self, address, prefix):
        super(AddressDocPropertyProvider, self).__init__(prefix)
        self.address = address

    def get_properties(self):
        properties = {}

        self._add_property(properties, 'address', 'street',
                           self.address.street)
        self._add_property(properties, 'address', 'zip_code',
                           self.address.zip_code)
        self._add_property(properties, 'address', 'city',
                           self.address.city)
        self._add_property(properties, 'address', 'country',
                           self.address.country)

        return properties


class MailAddressDocPropertyProvider(PrefixableDocPropertyProvider):
    """Provides doc-properties for a mail-address."""

    def __init__(self, mail_address, prefix):
        super(MailAddressDocPropertyProvider, self).__init__(prefix)
        self.mail_address = mail_address

    def get_properties(self):
        properties = {}

        self._add_property(properties, 'email', 'address',
                           self.mail_address.address)

        return properties


class PhoneNumberDocPropertyProvider(PrefixableDocPropertyProvider):
    """Provides doc-properties for a phone-number."""

    def __init__(self, phonenumber, prefix):
        super(PhoneNumberDocPropertyProvider, self).__init__(prefix)
        self.phonenumber = phonenumber

    def get_properties(self):
        properties = {}

        self._add_property(properties, 'phone', 'number',
                           self.phonenumber.phone_number)

        return properties


class URLDocPropertyProvider(PrefixableDocPropertyProvider):
    """Provides doc-properties for an url."""

    def __init__(self, url, prefix):
        super(URLDocPropertyProvider, self).__init__(prefix)
        self.url = url

    def get_properties(self):
        properties = {}

        self._add_property(properties, 'url', 'url',
                           self.url.url)

        return properties


class OrgRoleAddressDocPropertyProvider(AddressDocPropertyProvider):
    """Provides doc-properties for org role addresses."""

    def __init__(self, address, organization, prefix):
        super(OrgRoleAddressDocPropertyProvider, self).__init__(address,
                                                                prefix)
        self.organization = organization

    def get_properties(self):
        properties = super(
            OrgRoleAddressDocPropertyProvider, self).get_properties()

        self._add_property(properties, 'organization', 'name',
                           self.organization.name)

        return properties
