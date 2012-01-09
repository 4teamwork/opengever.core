from AccessControl.SecurityManagement import getSecurityManager
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import setSecurityManager
from Acquisition import aq_base
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from opengever.ogds.base.interfaces import IContactInformation
from opengever.sharing import _
from opengever.sharing.behaviors import IDossier, IStandard
from opengever.sharing.events import LocalRolesAcquisitionActivated
from opengever.sharing.events import LocalRolesAcquisitionBlocked
from opengever.sharing.events import LocalRolesModified
from plone.app.workflow.browser.sharing import SharingView
from plone.app.workflow.interfaces import ISharingPageRole
from plone.memoize.instance import memoize
from zope.component import getUtilitiesFor
from zope.component import getUtility
from zope.event import notify


ROLE_MAPPING = (
    (IDossier, (
            (u'Reader', _('sharing_dossier_reader')),
            (u'Contributor', _('sharing_dossier_contributor')),
            (u'Editor', _('sharing_dossier_editor')),
            (u'Reviewer', _('sharing_dossier_reviewer')),
            (u'Publisher', _('sharing_dossier_publisher')),
            (u'Administrator', _('sharing_dossier_administrator')),
            )),

    (IStandard, (
            (u'Reader', _('sharing_reader')),
            (u'Contributor', _('sharing_contributor')),
            (u'Editor', _('sharing_editor')),
            (u'Role Manager', _('sharing_role_manager')),
            )),
    )


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
                pairs.append(dict(id=name, title=utility.title))

        pairs.sort(key=lambda x: x["id"])
        return pairs

    def available_roles(self):
        result = []
        for key, value in ROLE_MAPPING:
            if key.providedBy(self.context) or key is IStandard:
                roles = [r.get('id') for r in self.roles()]
                for id, title in value:
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

    def update_inherit(self, status=True, reindex=True):
        """Method Wrapper for the super method, to allow notify a
        corresponding event. Needed for adding a Journalentry after a
        change of the inheritance"""

        # Modifying local roles needs the "Sharing page: Delegate roles"
        # permission as well as "Modify portal content". However, we don't
        # want to give the "Role Manager" Role "Modify portal content",
        # so we circumvent the permission check here by temporarily assuming
        # the owner's roles. [lgraf]

        context = self.context
        portal_membership = getToolByName(context, 'portal_membership')

        block = not status
        oldblock = bool(getattr(aq_base(context),
                                '__ac_local_roles_block__', False))

        if block == oldblock:
            return False

        # store the real user
        user = portal_membership.getAuthenticatedMember()

        # assume the manger user security context
        old_sm = getSecurityManager()

        owner = getToolByName(
            context, 'portal_url').getPortalObject().getWrappedOwner()
        newSecurityManager(self.context, owner)

        if block:
            # If user has inherited local roles and removes inheritance,
            # locally set roles he inherited before
            # to avoid definitive lose of access (refs #11945)
            context_roles = user.getRolesInContext(context)
            global_roles = user.getRoles()
            local_roles = [r for r in context_roles if r not in global_roles]
            context.manage_setLocalRoles(user.getId(), local_roles)

        context.__ac_local_roles_block__ = block and True or None

        # Restore the old security manager
        setSecurityManager(old_sm)

        if reindex:
            context.reindexObjectSecurity()

        if not block:
            notify(LocalRolesAcquisitionActivated(self.context))
        else:
            notify(LocalRolesAcquisitionBlocked(self.context))

        return True

    def update_role_settings(self, new_settings, reindex):
        """"Method Wrapper for the super method, to allow notify a
        LocalRolesModified event. Needed for adding a Journalentry after a
        role_settings change"""

        old_local_roles = dict(self.context.get_local_roles())
        changed = super(OpengeverSharingView, self).update_role_settings(
            new_settings, reindex)

        if changed:
            notify(LocalRolesModified(
                    self.context,
                    old_local_roles,
                    self.context.get_local_roles()))

        return changed

    def _principal_search_results(self,
                                  search_for_principal,
                                  get_principal_by_id,
                                  get_principal_title,
                                  principal_type,
                                  id_key):
        """A mapper for the original method, to constraint the users
        list to only the users which are assigned to the current client"""

        all_principals = SharingView._principal_search_results(
            self,
            search_for_principal,
            get_principal_by_id,
            get_principal_title,
            principal_type,
            id_key)

        if len(all_principals) == 0:
            return all_principals

        info = getUtility(IContactInformation)
        assigned_users = [user.userid for user in info.list_assigned_users()]
        results = []

        for principal in all_principals:
            if principal.get(
                'id') in assigned_users or principal.get('type') != 'user':
                results.append(principal)

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
