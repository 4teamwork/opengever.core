from ftw.monitor.interfaces import IWarmupPerformer
from ftw.monitor.warmup import DefaultWarmupPerformer
from opengever.base.interfaces import IOpengeverBaseLayer
from Products.CMFPlone.interfaces import IPloneSiteRoot
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.interface import noLongerProvides
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
import plone.api


@implementer(IWarmupPerformer)
@adapter(IPloneSiteRoot, IBrowserRequest)
class GEVERWarmupPerformer(DefaultWarmupPerformer):
    """Call some REST API endpoints to warmup the instance.
    """

    VIEW_NAMES = [
        u'GET_application_json_',
        u'GET_application_json_@config',
        u'GET_application_json_@navigation',
    ]

    def perform(self):
        # Skins and browser layers are not correctly setup during warmup.
        # Fix 'em before calling our endpoints
        self.context.setupCurrentSkin()
        alsoProvides(self.request, IOpengeverBaseLayer)
        noLongerProvides(self.request, IDefaultBrowserLayer)
        alsoProvides(self.request, IDefaultBrowserLayer)

        with plone.api.env.adopt_user(username=self.context.getOwner().getId()):
            for view_name in self.VIEW_NAMES:
                view = getMultiAdapter((self.context, self.request), name=view_name)
                view()
