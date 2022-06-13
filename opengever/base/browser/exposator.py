from plone.app.layout.viewlets.common import ViewletBase
from Products.CMFCore.utils import getToolByName


class ExposatorViewlet(ViewletBase):
    """ Viewlet which check the current clientm, if it's a remote client
    the navi and header area is blanked out.
    """

    REMOTE_CLIENT_JS = '''
<script type="text/javascript" id="exposator">
$(function() {
    $('#column-content, #portal-column-content').expose({closeOnClick: false, closeOnEsc: false, zIndex: 7000});
    $('#portal-breadcrumbs').css('z-index', '7001');
    $('#portal-breadcrumbs').append('<span style="float:right"><a href="javascript:window.close()">Fenster schliessen</a></span');
});
</script>
'''  # noqa

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
