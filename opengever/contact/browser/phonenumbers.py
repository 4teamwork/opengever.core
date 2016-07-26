from opengever.contact import _
from opengever.contact.browser.related_entity import RelatedEntityCRUDView
from opengever.contact.models import PhoneNumber


class PhoneNumbersView(RelatedEntityCRUDView):

    model = PhoneNumber
    contact_backref_name = 'phonenumbers'

    @property
    def attributes(self):
        """A list of all attribute names(String) which are definable.
        """
        return ['label', 'phone_number']

    def _validate(self, **kwargs):
        """Validates the given attributes.

        Returns None if the validation passed.
        Returns the errormessage if the validation failed.
        """
        if not kwargs.get('phone_number'):
            return _(
                u'error_no_phonenumber', u'Please specify an phone number')
