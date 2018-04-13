from AccessControl.SecurityManagement import SpecialUsers
from opengever.base.oguid import Oguid
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.ogds.base.utils import ogds_service
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
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
    """

    oguid_str = None
    view_name = None

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

        return self.request.RESPONSE.redirect(url)

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
