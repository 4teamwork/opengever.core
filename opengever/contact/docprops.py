from opengever.base.docprops import BaseDocPropertyProvider


class ContactDocPropertyProvider(BaseDocPropertyProvider):
    """Doc property provider for contacts."""

    DEFAULT_PREFIX = ('contact',)

    def _collect_properties(self):
        return {
            'title': self.context.get_title(with_former_id=False),
            'description': self.context.description,
        }


class PersonDocPropertyProvider(BaseDocPropertyProvider):

    DEFAULT_PREFIX = ('person',)

    def _collect_properties(self):
        return {
            'salutation': self.context.salutation,
            'academic_title': self.context.academic_title,
            'firstname': self.context.firstname,
            'lastname': self.context.lastname,
        }

    def get_properties(self, prefix=None):
        return self._merge(
            super(PersonDocPropertyProvider, self).get_properties(prefix=prefix),
            ContactDocPropertyProvider(self.context).get_properties(prefix=prefix)
        )


class AddressDocPropertyProvider(BaseDocPropertyProvider):
    """Provides doc-properties for an address."""

    DEFAULT_PREFIX = ('address',)

    def _collect_properties(self):
        return {
            'street': self.context.street,
            'zip_code': self.context.zip_code,
            'city': self.context.city,
            'country': self.context.country,
        }


class MailAddressDocPropertyProvider(BaseDocPropertyProvider):
    """Provides doc-properties for a mail-address."""

    DEFAULT_PREFIX = ('email',)

    def _collect_properties(self):
        return {
            'address': self.context.address,
        }


class PhoneNumberDocPropertyProvider(BaseDocPropertyProvider):
    """Provides doc-properties for a phone-number."""

    DEFAULT_PREFIX = ('phone',)

    def _collect_properties(self):
        return {
            'number': self.context.phone_number,
        }


class URLDocPropertyProvider(BaseDocPropertyProvider):
    """Provides doc-properties for an url."""

    DEFAULT_PREFIX = ('url',)

    def _collect_properties(self):
        return {
            'url': self.context.url,
        }
