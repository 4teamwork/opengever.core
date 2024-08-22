from datetime import datetime
from opengever.base.addressblock.docprops import get_addressblock_docprops
from opengever.base.docprops import BaseDocPropertyProvider
from plone.registry.interfaces import IRegistry
from zope.component import getUtility


def get_additional_doc_properties():
    registry = getUtility(IRegistry)
    return registry['opengever.kub.interfaces.IKuBSettings.additional_docproperty_fields'] or []


def update_default_fields_with_additional_doc_props(context, default_fields):
    custom_values = context.get('customValues')
    if custom_values:
        for field in get_additional_doc_properties():
            if field in custom_values:
                default_fields.update({field: custom_values[field]})


class KuBEntityDocPropertyProvider(object):

    def __init__(self, entity):
        # avoid circular imports
        from opengever.kub.entity import KuBEntity

        self.entity = entity
        self.person = None
        self.organization = None
        self.membership = None
        if entity.is_person():
            self.person = entity
        elif entity.is_organization():
            self.organization = entity
        elif entity.is_membership():
            self.person = KuBEntity("person:" + entity["person"]["id"],
                                    data=entity["person"])
            self.organization = KuBEntity("organization:" + entity["organization"]["id"],
                                          data=entity["organization"])
            self.membership = entity

    @property
    def membership_person_or_organization(self):
        return self.membership or self.person or self.organization

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
        properties.update(self.get_address_block(prefix))
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
        provider = KuBAddressDocPropertyProvider(self.membership_person_or_organization)
        return provider.get_properties(prefix)

    def get_address_block(self, prefix):
        return get_addressblock_docprops(self.entity, prefix)

    def get_email_properties(self, prefix):
        provider = KuBEmailDocPropertyProvider(self.membership_person_or_organization)
        return provider.get_properties(prefix)

    def get_phone_properties(self, prefix):
        provider = KuBPhoneNumberDocPropertyProvider(self.membership_person_or_organization)
        return provider.get_properties(prefix)

    def get_url_properties(self, prefix):
        provider = KuBURLDocPropertyProvider(self.membership_person_or_organization)
        return provider.get_properties(prefix)


class KuBContactDocPropertyProvider(BaseDocPropertyProvider):
    """Doc property provider for contacts."""

    DEFAULT_PREFIX = ('contact',)

    def _collect_properties(self):
        default_fields = {
            'title': self.context.get("text"),
            'description': self.context.get("description"),
        }
        update_default_fields_with_additional_doc_props(self.context, default_fields)
        return default_fields


class KuBPersonDocPropertyProvider(BaseDocPropertyProvider):

    DEFAULT_PREFIX = ('person',)

    def _collect_properties(self):
        date_of_birth = self.context.get('dateOfBirth')
        if date_of_birth:
            date_of_birth = datetime.strptime(date_of_birth, '%Y-%m-%d')
        default_fields = {
            'salutation': self.context.get("salutation"),
            'academic_title': self.context.get("title"),
            'firstname': self.context.get("firstName"),
            'lastname': self.context.get("officialName"),
            'date_of_birth': date_of_birth,
            'sex': self.context.get('sex'),
            'country': self.context.get('country'),
        }
        update_default_fields_with_additional_doc_props(self.context, default_fields)
        return default_fields


class KuBOrganizationDocPropertyProvider(BaseDocPropertyProvider):

    DEFAULT_PREFIX = ('organization',)

    def _collect_properties(self):
        properties = {
            'name': self.context.get("name"),
        }
        phone_provider = KuBPhoneNumberDocPropertyProvider(self.context)
        properties.update(phone_provider.get_properties(with_app_prefix=False))
        update_default_fields_with_additional_doc_props(self.context, properties)
        return properties


class KuBMembershipDocPropertyProvider(BaseDocPropertyProvider):
    """Provides doc-properties for an org-role and its associated person."""

    DEFAULT_PREFIX = ('orgrole',)

    def _collect_properties(self):
        default_fields = {
            'function': self.context.get("role"),
            'description': self.context.get("description"),
            'department': self.context.get("department"),
        }
        update_default_fields_with_additional_doc_props(self.context, default_fields)

        return default_fields


class KuBAddressDocPropertyProvider(BaseDocPropertyProvider):
    """Provides doc-properties for an address."""

    DEFAULT_PREFIX = ('address',)

    def _collect_properties(self):
        address = self.context.get("primaryAddress") or {}
        return {
            'extra_line_1': address.get("addressLine1"),
            'extra_line_2': address.get("addressLine2"),
            'street': u' '.join(filter(None, [
                address.get("street"),
                address.get("houseNumber"),
            ])),
            'zip_code': address.get("swissZipCode") or address.get('foreignZipCode'),
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
