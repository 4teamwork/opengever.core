from opengever.contact import _
from opengever.contact.browser.related_entity import RelatedEntityCRUDView
from opengever.contact.models import URL


class URLsView(RelatedEntityCRUDView):

    model = URL
    contact_backref_name = 'urls'

    @property
    def attributes(self):
        """A list of all attribute names(String) which are definable.
        """
        return ['label', 'url']

    def _validate(self, **kwargs):
        """Validates the given attributes.

        Returns None if the validation passed.
        Returns the errormessage if the validation failed.
        """
        if not kwargs.get('url'):
            return _(
                u'error_no_url', u'Please specify an url')
