from opengever.officeconnector.helpers import create_oc_url
from opengever.officeconnector.helpers import is_officeconnector_checkout_feature_enabled  # noqa
from Products.Five import BrowserView


class RedirectToOCCheckoutURL(BrowserView):
    """Redirects to the oc:<JWT> checkout URL for this document.
    """
    def __call__(self):
        if (is_officeconnector_checkout_feature_enabled()
                and self.context.is_checkout_and_edit_available()):
            payload = {'action': 'checkout'}
            url = create_oc_url(self.request, self.context, payload)
            return self.request.RESPONSE.redirect(url)

        # Redirect to document view in any failure case
        return self.request.RESPONSE.redirect(self.context.absolute_url())
