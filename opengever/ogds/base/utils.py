from datetime import datetime
from datetime import timedelta
from opengever.base.model import create_session
from opengever.ogds.base.interfaces import IAdminUnitConfiguration
from opengever.ogds.base.ou_selector import AnonymousOrgUnitSelector
from opengever.ogds.base.ou_selector import NoAssignedUnitsOrgUnitSelector
from opengever.ogds.base.ou_selector import OrgUnitSelector
from opengever.ogds.models.admin_unit import AdminUnit
from opengever.ogds.models.exceptions import RecordNotFound
from opengever.ogds.models.group import Group
from opengever.ogds.models.org_unit import OrgUnit
from opengever.ogds.models.user import User
from plone import api
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import IPloneSiteRoot
from sqlalchemy.sql.expression import true
from UserDict import DictMixin
from zope.component import getUtility
from zope.component.hooks import getSite
from zope.globalrequest import getRequest


EXPECTED_ENCODINGS = (
    'utf8',
    'iso-8859-1',
    'latin1',
    )


def ogds_service():
    return OGDSService(create_session())


class OGDSService(object):

    def __init__(self, session):
        self.session = session

    def _get_current_user_id(self):
        return api.user.get_current().getId()

    def fetch_current_user(self):
        userid = self._get_current_user_id()
        return self.fetch_user(userid) if userid else None

    def find_user(self, userid):
        """Returns a User by its userid. When no User is found, this method raises.
        a ValueError.

        See #fetch_user for similar behavior.
        """
        user = self.fetch_user(userid)
        if not user:
            raise RecordNotFound(User, userid)
        return user

    def fetch_user(self, userid):
        """Returns a User by it's userid. None is returned when no user is found.

        See #find_user for similar behavior.
        """
        return self._query_user().get(userid)

    def filter_users(self, query_string):
        return self._query_user().by_searchable_text(query_string)

    def all_users(self):
        return self._query_user().all()

    def inactive_users(self):
        return self._query_user().filter_by(active=False).all()

    def assigned_org_units(self, userid=None, omit_current=False):
        if userid is None:
            userid = self._get_current_user_id()

        query = self._query_org_units().join(OrgUnit.users_group)
        query = query.join(Group.users).filter(User.userid == userid)
        query = query.filter(OrgUnit.enabled == true())
        org_units = query.all()

        if omit_current:
            current_org_unit = get_current_org_unit()
            org_units = [each for each in org_units
                         if each != current_org_unit]
        return org_units

    def assigned_groups(self, userid):
        query = Group.query.join(Group.users)
        query = query.filter(User.userid == userid)
        return query.all()

    def fetch_org_unit(self, unit_id):
        return self._query_org_units().get(unit_id)

    def all_org_units(self, enabled_only=True):
        query = self._query_org_units()
        if enabled_only:
            query = query.filter_by(enabled=True)

        return query.all()

    def fetch_admin_unit(self, unit_id):
        return self._query_admin_units(enabled_only=False).get(unit_id)

    def all_admin_units(self, enabled_only=True):
        query = self._query_admin_units(enabled_only)
        return query.all()

    def has_multiple_admin_units(self, enabled_only=True):
        query = self._query_admin_units(enabled_only)
        return query.count() > 1

    def has_multiple_org_units(self):
        return self._query_org_units().count() > 1

    def fetch_group(self, groupid):
        return self._query_group().get(groupid)

    def _query_admin_units(self, enabled_only=True):
        query = AdminUnit.query
        if enabled_only:
            query = query.filter_by(enabled=enabled_only)
        return query

    def all_groups(self, active_only=True):
        query = self._query_group()
        if active_only:
            query = query.filter_by(active=True)
        return query.all()

    def _query_org_units(self):
        return OrgUnit.query.order_by(OrgUnit.title)

    def _query_user(self):
        return User.query

    def _query_group(self):
        return Group.query


class CookieStorage(DictMixin):
    """Helper object to store values on the request cookie.
    """

    def __init__(self, request):
        self.request = request

    def __getitem__(self, key):
        return self.request.cookies.get(key)

    def __setitem__(self, key, value):
        self.request.cookies[key] = value
        self.request.RESPONSE.setCookie(
            key, value, expires=self.expires, path='/')

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


def get_ou_selector(ignore_anonymous=False):
    site = api.portal.get()
    storage = CookieStorage(getRequest())
    mtool = getToolByName(site, 'portal_membership')
    member = mtool.getAuthenticatedMember()

    if mtool.isAnonymousUser() and not ignore_anonymous:
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
