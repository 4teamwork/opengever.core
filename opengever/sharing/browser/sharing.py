from AccessControl.SecurityManagement import getSecurityManager
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import setSecurityManager
from Acquisition import aq_base
from ftw.lawgiver.utils import get_specification_for
from opengever.base.handlebars import get_handlebars_template
from opengever.base.role_assignments import RoleAssignmentManager
from opengever.base.role_assignments import SharingRoleAssignment
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.ogds.base.utils import ogds_service
from opengever.sharing import _
from opengever.sharing.behaviors import IDossier, IStandard
from opengever.sharing.events import LocalRolesAcquisitionActivated
from opengever.sharing.events import LocalRolesAcquisitionBlocked
from opengever.sharing.events import LocalRolesModified
from opengever.sharing.interfaces import ISharingConfiguration
from pkg_resources import resource_filename
from plone import api
from plone.app.workflow.browser.sharing import SharingView
from plone.app.workflow.interfaces import ISharingPageRole
from plone.memoize.instance import clearafter
from plone.memoize.instance import memoize
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as PMF
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from urllib import urlencode
from zope.component import getUtilitiesFor
from zope.component import getUtility
from zope.event import notify
from zope.i18n import translate
import json
import re


ROLE_MAPPING = (
    (IDossier, (
        (u'Reader', _('sharing_dossier_reader')),
        (u'Contributor', _('sharing_dossier_contributor')),
        (u'Editor', _('sharing_dossier_editor')),
        (u'Reviewer', _('sharing_dossier_reviewer')),
        (u'Publisher', _('sharing_dossier_publisher')),
        (u'DossierManager', _('sharing_dossier_manager')),
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
    depending on the sharing behavior which is context
    """

    template = ViewPageTemplateFile('templates/sharing.pt')

    @property
    def vuejs_template(self):
        return get_handlebars_template(
            resource_filename('opengever.sharing.browser',
                              'templates/sharing.html'))

    def __call__(self):
        return self.template()

    def get_userid(self):
        return api.user.get_current().getId()

    def translate(self, msg):
        return translate(msg, context=self.request)

    def plone_translate(self, msgid):
        return self.translate(PMF(msgid))

    def translations(self):
        return json.dumps({
            'label_search': self.plone_translate('label_search'),
            'label_inherit_local_roles': self.plone_translate('label_inherit_local_roles'),
            'help_inherit_local_roles': self.plone_translate('help_inherit_local_roles'),
            'image_link_icon': self.plone_translate('image_link_icon'),
            'image_confirm_icon': self.plone_translate('image_confirm_icon'),
            'principal_search_placeholder': self.translate(
                _(u'principal_search_placeholder',
                  default=u'Search for Users and Groups')),
            'label_name': self.plone_translate('label_name'),
            'label_acquired': _(u'label_acquired', default=u'Acuired')
        })

    def saved(self):
        """Redirects to absolute_url and adds statusmessage.
        """
        message = _(u'label_roles_successfully_changed',
                    default=u'Local roles successfully changed')
        api.portal.show_message(
            message=message, request=self.request, type='info')

        return self.request.RESPONSE.redirect(self.context.absolute_url())

    @memoize
    def roles(self):
        super_roles = super(OpengeverSharingView, self).roles()

        if get_specification_for(self.context) is not None:
            # In lawgiver workflow specifications we can configure the
            # "visible roles", therefore we dont need to overwrite the
            # behavior here.
            return super_roles

        result = []
        for key, value in ROLE_MAPPING:
            if key.providedBy(self.context) or key is IStandard:
                roles = [r.get('id') for r in super_roles]
                for role_id, title in value:
                    if role_id in roles:
                        result.append(
                            {'id': role_id,
                             'title': title, })

                return result

        return super_roles

    def role_settings(self):
        """The standard role_settings method,
        but pop the AuthenticatedUsers group for not managers.
        """
        results = super(OpengeverSharingView, self).role_settings()
        member = self.context.portal_membership.getAuthenticatedMember()

        if member and 'Manager' not in member.getRolesInContext(self.context):
            # remove the group AuthenticatedUsers
            results.pop([r.get('id') for r in results].index('AuthenticatedUsers'))

        # Use group title attribute if exists, because our LDAP stack does
        # not support mapping additional attributes, we fetch the information
        # from ogds.
        for result in results:
            result['url'] = self.get_detail_view_url(result)
            if not result.get('type') == 'group':
                continue
            group = ogds_service().fetch_group(result['id'])
            if not group:
                continue
            result['title'] = group.label()

        return results

    def get_detail_view_url(self, item):
        """Returns the url to the detail view for users or group.
        """
        if item.get('type') == 'group':
            return '{}/@@list_groupmembers?group={}'.format(
                api.portal.get().absolute_url(), item['id'])
        else:
            return '{}/@@user-details/{}'.format(
                api.portal.get().absolute_url(), item['id'])

    def update_inherit(self, status=True, reindex=True):
        """Method Wrapper for the super method, to allow notify a
        corresponding event. Needed for adding a Journalentry after a
        change of the inheritance
        """
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
            if local_roles:
                context.manage_setLocalRoles(user.getId(), local_roles)

        context.__ac_local_roles_block__ = True if block else None

        # Restore the old security manager
        setSecurityManager(old_sm)

        if reindex:
            context.reindexObjectSecurity()

        if not block:
            notify(LocalRolesAcquisitionActivated(self.context))
        else:
            notify(LocalRolesAcquisitionBlocked(self.context))

        return True

    @clearafter
    def _update_role_settings(self, new_settings, reindex=True):
        """Replaced becasue we need our own permission manager stuff.
        """
        changed = False
        assignments = []

        for s in new_settings:
            principal = s['id']
            selected_roles = frozenset(s['roles'])
            if not selected_roles:
                continue

            assignments.append(SharingRoleAssignment(principal, selected_roles))

        if assignments:
            manager = RoleAssignmentManager(self.context)
            manager.set(assignments)

        return changed

    def update_role_settings(self, new_settings, reindex=True):
        """Method Wrapper for the super method, to allow notify a
        LocalRolesModified event. Needed for adding a Journalentry after a
        role_settings change
        """
        old_local_roles = dict(self.context.get_local_roles())
        changed = self._update_role_settings(new_settings, reindex)

        if changed:
            notify(LocalRolesModified(
                self.context,
                old_local_roles,
                self.context.get_local_roles(),
                ))

        return changed

    def _principal_search_results(self,
                                  search_for_principal,
                                  get_principal_by_id,
                                  get_principal_title,
                                  principal_type,
                                  id_key):
        """A mapper for the original method, to constraint the users
        list to only the users which are assigned to the current client
        """

        all_principals = super(OpengeverSharingView, self)._principal_search_results(
            search_for_principal,
            get_principal_by_id,
            get_principal_title,
            principal_type,
            id_key)

        if not all_principals:
            return all_principals

        admin_unit = get_current_admin_unit()
        assigned_users = set(user.userid for user in admin_unit.assigned_users())

        registry = getUtility(IRegistry)
        sharing_config = registry.forInterface(ISharingConfiguration)

        results = []
        for principal in all_principals:
            # users
            if principal.get('type') == 'user':
                if principal.get('id') in assigned_users:
                    results.append(principal)

            # groups
            elif re.search(sharing_config.black_list_prefix, principal.get('id')):
                if re.search(sharing_config.white_list_prefix, principal.get('id')):
                    results.append(principal)
            else:
                results.append(principal)
        return results

    def groupmembers_url(self, groupid):
        portal = api.portal.get()
        qs = urlencode({'group': groupid})
        return '/'.join((portal.portal_url(), '@@list_groupmembers?%s' % qs))


class SharingTab(OpengeverSharingView):
    """The sharing tab view, which show the standard sharin view,
    but wihtout the form.
    """

    index = ViewPageTemplateFile('sharing_tab.pt')

    @memoize
    def roles(self):
        return super(SharingTab, self).roles(check_permission=False)

    def get_css_classes(self):
        return ['searchform-hidden']
