from Acquisition import aq_inner
from Acquisition import aq_parent
from opengever.base.ip_range import is_in_ip_range
from opengever.base.sentry import log_msg_to_sentry
from opengever.document.behaviors import IBaseDocument
from opengever.officeconnector.interfaces import IOfficeConnectorSettings
from plone import api
from Products.CMFCore.utils import getToolByName
from Products.PluggableAuthService.interfaces.plugins import IAuthenticationPlugin  # noqa
from ua_parser.user_agent_parser import ParseUserAgent
from zExceptions import Forbidden
from zExceptions import NotFound
from zope.globalrequest import getRequest
import json


def is_officeconnector_attach_feature_enabled():
    return api.portal.get_registry_record(
        'attach_to_outlook_enabled',
        interface=IOfficeConnectorSettings,
        )


def is_officeconnector_checkout_feature_enabled():
    return api.portal.get_registry_record(
        'direct_checkout_and_edit_enabled',
        interface=IOfficeConnectorSettings,
        )


def is_client_ip_in_office_connector_disallowed_ip_ranges():
    request = getRequest()
    client_ip = request.getClientAddr()
    if not client_ip:
        # If for some reason we cannot determine the client_ip, we
        # cannot check whether office connector should be disallowed
        # for this request. This could be a problem with the configuration
        # of trusted proxies.
        log_msg_to_sentry('Cannot determine client IP.', request=request)
        return False

    blacklisted_ip_ranges = api.portal.get_registry_record(
        'office_connector_disallowed_ip_ranges',
        interface=IOfficeConnectorSettings,
        )
    return is_in_ip_range(client_ip, blacklisted_ip_ranges)


def parse_bcc(request):
    body = request.get('BODY', None)
    if body and 'bcc' in body:
        return json.loads(body).get('bcc', None)
    return None


def parse_documents(request, context, action):
    documents = []
    if (
            request['REQUEST_METHOD'] == 'GET'
            or request['REQUEST_METHOD'] == 'POST'
            and ('BODY' not in request
                 or isinstance(json.loads(request['BODY']), list))
        ):
        # Feature enabled for the wrong content type
        if not IBaseDocument.providedBy(context):
            raise NotFound

        # for checkout and attach actions, the document needs to have a file
        # for the oneoffixx action or checkout action fetched from
        # OfficeConnectorOneOffixxPayload, the document should be in the shadow state
        if not (context.has_file() or context.is_shadow_document()):
            raise NotFound

        documents.append(context)

    elif request['REQUEST_METHOD'] == 'POST' and 'BODY' in request:
        payload = json.loads(request['BODY'])
        paths = payload.get('documents', None)

        for path in paths:
            # Restricted traversal does not handle unicode paths
            document = api.content.get(path=str(path))

            if document.has_file():
                documents.append(document)

    return documents


def get_auth_plugin(context):
    plugin = None
    acl_users = None

    parent = aq_inner(context)

    while not acl_users:
        acl_users_candidate = getToolByName(parent, 'acl_users')
        # We've found the an acl_users for our user
        if acl_users_candidate:
            # And it also yielded a valid user
            if acl_users_candidate._verifyUser(
                    acl_users_candidate.plugins,
                    user_id=api.user.get_current().id,
                ):
                acl_users = acl_users_candidate
                break

        # We've searched everywhere without finding anything
        if parent is context.getPhysicalRoot():
            break

        # Did not find anything, go up one level and try again
        parent = aq_parent(parent)

    if acl_users:
        plugins = acl_users.plugins
        authenticators = plugins.listPlugins(IAuthenticationPlugin)

        # Assumes there is only one JWT auth plugin present in the acl_users
        # which manages the user/session in question.
        #
        # This will work as long as the plugin this finds uses the same secret
        # as whatever it ends up authenticating against - this is in all
        # likelihood the Plone site keyring.
        for authenticator in (a[1] for a in authenticators):
            if authenticator.meta_type == "JWT Authentication Plugin":
                plugin = authenticator
                break

    return plugin


def create_oc_url(request, context, payload):
    auth_plugin = get_auth_plugin(context)

    if not auth_plugin:
        raise Forbidden

    action = payload.get('action', None)

    # Feature used wrong - an action is always required
    if not action:
        raise NotFound

    bcc = parse_bcc(request)

    documents = parse_documents(request, context, action)

    if not documents:
        raise NotFound

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

    if bcc:
        payload['bcc'] = bcc

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

    return None
