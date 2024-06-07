from AccessControl.SecurityInfo import ClassSecurityInfo
from base64 import b64decode
from base64 import b64encode
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from logging import getLogger
from opengever.ogds.base.interfaces import IInternalOpengeverRequestLayer
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.ogds.models.service import ogds_service
from plone import api
from plone.protect.interfaces import IDisableCSRFProtection
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PluggableAuthService.interfaces.plugins import IAuthenticationPlugin  # noqa
from Products.PluggableAuthService.interfaces.plugins import IExtractionPlugin
from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from zope.annotation import IAnnotations
from zope.interface import alsoProvides
from zope.interface import implementer
import six
import time


logger = getLogger('AdminUnitAuthentication')

OGDS_ADMIN_UNIT_AUTH_PRIVATE_KEY_KEY = 'opengever.ogds.auth.admin_unit.private_key'
OGDS_ADMIN_UNIT_AUTH_TOKEN_TTL = 60

manage_addAdminUnitAuthenticationPlugin = PageTemplateFile(
    "www/addAdminUnitAuthPlugin", globals(), __name__="manage_addAdminUnitAuthenticationPlugin")


def addAdminUnitAuthenticationPlugin(self, id_, title=None, REQUEST=None):
    """Add an admin unit authentication plugin
    """
    plugin = AdminUnitAuthenticationPlugin(id_, title)
    acl_users = api.portal.get_tool('acl_users')
    acl_users._setObject(plugin.getId(), plugin)

    private_key, public_key = create_keypair()

    portal = api.portal.get()
    IAnnotations(portal)[OGDS_ADMIN_UNIT_AUTH_PRIVATE_KEY_KEY] = b64encode(private_key)

    admin_unit = get_current_admin_unit()
    admin_unit.public_key = b64encode(public_key)
    ogds_service().session.add(admin_unit)

    plugin = acl_users[plugin.getId()]
    plugin.manage_activateInterfaces([
        'IExtractionPlugin',
        'IAuthenticationPlugin',
    ])

    if REQUEST is not None:
        REQUEST["RESPONSE"].redirect(
            "%s/manage_workspace"
            "?manage_tabs_message=Admin+unit+authentication+plugin+added." %
            self.absolute_url()
        )


@implementer(IAuthenticationPlugin, IExtractionPlugin)
class AdminUnitAuthenticationPlugin(BasePlugin):
    """Plone PAS plugin for authentication of requests between admin units.
    """
    meta_type = 'AdminUnit Authentication Plugin'
    security = ClassSecurityInfo()

    def __init__(self, id_, title=None):
        self._setId(id_)
        self.title = title

    # IExtractionPlugin implementation
    # Extracts the authentication token from the X-OGDS-AC header
    def extractCredentials(self, request):
        creds = {}
        auth = request.get_header('X-OGDS-AC', None)
        if auth:
            creds['token'] = auth
        return creds

    # IAuthenticationPlugin implementation
    def authenticateCredentials(self, credentials):
        # Ignore credentials that are not from our extractor
        extractor = credentials.get('extractor')
        if extractor != self.getId():
            return None

        if 'token' not in credentials:
            return None

        userid = verify_auth_token(credentials['token'])

        pas = self._getPAS()
        info = pas._verifyUser(pas.plugins, user_id=userid)
        if info is None:
            logger.warning('No user found for userid %s', userid)
            return None

        activate_request_layer(self.REQUEST, IInternalOpengeverRequestLayer)
        activate_request_layer(self.REQUEST, IDisableCSRFProtection)

        return userid, info['login']


def create_auth_token(admin_unit_id, userid, timestamp=None):
    """Creates an authentication token for making requests to other admin units"""
    portal = api.portal.get()
    private_bytes = b64decode(
        IAnnotations(portal).get(OGDS_ADMIN_UNIT_AUTH_PRIVATE_KEY_KEY, '')
    )
    private_key = Ed25519PrivateKey.from_private_bytes(private_bytes)

    if timestamp is None:
        timestamp = '%08x' % int(time.time())

    admin_unit_id = six.ensure_binary(admin_unit_id)
    userid = six.ensure_binary(userid)
    message = ''.join([timestamp, admin_unit_id, userid])
    signature = private_key.sign(message)

    token = '%s%s%s!%s' % (signature, timestamp, admin_unit_id, userid)
    return b64encode(token)


def split_token(token):
    signature = token[:64]
    timestamp = token[64:72]
    remainder = token[72:]
    parts = remainder.split("!")

    try:
        timestamp = int(timestamp, 16)
    except ValueError:
        timestamp = 0

    if len(parts) == 2:
        admin_unit_id, userid = parts
    else:
        admin_unit_id, userid = None, None

    return signature, timestamp, admin_unit_id, userid


def verify_auth_token(token, ttl=60, now=None):
    try:
        token = b64decode(token)
    except TypeError:
        return None

    signature, timestamp, admin_unit_id, userid = split_token(token)

    if now is None:
        now = int(time.time())
    if timestamp + ttl < now:
        logger.info('Token expired')
        return None

    admin_unit = ogds_service().fetch_admin_unit(admin_unit_id)
    if admin_unit is None:
        return None
    public_key = Ed25519PublicKey.from_public_bytes(b64decode(admin_unit.public_key))
    message = ''.join(['%08x' % timestamp, admin_unit_id, userid])
    try:
        public_key.verify(signature, message)
    except InvalidSignature:
        logger.info('Invalid signature')
        return None
    return userid


def create_keypair():
    private_key = Ed25519PrivateKey.generate()
    private_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption(),
    )
    public_key = private_key.public_key()
    public_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )
    return private_bytes, public_bytes


def activate_request_layer(request, layer):
    if not layer.providedBy(request):
        alsoProvides(request, layer)
