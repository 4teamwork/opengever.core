from AccessControl.SecurityManagement import SpecialUsers
from opengever.base.oguid import Oguid
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.ogds.base.utils import ogds_service
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from zExceptions import Unauthorized
from zope.component import getUtility
from zope.intid.interfaces import IIntIds


class ResolveOGUIDView(BrowserView):

    @classmethod
    def url_for(cls, oguid, admin_unit=None):
        if not admin_unit:
            admin_unit = get_current_admin_unit()

        return "{}/@@resolve_oguid?oguid={}".format(admin_unit.public_url,
                                                    oguid)

    def _is_on_different_admin_unit(self, admin_unit_id):
        return admin_unit_id != get_current_admin_unit().id()

    def __call__(self):
        oguid = Oguid.parse(self.request.get('oguid'))

        if self._is_on_different_admin_unit(oguid.admin_unit_id):
            admin_unit = ogds_service().fetch_admin_unit(oguid.admin_unit_id)
            url = self.url_for(oguid, admin_unit)
            return self.request.RESPONSE.redirect(url)

        obj = self._get_object(oguid.int_id)
        return self.request.RESPONSE.redirect(obj.absolute_url())

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
