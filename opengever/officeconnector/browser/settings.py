from opengever.officeconnector.helpers import is_officeconnector_attach_as_pdf_feature_enabled
from opengever.officeconnector.helpers import is_officeconnector_attach_feature_enabled
from opengever.officeconnector.helpers import is_officeconnector_checkout_feature_enabled
from opengever.officeconnector.helpers import is_officeconnector_restapi_feature_enabled
from opengever.officeconnector.interfaces import IOfficeConnectorSettingsView
from plone.memoize.view import memoize_contextless
from Products.Five import BrowserView
from zope.interface import implements


class SettingsView(BrowserView):
    """Provide memoized browser views to check registry settings in templates.

    Currently provides views for the registry flags.
    """

    implements(IOfficeConnectorSettingsView)

    @memoize_contextless
    def is_attach_enabled(self):
        return is_officeconnector_attach_feature_enabled()

    @memoize_contextless
    def is_checkout_enabled(self):
        return is_officeconnector_checkout_feature_enabled()

    @memoize_contextless
    def is_restapi_enabled(self):
        return is_officeconnector_restapi_feature_enabled()

    @memoize_contextless
    def is_attach_as_pdf_enabled(self):
        return is_officeconnector_attach_as_pdf_feature_enabled()
