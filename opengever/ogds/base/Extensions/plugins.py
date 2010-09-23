from opengever.ogds.base.interfaces import IContactInformation
from zope.component import getUtility


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
    if client and client.client_id == cid and client.ip_address == ip:
        return uid, login
    return None
