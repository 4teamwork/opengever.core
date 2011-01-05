from opengever.sharing import _
from opengever.sharing.behaviors import IDossier, IStandard
from plone.app.workflow.browser.sharing import SharingView
from plone.app.workflow.interfaces import ISharingPageRole
from plone.memoize.instance import memoize
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getUtilitiesFor

ROLE_MAPPING = {
    IDossier: (
        (u'Reader', _('sharing_dossier_reader')),
        (u'Contributor', _('sharing_dossier_contributor')),
        (u'Editor', _('sharing_dossier_editor')),
        (u'Reviewer', _('sharing_dossier_reviewer')),
        (u'Publisher', _('sharing_dossier_publisher')),
        (u'Administrator', _('sharing_dossier_administrator')),
    ),

    IStandard: (
        (u'Reader', _('sharing_reader')),
        (u'Contributor', _('sharing_contributor')),
        (u'Editor', _('sharing_editor')),
    ),
}


class OpengeverSharingView(SharingView):
    """Special Opengever Sharing View, which display different roles
    depending on the sharing behavior which is context"""

    template = ViewPageTemplateFile('sharing.pt')

    @memoize
    def roles(self, check_permission=True):
        """Get a list of roles that can be managed.

        Returns a list of dicts with keys:

            - id
            - title
        """
        context = self.context
        portal_membership = getToolByName(context, 'portal_membership')

        pairs = []
        for name, utility in getUtilitiesFor(ISharingPageRole):
            permission = utility.required_permission
            if not check_permission or permission is None or \
                portal_membership.checkPermission(permission, context):
                pairs.append(dict(id = name, title = utility.title))

        pairs.sort(key=lambda x: x["id"])
        return pairs

    def available_roles(self):
        result = []
        for key, value in ROLE_MAPPING.items():
            if key.providedBy(self.context) or key is IStandard:
                for id, title in value:
                    roles = [r.get('id') for r in self.roles()]
                    if id in roles:
                        result.append(
                            {'id': id,
                             'title': title, })
                return result

        return self.roles()

    def role_settings(self):
        """ The standard role_settings method,
        but pop the AuthenticatedUsers group for not managers. """
        results = super(OpengeverSharingView, self).role_settings()

        member = self.context.portal_membership.getAuthenticatedMember()

        if member:
            if 'Manager' in member.getRolesInContext(self.context):
                return results

        # remove the group AuthenticatedUsers
        results.pop([r.get('id') for r in results].index('AuthenticatedUsers'))

        return results


class SharingTab(OpengeverSharingView):
    """The sharing tab view, which show the standard sharin view,
    but wihtout the form."""

    template = ViewPageTemplateFile('sharing_tab.pt')

    @memoize
    def roles(self):
        return super(SharingTab, self).roles(check_permission=False)

    def get_css_classes(self):
        return ['searchform-hidden']
