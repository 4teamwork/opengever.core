from datetime import datetime
from datetime import timedelta
from opengever.core.model import create_session
from opengever.ogds.base.interfaces import IAdminUnitConfiguration
from opengever.ogds.base.ou_selector import AnonymousOrgUnitSelector
from opengever.ogds.base.ou_selector import NoAssignedUnitsOrgUnitSelector
from opengever.ogds.base.ou_selector import OrgUnitSelector
from opengever.ogds.models.service import OGDSService
from plone import api
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import IPloneSiteRoot
from UserDict import DictMixin
from zope.app.component.hooks import getSite
from zope.component import getUtility
from zope.globalrequest import getRequest


EXPECTED_ENCODINGS = (
    'utf8',
    'iso-8859-1',
    'latin1',
    )


def ogds_service():
    return PloneOGDSService(create_session())


class PloneOGDSService(OGDSService):
    """Extends ogds-service with plone and opengever.core specific methods.

    """
    def _get_current_user_id(self):
        return api.user.get_current().getId()

    def fetch_current_user(self):
        userid = self._get_current_user_id()
        return self.fetch_user(userid) if userid else None

    def assigned_org_units(self, userid=None, omit_current=False):
        if userid is None:
            userid = self._get_current_user_id()
        org_units = super(PloneOGDSService, self).assigned_org_units(userid)
        if omit_current:
            current_org_unit = get_current_org_unit()
            org_units = [each for each in org_units
                         if each != current_org_unit]
        return org_units


class CookieStorage(DictMixin):
    """Helper object to store values on the request cookie.
    """

    def __init__(self, request):
        self.request = request

    def __getitem__(self, key):
        return self.request.cookies.get(key)

    def __setitem__(self, key, value):
        self.request.cookies[key] = value
        self.request.RESPONSE.setCookie(key, value, expires=self.expires)

    def __delitem__(self, key):
        del self.request.cookies[key]
        self.request.RESPONSE.expireCookie(key)

    def keys(self):
        return self.request.cookies.keys()

    @property
    def expires(self):
        max_age = timedelta(days=30)
        expiration_date = datetime.now() + max_age
        return expiration_date.strftime("%a, %d-%b-%Y %H:%M:%S GMT")


def get_ou_selector():
    site = api.portal.get()
    storage = CookieStorage(getRequest())
    mtool = getToolByName(site, 'portal_membership')
    member = mtool.getAuthenticatedMember()

    if mtool.isAnonymousUser():
        return AnonymousOrgUnitSelector()

    if member.has_role('Manager'):
        users_units = ogds_service().all_org_units()
    else:
        users_units = ogds_service().assigned_org_units(member.getId())

    admin_unit_units = get_current_admin_unit().org_units

    if not admin_unit_units:
        return NoAssignedUnitsOrgUnitSelector()

    return OrgUnitSelector(storage, admin_unit_units, users_units)


def admin_unit_cachekey(method):
    """chackekey for `get_current_admin_unit` wich is unique for every plone
    site. This makes a setup with multiple opengever sites on one zope
    possible.

    """
    context = getSite()

    if not IPloneSiteRoot.providedBy(context):
        for obj in context.aq_chain:
            if IPloneSiteRoot.providedBy(obj):
                context = obj
                break

    return 'get_current_admin_unit:%s' % (context.id)


def get_current_org_unit():
    return get_ou_selector().get_current_unit()


# @ram.cache(admin_unit_cachekey)
def get_current_admin_unit():
    registry = getUtility(IRegistry)
    proxy = registry.forInterface(IAdminUnitConfiguration)
    return ogds_service().fetch_admin_unit(proxy.current_unit_id)


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
