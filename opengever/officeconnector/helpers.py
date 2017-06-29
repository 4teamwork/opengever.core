from opengever.document.behaviors import IBaseDocument
from opengever.officeconnector.interfaces import IOfficeConnectorSettings
from plone import api
from Products.CMFCore.utils import getToolByName
from Products.PluggableAuthService.interfaces.plugins import IAuthenticationPlugin  # noqa
from ua_parser.user_agent_parser import ParseUserAgent
from zExceptions import Forbidden
from zExceptions import NotFound

import json


def is_officeconnector_attach_feature_enabled():
    return api.portal.get_registry_record('attach_to_outlook_enabled',
                                          interface=IOfficeConnectorSettings)


def is_officeconnector_checkout_feature_enabled():
    return api.portal.get_registry_record('direct_checkout_and_edit_enabled',
                                          interface=IOfficeConnectorSettings)


def parse_documents(request, context):
    documents = []

    if (request['REQUEST_METHOD'] == 'GET' or
            request['REQUEST_METHOD'] == 'POST' and 'BODY' not in request):
        # Feature enabled for the wrong content type
        if not IBaseDocument.providedBy(context):
            raise NotFound

        if not context.has_file():
            raise NotFound

        documents.append(context)

    if request['REQUEST_METHOD'] == 'POST' and 'BODY' in request:

        paths = json.loads(request['BODY'])
        for path in paths:
            # Restricted traversal does not handle unicode paths
            document = api.content.get(path=str(path))
            if document.has_file():
                documents.append(document)

    return documents


def get_auth_plugin(context):
    plugin = None
    acl_users = getToolByName(context, "acl_users")
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

    return plugin


def create_oc_url(request, context, payload):
    # Feature used wrong - an action is always required
    if 'action' not in payload:
        raise NotFound

    documents = parse_documents(request, context)

    if not documents:
        raise NotFound

    auth_plugin = get_auth_plugin(context)

    if not auth_plugin:
        raise Forbidden

    # Create a JWT for OfficeConnector - contents:
    # action - tells OfficeConnector which code path to take
    # url - tells OfficeConnector where from to fetch further instructions

    payload['url'] = '/'.join((
        api.portal.get().absolute_url(),
        'oc_' + payload['action'],
        ))

    # Create a multi-document payload
    payload['documents'] = []

    for document in documents:
        payload['documents'].append(api.content.get_uuid(document))

    user_id = api.user.get_current().getId()

    token = auth_plugin.create_token(user_id, data=payload)

    # https://blogs.msdn.microsoft.com/ieinternals/2014/08/13/url-length-limits/
    # IE11 only allows up to 507 characters for Application Protocols.
    #
    # This is eaten into by both the protocol identifier and the payload.
    #
    # In testing we've discovered for this to be a bit fuzzy and gotten
    # arbitrary and inconsistent results of 506..509.
    #
    # For operational safety we've set the total url + separator + payload
    # limit at 500 or 2000 characters.
    url = 'oc:' + token
    user_agent = ParseUserAgent(request.environ.get('HTTP_USER_AGENT', ''))

    if user_agent['family'] == u'IE' and user_agent['major'] == '11':
        limit = 500
    else:
        limit = 2000

    if len(url) <= limit:
        return url
    else:
        return None
