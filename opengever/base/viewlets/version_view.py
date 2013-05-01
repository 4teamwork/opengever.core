from five import grok
from plone.app.versioningbehavior.behaviors import IVersioningSupport
from zope.component import getMultiAdapter


class VersionView(grok.View):
    """Displays a particular version of an object using the default view of
    the respective content type.
    """
    grok.context(IVersioningSupport)
    grok.require('zope2.View')
    grok.name('version-view')

    def render(self, version_id):
        pr = self.context.portal_repository
        old_obj = pr.retrieve(self.context, version_id).object
        content_view = getMultiAdapter((old_obj, self.request), name='view')
        return content_view()
