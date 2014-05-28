from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import IPloneSiteRoot
from StringIO import StringIO
from opengever.ogds.base.exceptions import ClientNotFound
from opengever.ogds.base.interfaces import IClientConfiguration
from opengever.ogds.base.interfaces import IContactInformation
from opengever.ogds.base.ou_selector import AnonymousOrgUnitSelector
from opengever.ogds.base.ou_selector import NoAssignedUnitsOrgUnitSelector
from opengever.ogds.base.ou_selector import OrgUnitSelector
from opengever.ogds.models.client import Client
from opengever.ogds.models.service import OGDSService
from plone.memoize import ram
from plone.registry.interfaces import IRegistry
from z3c.saconfig import named_scoped_session
from zope.app.component.hooks import getSite, setSite
from zope.component import getUtility
from zope.globalrequest import getRequest
import json
import os.path
import urllib
import urllib2


EXPECTED_ENCODINGS = (
    'utf8',
    'iso-8859-1',
    'latin1',
    )


Session = named_scoped_session('opengever')


def create_session():
    """Returns a new sql session bound to the defined named scope.
    """
    return Session()


def ogds_service():
    return OGDSService(create_session())


def get_current_client():
    """Returns the current client.
    """

    session = create_session()
    client_id = get_client_id()

    if not client_id:
        raise ValueError('No client configured')

    client = session.query(Client).get(client_id)
    if not client:
        raise ValueError('Current client not found')
    return client


def get_ou_selector():
    site = getSite()
    sdm = site.session_data_manager
    storage = sdm.getSessionData(create=True)
    mtool = getToolByName(site, 'portal_membership')
    member = mtool.getAuthenticatedMember()

    if mtool.isAnonymousUser():
        return AnonymousOrgUnitSelector()

    if member.has_role('Manager'):
        units = ogds_service().all_org_units()
    else:
        units = ogds_service().assigned_org_units(member.getId())

    if not units:
        return NoAssignedUnitsOrgUnitSelector()

    return OrgUnitSelector(storage, units)


def client_id_cachekey(method):
    """chackekey for the get_client_id, wich is unique for every plone site.
    So a setup with multiple opengever sites on one plone instance is possible.
    """
    context = getSite()

    if not IPloneSiteRoot.providedBy(context):
        for obj in context.aq_chain:
            if IPloneSiteRoot.providedBy(obj):
                context = obj
                break

    return 'get_client_id:%s' % (context.id)


def get_current_org_unit():
    return get_ou_selector().get_current_unit()

# @ram.cache(client_id_cachekey)
def get_client_id():
    """Returns the client_id of the current client.
    """
    return get_ou_selector().get_current_unit().id()

    # registry = getUtility(IRegistry)
    # proxy = registry.forInterface(IClientConfiguration)
    # return proxy.client_id


def client_public_url_cachekey(method):
    """chackekey for the get_client_public_url, wich is unique for every plone
    site. So a setup with multiple opengever sites on one plone instance is
    possible.
    """

    context = getSite()

    if not IPloneSiteRoot.providedBy(context):
        for obj in context.aq_chain:
            if IPloneSiteRoot.providedBy(obj):
                context = obj
                break

    return 'get_client_public_url:%s' % (context.id)


@ram.cache(client_public_url_cachekey)
def get_client_public_url():
    """Returns the public_url of the current client.
    """

    return get_current_client().public_url


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


def brain_is_contact(brain):
    """Tests, if the object which the `brain` is of, is a contact
    object. The object is not touched, since the user may not have
    access.
    """

    iface = 'opengever.contact.contact.IContact'
    types_tool = getToolByName(getSite(), 'portal_types')
    fti = types_tool.get(brain.portal_type)

    # the iface is either defined as schema in the fti..
    if fti.schema == iface:
        return True

    # ..  or as a behavior
    elif iface in fti.behaviors:
        return True

    else:
        return False


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
    if isinstance(path, unicode):
        path = path.encode('utf-8')

    site = getSite()

    if get_client_id() == target_client_id:
        # do not connect to the site itself but do a restrictedTraverse
        request = getRequest()

        # we need to back up the request data and set them new for the
        # view which is called with the same request (restrictedTraverse)
        ori_form = request.form
        ori_other = request.other
        request.form = data
        request.other = ori_other.copy()
        for key in ori_form.keys():
            if key in request.other:
                del request.other[key]

        # kss validation overrides getSite() hook with a bad object
        # but we need getSite to work properly, so we fix it.
        old_site = None
        if site.__class__.__name__ == 'Z3CFormValidation':
            old_site = site
            fixed_site = getToolByName(site, 'portal_url').getPortalObject()
            setSite(fixed_site)

        site = getSite()
        if path:
            view = site.restrictedTraverse(os.path.join(path, viewname))
        else:
            view = site.restrictedTraverse(viewname)
        data = view()

        if old_site:
            # Restore the site if necessary
            site = old_site
            setSite(site)

        # restore the request
        request.form = ori_form
        request.other = ori_other

        return StringIO(data)

    site = getSite()
    info = getUtility(IContactInformation)
    target = info.get_client_by_id(target_client_id)

    if not target:
        raise ClientNotFound()

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


def decode_for_json(value, additional_encodings=[]):
    """ Json does not handle encodings, so we need to convert any strings in
    unicode in a way which allows to convert it back on the receiver.
    """

    if additional_encodings:
        encodings = list(EXPECTED_ENCODINGS) + list(additional_encodings)
    else:
        encodings = EXPECTED_ENCODINGS

    # unicode
    if isinstance(value, unicode):
        return u'unicode:' + value

    # encoded strings
    elif isinstance(value, str):
        for enc in encodings:
            try:
                return unicode(enc) + u':' + value.decode(enc)
            except UnicodeDecodeError:
                pass
        raise

    # lists, tuples, sets
    elif type(value) in (list, tuple, set):
        nval = []
        for sval in value:
            nval.append(decode_for_json(sval))
        if isinstance(value, tuple):
            return tuple(nval)
        if isinstance(value, set):
            return set(nval)
        return nval

    # dicts
    elif isinstance(value, dict):
        nval = {}
        for key, sval in value.items():
            key = decode_for_json(key)
            sval = decode_for_json(sval)
            nval[key] = sval
        return nval

    # others
    else:
        return value


def encode_after_json(value):
    """ Is the opposite of decode_for_json
    """

    # there should not be any encoded strings
    if isinstance(value, str):
        value = unicode(value)

    # unicode
    if isinstance(value, unicode):
        encoding, nval = unicode(value).split(':', 1)
        if encoding == u'unicode':
            return nval
        else:
            return nval.encode(encoding)

    # lists, tuples, sets
    elif type(value) in (list, tuple, set):
        nval = []
        for sval in value:
            nval.append(encode_after_json(sval))
        if isinstance(value, tuple):
            return tuple(nval)
        elif isinstance(value, set):
            return set(nval)
        else:
            return nval

    # dicts
    elif isinstance(value, dict):
        nval = {}
        for key, sval in value.items():
            key = encode_after_json(key)
            sval = encode_after_json(sval)
            nval[key] = sval
        return nval

    # other types
    else:
        return value
