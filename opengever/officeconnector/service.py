from opengever.document.document import IDocumentSchema
from opengever.officeconnector.helpers import is_officeconnector_attach_feature_enabled  # noqa
from opengever.officeconnector.helpers import is_officeconnector_checkout_feature_enabled  # noqa
from plone import api
from plone.rest import Service
from Products.CMFCore.utils import getToolByName
from Products.PluggableAuthService.interfaces.plugins import IAuthenticationPlugin  # noqa
from zExceptions import Forbidden
from zExceptions import NotFound

import json


class OfficeConnectorURL(Service):
    """Create oc:<JWT> URLs for javascript to fetch and pass to the OS."""

    def create_officeconnector_url(self, payload):
        # Feature used wrong - an action is always required
        if 'action' not in payload:
            raise NotFound

        # Feature enabled for the wrong content type
        if not IDocumentSchema.providedBy(self.context):
            raise NotFound

        if not self.context.file:
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
            raise Forbidden

        # Create a JWT for OfficeConnector - contents:
        # action - tells OfficeConnector which code path to take
        # url - tells OfficeConnector where from to fetch further instructions
        payload['url'] = '/'.join([
            api.portal.get().absolute_url(),
            'oc_' + payload['action'],
            api.content.get_uuid(self.context),
            ])
        user_id = api.user.get_current().getId()
        token = plugin.create_token(user_id, data=payload)

        # https://blogs.msdn.microsoft.com/ieinternals/2014/08/13/url-length-limits/
        # IE11 only allows up to 507 characters for Application Protocols.
        #
        # This is eaten into by both the protocol identifier and the payload.
        #
        # In testing we've discovered for this to be a bit fuzzy and gotten
        # arbitrary and inconsistent results of 506..509.
        #
        # For operational safety we've set the total url + separator + payload
        # limit at 500 characters.
        url = 'oc:' + token
        self.request.response.setHeader('Content-type', 'application/json')
        if len(url) <= 500:
            return json.dumps(dict(url=url))
        else:
            self.request.response.setStatus(500)
            return json.dumps(dict(error=dict(
                type='Generated URL too long',
                message='The URL is too long for IE11',
            )))


class OfficeConnectorAttachURL(OfficeConnectorURL):
    """Create oc:<JWT> URLs for javascript to fetch and pass to the OS.

    Instruct where to fetch an OfficeConnector 'attach' action payload for this
    document.
    """

    def render(self):
        # Feature disabled or used wrong
        if not is_officeconnector_attach_feature_enabled():
            raise NotFound
        payload = {'action': 'attach'}
        return self.create_officeconnector_url(payload)


class OfficeConnectorCheckoutURL(OfficeConnectorURL):
    """Create oc:<JWT> URLs for javascript to fetch and pass to the OS.

    Instruct where to fetch an OfficeConnector 'checkout' action payload for
    this document.
    """

    def render(self):
        # Feature disabled or used wrong
        if not is_officeconnector_checkout_feature_enabled():
            raise NotFound

        payload = {'action': 'checkout'}

        return self.create_officeconnector_url(payload)
