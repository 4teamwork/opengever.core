from Products.CMFCore.utils import getToolByName
from StringIO import StringIO
from opengever.ogds.base.exceptions import ClientNotFound
from opengever.ogds.base.interfaces import IClientConfiguration
from opengever.ogds.base.interfaces import IContactInformation
from opengever.ogds.base.model.client import Client
from plone.registry.interfaces import IRegistry
from z3c.saconfig import named_scoped_session
from zope.app.component.hooks import getSite
from zope.component import getUtility
import json
import os.path
import urllib
import urllib2


Session = named_scoped_session('opengever.ogds')


def create_session():
    """Returns a new sql session bound to the defined named scope.
    """

    return Session()


def get_current_client():
    """Returns the current client.
    """

    session = create_session()
    client_id = get_client_id()

    clients = session.query(Client).filter_by(client_id=client_id).all()
    if len(clients) == 0:
        raise ValueError('Current client not found')
    else:
        return clients[0]


def get_client_id():
    """Returns the client_id of the current client.
    """

    registry = getUtility(IRegistry)
    proxy = registry.forInterface(IClientConfiguration)
    return proxy.client_id


def remote_json_request(target_client_id, viewname, path='',
                        data={}, headers={}):
    """ Sends a request to a json-action on a remote zope instance,
    decodes the response with json and returns it.

    :target_client_id: remote client id
    :viewname: name of the view to call on the target
    :path: context path relative to site root
    :data: dict of additional data to send
    :headers: dict of additional headers to send
    """

    response = remote_request(target_client_id, viewname, path=path,
                              data=data, headers=headers)
    data = response.read()
    return json.loads(data)


def remote_request(target_client_id, viewname, path='', data={}, headers={}):
    """ Sends a request to another zope instance
    Returns a response stream

    Authentication:
    In the request there is a attribute '__cortex_ac' which is set to the
    username of the current user.

    :target_client_id: remote client id
    :viewname: name of the view to call on the target
    :path: context path relative to site root
    :data: dict of additional data to send
    :headers: dict of additional headers to send
    """

    if isinstance(viewname, unicode):
        viewname = viewname.encode('utf-8')

    site = getSite()
    request = site.REQUEST
    info = getUtility(IContactInformation)
    target = info.get_client_by_id(target_client_id)

    if not target:
        raise ClientNotFound()

    if request.URL.startswith(target.site_url) or \
            request.URL.startswith(target.public_url):
        # do not connect to the site itself but do a restrictedTraverse
        if path:
            view = site.restrictedTraverse(os.path.join(path, viewname))
        else:
            view = site.restrictedTraverse(viewname)
        data = view()
        return StringIO(data)

    headers = headers.copy()
    data = data.copy()

    mtool = getToolByName(site, 'portal_membership')
    member = mtool.getAuthenticatedMember()

    key = 'X-OGDS-AC'
    if key not in headers.keys() and member:
        headers[key] = member.getId()

    headers['X-OGDS-CID'] = get_client_id()
    handler = urllib2.ProxyHandler({})
    opener = urllib2.build_opener(handler)

    viewname = viewname.startswith('@@') and viewname or '@@%s' % viewname
    if path:
        url = os.path.join(target.site_url, path, viewname)
    else:
        url = os.path.join(target.site_url, viewname)

    request = urllib2.Request(url,
                              urllib.urlencode(data),
                              headers)
    return opener.open(request)
