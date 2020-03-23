from opengever.ogds.base.interfaces import IInternalOpengeverRequestLayer
from opengever.ogds.models.service import ogds_service
from plone.protect.interfaces import IDisableCSRFProtection
from zope.interface import alsoProvides


# IExtractionPlugin.extractCredentials
def extract_user(self, request):
    creds = {}
    # get ac and remote_address
    login = request.get_header('X-OGDS-AC', None)
    auid = request.get_header('X-OGDS-AUID', None)
    remote_address = ''
    try:
        remote_address = request.getClientAddr()
    except AttributeError:
        pass
    # verify
    if login and remote_address and auid:
        creds['auid'] = auid
        creds['id'] = login
        creds['login'] = login
        creds['remote_address'] = remote_address
        creds['remote_host'] = request.get_header('REMOTE_HOST', '')
    return creds


# IAuthenticationPlugin.authenticateCredentials
def authenticate_credentials(self, credentials):
    uid = credentials.get('id')
    if uid is None:
        # Not one of our internal requests
        return None
    login = credentials['login']
    auid = credentials['auid'].strip()
    ip = credentials['remote_address'].strip()
    # is the client_id and the ip combination valid?
    admin_unit = ogds_service().fetch_admin_unit(auid)
    # split client.ip_address because they could be a comme seperated list
    if admin_unit and ip in admin_unit.ip_address.split(','):
        activate_request_layer(self.REQUEST, IInternalOpengeverRequestLayer)
        activate_request_layer(self.REQUEST, IDisableCSRFProtection)
        return uid, login
    return None


def activate_request_layer(request, layer):
    if not layer.providedBy(request):
        alsoProvides(request, layer)
