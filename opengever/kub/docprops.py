from opengever.base.docprops import BaseDocPropertyProvider


class KuBEntityDocPropertyProvider(object):

    def __init__(self, entity):
        # avoid circular imports
        from opengever.kub.entity import KuBEntity

        self.person = None
        self.organization = None
        self.membership = None
        if entity.is_person():
            self.person = entity
        elif entity.is_organization():
            self.organization = entity
        elif entity.is_membership():
            self.person = KuBEntity("person:" + entity["person"]["id"])
            self.organization = KuBEntity("organization:" + entity["organization"]["id"])
            self.membership = entity

    @property
    def membership_person_or_organization(self):
        return self.membership or self.person or self.organization

    @property
    def person_or_organization(self):
        return self.person or self.organization

    @property
    def organization_or_person(self):
        return self.organization or self.person

    def get_properties(self, prefix=None):
        properties = {}
        properties.update(self.get_contact_properties(prefix))
        properties.update(self.get_person_properties(prefix))
        properties.update(self.get_organization_properties(prefix))
        properties.update(self.get_membership_properties(prefix))
        properties.update(self.get_address_properties(prefix))
        properties.update(self.get_email_properties(prefix))
        properties.update(self.get_phone_properties(prefix))
        properties.update(self.get_url_properties(prefix))
        return properties

    def get_contact_properties(self, prefix):
        provider = KuBContactDocPropertyProvider(self.membership_person_or_organization)
        return provider.get_properties(prefix)

    def get_person_properties(self, prefix):
        if self.person is None:
            return {}
        return KuBPersonDocPropertyProvider(self.person).get_properties(prefix)

    def get_organization_properties(self, prefix):
        if self.organization is None:
            return {}
        return KuBOrganizationDocPropertyProvider(self.organization).get_properties(prefix)

    def get_membership_properties(self, prefix):
        if self.membership is None:
            return {}
        return KuBMembershipDocPropertyProvider(self.membership).get_properties(prefix)

    def get_address_properties(self, prefix):
        provider = KuBAddressDocPropertyProvider(self.organization_or_person)
        return provider.get_properties(prefix)

    def get_email_properties(self, prefix):
        provider = KuBEmailDocPropertyProvider(self.person_or_organization)
        return provider.get_properties(prefix)

    def get_phone_properties(self, prefix):
        provider = KuBPhoneNumberDocPropertyProvider(self.person_or_organization)
        return provider.get_properties(prefix)

    def get_url_properties(self, prefix):
        provider = KuBURLDocPropertyProvider(self.organization_or_person)
        return provider.get_properties(prefix)


class KuBContactDocPropertyProvider(BaseDocPropertyProvider):
    """Doc property provider for contacts."""

    DEFAULT_PREFIX = ('contact',)

    def _collect_properties(self):
        return {
            'title': self.context.get("text"),
            'description': self.context.get("description"),
        }


class KuBPersonDocPropertyProvider(BaseDocPropertyProvider):

    DEFAULT_PREFIX = ('person',)

    def _collect_properties(self):
        return {
            'salutation': self.context.get("salutation"),
            'academic_title': self.context.get("title"),
            'firstname': self.context.get("firstName"),
            'lastname': self.context.get("officialName"),
        }


class KuBOrganizationDocPropertyProvider(BaseDocPropertyProvider):

    DEFAULT_PREFIX = ('organization',)

    def _collect_properties(self):
        return {'name': self.context.get("name")}


class KuBMembershipDocPropertyProvider(BaseDocPropertyProvider):
    """Provides doc-properties for an org-role and its associated person."""

    DEFAULT_PREFIX = ('orgrole',)

    def _collect_properties(self):
        return {
            'function': self.context.get("role"),
            'description': self.context.get("description"),
            'department': self.context.get("department"),
        }


class KuBAddressDocPropertyProvider(BaseDocPropertyProvider):
    """Provides doc-properties for an address."""

    DEFAULT_PREFIX = ('address',)

    def _collect_properties(self):
        address = self.context.get("primaryAddress") or {}
        return {
            'street': address.get("street"),
            'zip_code': address.get("swissZipCode"),
            'city': address.get("town"),
            'country': address.get("countryName"),
        }


class KuBEmailDocPropertyProvider(BaseDocPropertyProvider):
    """Provides doc-properties for a mail-address."""

    DEFAULT_PREFIX = ('email',)

    def _collect_properties(self):
        email = self.context.get("primaryEmail") or {}
        return {
            'address': email.get("email"),
        }


class KuBPhoneNumberDocPropertyProvider(BaseDocPropertyProvider):
    """Provides doc-properties for a phone-number."""

    DEFAULT_PREFIX = ('phone',)

    def _collect_properties(self):
        phone_number = self.context.get("primaryPhoneNumber") or {}
        return {
            'number': phone_number.get("phoneNumber"),
        }


class KuBURLDocPropertyProvider(BaseDocPropertyProvider):
    """Provides doc-properties for an url."""

    DEFAULT_PREFIX = ('url',)

    def _collect_properties(self):
        url = self.context.get("primaryUrl") or {}
        return {
            'url': url.get("url"),
        }
