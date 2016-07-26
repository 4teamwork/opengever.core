from opengever.contact import _
from opengever.contact.browser.related_entity import RelatedEntityCRUDView
from opengever.contact.models.mailaddress import MailAddress
from plone import api


class MailAddressesView(RelatedEntityCRUDView):

    model = MailAddress
    contact_backref_name = 'mail_addresses'

    @property
    def attributes(self):
        """A list of all attribute names(String) which are definable.
        """
        return ['label', 'address']

    def _validate(self, **kwargs):
        """Validates the given attributes.

        Returns None if the validation passed.
        Returns the errormessage if the validation failed.
        """
        label = kwargs.get('label')
        mailaddress = kwargs.get('address')

        plone_utils = api.portal.get_tool('plone_utils')

        if not label and not mailaddress:
            return _(
                u'error_no_label_and_email',
                u'Please specify a label and an email address.'
            )

        elif not label:
            return _(
                u'error_no_label',
                u'Please specify a label for your email address')

        elif not mailaddress:
            return _(
                u'error_no_email', u'Please specify an email address')

        elif not plone_utils.validateSingleEmailAddress(mailaddress):
            return _(
                u'error_invalid_email',
                u'Please specify a valid email address')
