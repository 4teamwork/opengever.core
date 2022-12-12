from opengever.base.addressblock import AddressBlockData
from opengever.base.addressblock.interfaces import IAddressBlockData
from opengever.contact.ogdsuser import OgdsUserToContactAdapter
from opengever.kub.entity import KuBEntity
from zope.component import adapter
from zope.interface import implementer


@implementer(IAddressBlockData)
@adapter(OgdsUserToContactAdapter)
def ogds_address_data_factory(context):
    return OGDSAddressDataExtractor(context)()


class OGDSAddressDataExtractor(object):
    """Extracts address data from an OGDS user as an IAddressBlockData.

    For technical reasons, this currently adapts an OgdsUserToContactAdapter
    instead of an OGDS User directly, because that's what ends up in the
    recipient_data / sender_data tuples.
    """

    def __init__(self, context):
        self.context = context

    def __call__(self):
        ogds_user = self.context.ogds_user

        return AddressBlockData(
            academic_title=None,
            org_name=None,
            po_box=None,

            salutation=ogds_user.salutation,
            first_name=ogds_user.firstname,
            last_name=ogds_user.lastname,

            street_and_no=ogds_user.address1,
            postal_code=ogds_user.zip_code,
            city=ogds_user.city,
            country=ogds_user.country,
        )


@implementer(IAddressBlockData)
@adapter(KuBEntity)
def kub_address_data_factory(context):
    return KuBAddressDataExtractor(context)()


class KuBAddressDataExtractor(object):
    """Extracts address data from a KuB entity as an IAddressBlockData.
    """

    def __init__(self, context):
        self.context = context

    def __call__(self):
        entity = self.context

        provider = entity.get_doc_property_provider()
        is_person = entity.is_person()
        is_organization = entity.is_organization()
        is_membership = entity.is_membership()

        # Organization name
        org_name = None
        if is_organization or is_membership:
            org_name = provider.organization.get('name')

        # Person name and details
        academic_title = None
        salutation = None
        first_name = None
        last_name = None

        if is_person or is_membership:
            academic_title = provider.person.get('title')
            salutation = provider.person.get('salutation')
            first_name = provider.person.get('firstName')
            last_name = provider.person.get('officialName')

        # Localization data (Street or PO Box, Postal Code, City)
        if is_organization or is_membership:
            addressed_location = provider.organization.get('primaryAddress', {})
        else:
            addressed_location = provider.person.get('primaryAddress', {})

        street = addressed_location.get('street')
        house_no = addressed_location.get('houseNumber')
        street_tokens = filter(None, [street, house_no])
        street_and_no = u' '.join(street_tokens)
        # XXX: KuB also shows 'dwellingNumber' and 'locality' in API, but
        # there's no way to edit those fields it seems.

        po_box = addressed_location.get('postOfficeBox')

        postal_code = addressed_location.get('swissZipCode')
        if not postal_code:
            postal_code = addressed_location.get('foreignZipCode')

        city = addressed_location.get('town')

        country = addressed_location.get('countryName')

        return AddressBlockData(
            org_name=org_name,

            academic_title=academic_title,
            salutation=salutation,
            first_name=first_name,
            last_name=last_name,

            street_and_no=street_and_no,
            po_box=po_box,

            postal_code=postal_code,
            city=city,
            country=country,
        )
