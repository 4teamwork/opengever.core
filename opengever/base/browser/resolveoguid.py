from AccessControl.SecurityManagement import SpecialUsers
from opengever.base.oguid import Oguid
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.ogds.base.utils import ogds_service
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from urllib import urlencode
from urlparse import parse_qsl
from zExceptions import Unauthorized
from zope.component import getUtility
from zope.interface import implementer
from zope.intid.interfaces import IIntIds
from zope.publisher.interfaces import IPublishTraverse


@implementer(IPublishTraverse)
class ResolveOGUIDView(BrowserView):
    """The view supports the following url formats:

    GET paramater: /fd/resolve_oguid?oguid=fd:123
    Traversal based paramater: /fd/resolve_oguid/fd:123
    Specific view: /fd/resolve_oguid/fd:123/tooltip

    Any query string parameters (in addition to a possible oguid) will
    be preserved.
    """

    oguid_str = None
    view_name = None
    key_to_strip = 'oguid'

    def publishTraverse(self, request, name):
        if self.oguid_str:
            self.view_name = name
        else:
            self.oguid_str = name

        return self

    @classmethod
    def url_for(cls, oguid, admin_unit=None, view_name=None):
        if not admin_unit:
            admin_unit = get_current_admin_unit()

        if view_name:
            return "{}/@@resolve_oguid/{}/{}".format(admin_unit.public_url,
                                                     oguid, view_name)

        return "{}/@@resolve_oguid?oguid={}".format(admin_unit.public_url,
                                                    oguid)

    @classmethod
    def _extend_with_querystring(cls, url, qs):
        """Given an URL and a querystring in the form 'key=value&foo=bar',
        extend the URL with the QS, taking into account that it may already
        contain one.
        """
        if url.endswith('?'):
            return ''.join((url, qs))
        return '?'.join((url, qs))

    @classmethod
    def _strip_parameter(cls, qs):
        """Given a query string in the form 'key=value&foo=bar', remove the
        oguid parameter from it if present.
        """
        # Preserve order as well as multivalued query string params
        qs_params = qs_params = [
            (k, v) for k, v in parse_qsl(qs) if k != cls.key_to_strip]
        return urlencode(qs_params)

    def _is_on_different_admin_unit(self, admin_unit_id):
        return admin_unit_id != get_current_admin_unit().id()

    def __call__(self):
        if not self.oguid_str:
            self.oguid_str = self.request.get('oguid')

        oguid = Oguid.parse(self.oguid_str)

        if self._is_on_different_admin_unit(oguid.admin_unit_id):
            admin_unit = ogds_service().fetch_admin_unit(oguid.admin_unit_id)
            url = self.url_for(oguid, admin_unit, self.view_name)

        else:
            obj = self._get_object(oguid.int_id)
            url = obj.absolute_url()
            if self.view_name:
                url = '/'.join((url, self.view_name))

        return self.request.RESPONSE.redirect(self.preserve_query_string(url))

    def preserve_query_string(self, url):
        qs = self.request.get('QUERY_STRING')
        qs = self._strip_parameter(qs)
        if qs:
            url = self._extend_with_querystring(url, qs)

        return url

    def _get_object(self, iid):
        intids = getUtility(IIntIds)
        obj = intids.getObject(int(iid))
        self._check_permissions(obj)
        return obj

    def _check_permissions(self, obj):
        mtool = getToolByName(self.context, 'portal_membership')
        member = mtool.getAuthenticatedMember()

        if member == SpecialUsers.nobody or \
                not member.checkPermission('View', obj):
            raise Unauthorized
