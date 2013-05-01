from Products.CMFCore.utils import getToolByName
from five import grok
from plone.app.layout.viewlets.interfaces import IPortalHeader
from zope.interface import Interface


class ExposatorViewlet(grok.Viewlet):
    """ Viewlet which check the current clientm, if it's a remote client
    the navi and header area is blanked out.
    """

    grok.name('exposator')
    grok.context(Interface)
    grok.viewletmanager(IPortalHeader)
    grok.require('zope2.View')

    REMOTE_CLIENT_JS = '''
<script type="text/javascript">
$(function() {
    $('#portal-column-content').expose({closeOnClick: false, closeOnEsc: false});
    $('#portal-breadcrumbs').append('<span style="float:right"><a href="javascript:window.close()">Fenster schliessen</a></span')
});
</script>
'''

    def render(self):
        html = []
        member = getToolByName(
            self.context, 'portal_membership').getAuthenticatedMember()

        # Never display the exposator overlay for anonymous users
        if member.getUserName() == 'Anonymous User':
            return ''

        # check if the users isn't a Member or a Manger
        # then display the expose
        if not member.has_role('Member') and not member.has_role('Manager'):
            html.append(ExposatorViewlet.REMOTE_CLIENT_JS)
        return ''.join(html)
