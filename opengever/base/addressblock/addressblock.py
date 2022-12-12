from opengever.base.addressblock.interfaces import IAddressBlockData
from zope.interface import implementer


@implementer(IAddressBlockData)
class AddressBlockData(object):
    """Holds structured data intended to render a formatted address block.

    The `format()` method will attempt to render a postal address for the
    given data as best as possible. Depending on which fields are present, it
    will determine what type of address to render:

    - business address vs. private
    - addressed to an organisation, or an individual person at that organization
    - PO box address or street address
    - domestic address or international address

    The formatting of these types of addresses mostly follows the guidelines
    for domestic parcels by the Swiss Post:
    https://www.post.ch/de/briefe-versenden/adressieren-und-gestalten/sendungen-richtig-adressieren  # noqa

    The only exceptions are that Domiziladressen / Unteradressen as well as
    extra address lines (Adresszusatz or c/o addresses) are not supported or
    handled yet.
    """

    def __init__(self, **kwargs):
        # Person data
        self.salutation = kwargs.get('salutation')
        self.academic_title = kwargs.get('academic_title')
        self.first_name = kwargs.get('first_name')
        self.last_name = kwargs.get('last_name')

        # Org data
        self.org_name = kwargs.get('org_name')

        # Street or PO box
        self.street_and_no = kwargs.get('street_and_no')
        self.po_box = kwargs.get('po_box')

        # Postal code and city
        self.postal_code = kwargs.get('postal_code')
        self.city = kwargs.get('city')

        # Country
        self.country = kwargs.get('country')

    def is_business_address(self):
        return bool(self.org_name)

    def is_private_address(self):
        return not self.is_business_address()

    def is_individually_addressed(self):
        return bool(self.last_name)

    def is_po_box_address(self):
        return bool(self.po_box)

    def format(self):
        lines = []

        if self.is_private_address():
            # Private address:
            # Line 1 is salutation
            # Line 2 is person's full name, possibly preceeded by academic title
            if self.salutation:
                lines.append(self.salutation)
            lines.append(self.join_tokens(
                self.academic_title,
                self.first_name,
                self.last_name,
            ))
        else:
            # Business address:
            # Line 1 is company/org name
            lines.append(self.org_name)

            if self.is_individually_addressed():
                # Business address, addressed to a specific person:
                # Line 2 is the person's salutation, title, and full name
                lines.append(self.join_tokens(
                    self.salutation,
                    self.academic_title,
                    self.first_name,
                    self.last_name,
                ))

        if self.is_po_box_address():
            # Technically, an address could contain both Street+Number and a
            # PO box, from what I understand (Domiziladresse or Unteradresse).
            # These are rare / complicated cases however, and we should only
            # try to solve them once we have a clear use case / example.
            #
            # For now, we therefore use the presence of a value for po_box
            # as an indicator that the address should *only* contain the
            # PO box line, and drop the street_and_no in that case.
            lines.append(self.po_box)
        else:
            lines.append(self.street_and_no)

        lines.append(self.join_tokens(self.postal_code, self.city))

        # Never add 'Schweiz' to domestic addresses, even if part of data.
        if self.country:
            names = ['switzerland', 'schweiz', 'suisse', 'svizzera']
            if not any(name in self.country.lower() for name in names):
                lines.append(self.country)

        return u'\n'.join(lines)

    def join_tokens(self, *tokens):
        tokens = [t.strip() for t in tokens if t]
        return u' '.join(tokens)
