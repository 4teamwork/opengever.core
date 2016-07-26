from opengever.contact.browser.related_entity import RelatedEntityCRUDView
from opengever.contact.models import Address


class AddressesView(RelatedEntityCRUDView):

    model = Address
    contact_backref_name = 'addresses'

    @property
    def attributes(self):
        """A list of all attribute names(String) which are definable.
        """
        return ['label', 'street', 'zip_code', 'city']
