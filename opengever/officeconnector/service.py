from opengever.document.document import IDocumentSchema
from opengever.officeconnector.helpers import is_officeconnector_attach_feature_enabled  # noqa
from opengever.officeconnector.helpers import is_officeconnector_checkout_feature_enabled  # noqa
from plone import api
from plone.protect.utils import addTokenToUrl
from plone.rest import Service
from Products.CMFCore.utils import getToolByName
from Products.PluggableAuthService.interfaces.plugins import IAuthenticationPlugin  # noqa
from zExceptions import NotFound

import json


class OfficeConnectorToken(Service):

    def create_officeconnector_url(self, payload):
        # Feature used wrong - an action is always required
        if 'action' not in payload:
            raise NotFound

        # Feature enabled for the wrong content type
        if not IDocumentSchema.providedBy(self.context):
            raise NotFound

        plugin = None
        acl_users = getToolByName(self.context, "acl_users")
        plugins = acl_users._getOb('plugins')
        authenticators = plugins.listPlugins(IAuthenticationPlugin)

        # Assumes there is only one JWT auth plugin present in the acl_users
        # which manages the user/session in question.
        #
        # This will work as long as the plugin this finds uses the same secret
        # as whatever it ends up authenticating against - this is in all
        # likelihood the Plone site keyring.
        for id_, authenticator in authenticators:
            if authenticator.meta_type == "JWT Authentication Plugin":
                plugin = authenticator
                break

        if not plugin:
            raise NotFound

        payload['download'] = addTokenToUrl('/'.join([self.context.absolute_url(), 'download_file_version'])) # noqa

        # Attach the file info if this is a file
        filename = self.context.get_filename()
        if filename:
            payload['filename'] = filename
            payload['content-type'] = self.context.file.contentType

        user_id = api.user.get_current().getId()
        response = {}
        response['token'] = plugin.create_token(user_id, data=payload)

        return json.dumps(response)


class OfficeConnectorAttachToken(OfficeConnectorToken):

    def render(self):
        # Feature disabled or used wrong
        if not is_officeconnector_attach_feature_enabled():
            raise NotFound
        payload = {'action': 'attach'}
        return self.create_officeconnector_url(payload)


class OfficeConnectorCheckoutToken(OfficeConnectorToken):

    def render(self):
        # Feature disabled or used wrong
        if not is_officeconnector_checkout_feature_enabled():
            raise NotFound

        payload = {'action': 'checkout'}

        return self.create_officeconnector_url(payload)
