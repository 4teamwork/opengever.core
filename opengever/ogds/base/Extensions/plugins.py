from opengever.ogds.base.interfaces import IContactInformation
from opengever.ogds.base.interfaces import IInternalOpengeverRequestLayer
from zope.component import getUtility
from zope.interface import alsoProvides


# IExtractionPlugin.extractCredentials
def extract_user(self, request):
    creds = {}
    # get ac and remote_address
    login = request.get_header('X-OGDS-AC', None)
    cid = request.get_header('X-OGDS-CID', None)
    remote_address = ''
    try:
        remote_address = request.getClientAddr()
    except AttributeError:
        pass
    # verify
    if login and remote_address and cid:
        creds['cid'] = cid
        creds['id'] = login
        creds['login'] = login
        creds['remote_address'] = remote_address
        creds['remote_host'] = request.get_header('REMOTE_HOST', '')
    return creds


# IAuthenticationPlugin.authenticateCredentials
def authenticate_credentials(self, credentials):
    uid = credentials['id']
    login = credentials['login']
    cid = credentials['cid'].strip()
    ip = credentials['remote_address'].strip()
    # is the client_id and the ip combination valid?
    info = getUtility(IContactInformation)
    client = info.get_client_by_id(cid)
    #split client.ip_address because they could be a comme seperated list
    if client and ip in client.ip_address.split(','):
        activate_request_layer(self.REQUEST, IInternalOpengeverRequestLayer)
        return uid, login
    return None


def activate_request_layer(request, layer):
    if not layer.providedBy(request):
        alsoProvides(request, layer)
