from five import grok
from opengever.ogds.base.interfaces import IContactInformation
from plone.app.layout.viewlets.interfaces import IPortalHeader
from Products.CMFCore.utils import getToolByName

from zope.interface import Interface
from zope.component import getUtility


class ExposatorViewlet(grok.Viewlet):
    """ Viewlet which check the current clientm, if it's a remote client
    the navi and header area is blanked out.
    """

    grok.name('redirector')
    grok.context(Interface)
    grok.viewletmanager(IPortalHeader)
    grok.require('zope2.View')

    REMOTE_CLIENT_JS = '''
<script type="text/javascript">
jq(function() {
    jq('#portal-column-content').expose({closeOnClick: false, closeOnEsc: false});
    jq('#portal-breadcrumbs').append('<span style="float:right"><a href="javascript:window.close()">Fenster schliessen</a></span')
});
</script>
'''

    def render(self):
        html = []
        member = getToolByName(
            self.context, 'portal_membership').getAuthenticatedMember()
        userid = member.getId()

        # check if it's a home_client, when not show expose
        info = getUtility(IContactInformation)
        if userid != u'zopemaster' and \
                not info.is_client_assigned(userid=userid):
            html.append(ExposatorViewlet.REMOTE_CLIENT_JS)
        return ''.join(html)
