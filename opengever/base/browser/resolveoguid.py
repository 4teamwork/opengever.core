from AccessControl.SecurityManagement import SpecialUsers
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from five import grok
from opengever.ogds.base.utils import get_client_id
from zExceptions import NotFound
from zope.component import getUtility
from zope.intid.interfaces import IIntIds


class ResolveOGUIDView(grok.View):

    grok.name('resolve_oguid')
    grok.context(IPloneSiteRoot)
    grok.require('zope2.View')

    def render(self):
        oguid = self.request.get('oguid')
        clientid, iid = oguid.split(':')

        assert clientid == get_client_id(), (
            'Connected to wrong client! %s instead of %s' % (
                clientid, get_client_id()))

        obj = self._get_object(int(iid))

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
            raise NotFound
