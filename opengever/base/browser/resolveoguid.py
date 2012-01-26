from AccessControl.SecurityManagement import SpecialUsers
from Products.CMFCore.utils import getToolByName
from five import grok
from opengever.ogds.base.interfaces import IContactInformation
from opengever.ogds.base.utils import get_client_id
from zExceptions import NotFound
from zope.component import getUtility
from zope.intid.interfaces import IIntIds
from zope.interface import Interface


class ResolveOGUIDView(grok.View):

    grok.name('resolve_oguid')
    grok.context(Interface)
    grok.require('zope2.View')

    def render(self):
        oguid = self.request.get('oguid')
        clientid, iid = oguid.split(':')

        if clientid != get_client_id():
            # wrong client. redirect to right one.
            info = getUtility(IContactInformation)
            client = info.get_client_by_id(clientid)

            url = '%s/@@resolve_oguid?oguid=%s' % (client.public_url, oguid)
            return self.request.RESPONSE.redirect(url)

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
