from AccessControl.SecurityManagement import getSecurityManager
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import setSecurityManager
from Acquisition import aq_base
from collections import OrderedDict
from ftw.lawgiver.utils import get_specification_for
from itertools import chain
from opengever.base import _ as base_mf
from opengever.base import utils
from opengever.base.handlebars import get_handlebars_template
from opengever.base.role_assignments import ASSIGNMENT_VIA_SHARING
from opengever.base.role_assignments import RoleAssignmentManager
from opengever.base.role_assignments import SharingRoleAssignment
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.inbox.inbox import IInbox
from opengever.ogds.base.interfaces import IOGDSSyncConfiguration
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.ogds.base.utils import groupmembers_url
from opengever.ogds.models.service import ogds_service
from opengever.sharing import _
from opengever.sharing.behaviors import IDossier
from opengever.sharing.events import LocalRolesAcquisitionActivated
from opengever.sharing.events import LocalRolesAcquisitionBlocked
from opengever.sharing.events import LocalRolesModified
from opengever.sharing.interfaces import IDisabledPermissionCheck
from opengever.sharing.interfaces import ISharingConfiguration
from opengever.workspace.utils import get_context_user_members_ids
from pkg_resources import resource_filename
from plone import api
from plone.app.workflow.browser.sharing import merge_search_results
from plone.app.workflow.browser.sharing import SharingView
from plone.app.workflow.interfaces import ISharingPageRole
from plone.memoize.instance import clearafter
from plone.memoize.instance import memoize
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as PMF
from Products.CMFPlone.utils import normalizeString
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from urllib import urlencode
from zope.component import getUtilitiesFor
from zope.component import getUtility
from zope.event import notify
from zope.i18n import translate
import json
import re


ROLES_ORDER = ['Reader', 'Contributor', 'Editor', 'Reviewer',
               'Publisher', 'DossierManager',
               'MeetingUser', 'CommitteeAdministrator',
               'CommitteeResponsible', 'CommitteeMember', 'TaskResponsible',
               'Role Manager', 'WorkspaceAdmin', 'WorkspacesCreator',
               'WorkspaceMember', 'WorkspaceGuest', 'WorkspacesUser']


GEVER_ROLE_MAPPING = OrderedDict([
    (u'Reader', _('sharing_dossier_reader')),
    (u'Contributor', _('sharing_dossier_contributor')),
    (u'Editor', _('sharing_dossier_editor')),
    (u'Reviewer', _('sharing_dossier_reviewer')),
    (u'Publisher', _('sharing_dossier_publisher')),
    (u'DossierManager', _('sharing_dossier_manager')),
    (u'TaskResponsible', _('sharing_task_responsible')),
    (u'Role Manager', _('sharing_role_manager')),
])

WORKSPACE_ROLE_MAPPING = OrderedDict([
    (u'WorkspaceAdmin', _('sharing_workspace_admin')),
    (u'WorkspaceMember', _('sharing_workspace_member')),
    (u'WorkspaceGuest', _('sharing_workspace_guest'))
])


class OpengeverSharingView(SharingView):

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
            'help_inherit_local_roles': self.translate(
                _(u'help_inherit_local_roles',
                  default=u'By default, permissions from the container of this '
                  u'item are inherited. If you disable this, only the '
                  u'explicitly defined sharing permissions will be valid.')),
            'not_all_search_results_visible': self.translate(
                _(u'not_all_search_results_visible',
                  default=u'Only the 25 first search results are visible.')),
            'image_link_icon': self.plone_translate('image_link_icon'),
            'image_confirm_icon': self.plone_translate('image_confirm_icon'),
            'principal_search_placeholder': self.translate(
                _(u'principal_search_placeholder',
                  default=u'Search for Users and Groups')),
            'label_name': self.plone_translate('label_name'),
            'label_acquired': self.translate(
                _(u'label_acquired_permission', default=u'Acquired permission')),
            'label_local': self.translate(
                _(u'label_local_permission', default=u'Local permission')),
            'label_save': self.translate(PMF(u'Save')),
            'label_cancel': self.translate(PMF(u'Cancel')),
            'label_automatic_permission': self.translate(
                _(u'label_automatic_permission', default=u'Automatic permission')),
            'label_local_permission': self.translate(
                _(u'label_local_permission', default=u'Local permission')),
            'label_save_failed': self.translate(
                _(u'message_save_failed', default=u'Local roles save failed.')),
            'message_title_error': self.translate(
                base_mf('message_title_error', default=u"Error")),
        })

    def saved(self):
        """Redirects to absolute_url and adds statusmessage.
        """
        message = _(u'label_roles_successfully_changed',
                    default=u'Local roles successfully changed')
        api.portal.show_message(
            message=message, request=self.request, type='info')

        return self.request.RESPONSE.redirect(self.context.absolute_url())

    def _roles(self):
        """plone.app.workflow SharingView original roles method, but
        with conditionally permission check.
        """
        is_permission_check_disabled = IDisabledPermissionCheck.providedBy(
            self.request)

        context = self.context
        portal_membership = api.portal.get_tool('portal_membership')
        pairs = []

        for name, utility in getUtilitiesFor(ISharingPageRole):
            permission = utility.required_permission
            if not is_permission_check_disabled and permission is not None:
                if not portal_membership.checkPermission(permission, context):
                    continue

            # be friendly to utilities implemented without required_interface
            iface = getattr(utility, 'required_interface', None)
            if iface is not None and not iface.providedBy(context):
                continue

            pairs.append(dict(id=name, title=utility.title))

        pairs.sort(key=lambda x: normalizeString(
            translate(x["title"], context=self.request)))

        return pairs

    @memoize
    def roles(self):
        super_roles = self._roles()

        if get_specification_for(self.context) is not None:
            # In lawgiver workflow specifications we can configure the
            # "visible roles", therefore we dont need to overwrite the
            # behavior here.
            return super_roles

        if IDossier.providedBy(self.context):
            available_roles = [u'Reader', u'Contributor', u'Editor', u'Reviewer',
                               u'Publisher', u'DossierManager']
        else:
            available_roles = [u'Reader', u'Contributor', u'Editor']

        if IDossierMarker.providedBy(self.context) or IInbox.providedBy(self.context):
            available_roles.append(u'TaskResponsible')

        result = []
        for role in [r.get('id') for r in super_roles]:
            if role in available_roles:
                result.append({'id': role, 'title': GEVER_ROLE_MAPPING[role]})

        return result

    def role_settings(self):
        """The standard role_settings method, but:
        - sort existing settings first, then search results
        - pop the AuthenticatedUsers group for not managers.
        """
        existing_settings = self.existing_role_settings()
        user_results = self.user_search_results()
        group_results = self.group_search_results()

        # Customization: we sort existing_settings separately from the search results
        existing_settings.sort(key=lambda x: safe_unicode(x["type"]) + safe_unicode(x["title"]))
        search_results = user_results + group_results
        search_results.sort(key=lambda x: safe_unicode(x["type"]) + safe_unicode(x["title"]))
        results = existing_settings + search_results

        # We may be called when the user does a search instead of an update.
        # In that case we must not loose the changes the user made and
        # merge those into the role settings.
        requested = self.request.form.get('entries', None)
        if requested is not None:
            knownroles = [r['id'] for r in self.roles()]
            settings = {}
            for entry in requested:
                roles = [r for r in knownroles
                         if entry.get('role_%s' % r, False)]
                settings[(entry['id'], entry['type'])] = roles

            for entry in results:
                desired_roles = settings.get((entry['id'], entry['type']), None)

                if desired_roles is None:
                    continue
                for role in entry["roles"]:
                    if entry["roles"][role] in [True, False]:
                        entry["roles"][role] = role in desired_roles

        # Customization: starting here the rest is Gever customization.
        member = self.context.portal_membership.getAuthenticatedMember()

        auth_group_index = [r.get('id') for r in results].index('AuthenticatedUsers')
        if member and 'Manager' not in member.getRolesInContext(self.context):
            # Remove the group AuthenticatedUsers if its not a manager
            results.pop(auth_group_index)
        else:
            # Translate `Logged-In users` label, currently the plone.restapi
            # sharing endpoint does not translate this label
            results[auth_group_index]['title'] = translate(
                results[auth_group_index]['title'],
                domain='plone', context=self.request)

        manager = RoleAssignmentManager(self.context)
        for result in results:
            self.extend_with_detail_view_infos(result)
            result['computed_roles'] = result['roles']
            self.extend_with_assignment_infos(result, manager)
            self.update_computed_info(result)

            # Use group title attribute if exists, because our LDAP stack does
            # not support mapping additional attributes, we fetch the information
            # from ogds.
            if not result.get('type') == 'group':
                continue
            group = ogds_service().fetch_group(result['id'])
            if not group:
                continue
            result['title'] = group.label()

        return results

    def extend_with_detail_view_infos(self, item):
        """We do not use item['type'] to determine whether it is a group or a user,
        as this was determined from the acl_users which wrongly identifies
        inactive groups (groups that were deleted from the LDAP) as users.
        Instead we check using the ogds service.
        """
        url = None
        service = ogds_service()
        group = service.fetch_group(item['id'])
        user = service.fetch_user(item['id'])
        if group:
            url = '{}/@@list_groupmembers?{}'.format(
                api.portal.get().absolute_url(),
                urlencode({'group': item['id']}))
        elif user:
            url = '{}/@@user-details-plain/{}'.format(
                api.portal.get().absolute_url(), item['id'])

        item['url'] = url

    def extend_with_assignment_infos(self, item, manager):
        local_roles = {role['id']: False for role in self.roles()}
        automatic_roles = {role['id']: False for role in self.roles()}

        assignments = manager.get_assignments_by_principal_id(item['id'])
        for assignment in assignments:
            if isinstance(assignment, SharingRoleAssignment):
                for role in assignment.roles:
                    local_roles[role] = True
            else:
                for role in assignment.roles:
                    automatic_roles[role] = True

        item['roles'] = local_roles
        item['automatic_roles'] = automatic_roles

    def update_computed_info(self, item):
        """Set acquired for all acquired roles in the `computed_roles`,
        even if autoamtic local roles exists.
        """

        _inherited_roles = {
            name: roles
            for (name, roles, rtype, rid) in self._inherited_roles()}

        for role in _inherited_roles.get(item['id'], []):
            item['computed_roles'][role] = 'acquired'

    def update_inherit(self, status=True, reindex=True):
        """Method Wrapper for the super method, to allow notify a
        corresponding event. Needed for adding a Journalentry after a
        change of the inheritance
        """

        is_administrator = utils.is_administrator()

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

        if block and not is_administrator:
            # If user has inherited local roles and removes inheritance,
            # locally set roles he inherited before
            # to avoid definitive lose of access (refs #11945)

            # For administrators and managers we skip those fallback, because
            # the access for those users is ensured by the global roles. So we
            # can avoid local_roles assigned to a specific users, which we say
            # should not be used usually.

            context_roles = user.getRolesInContext(context)
            global_roles = user.getRoles()
            local_roles = [r for r in context_roles if r not in global_roles]
            if local_roles:
                assignment = SharingRoleAssignment(user.getId(), local_roles)
                RoleAssignmentManager(self.context).add_or_update_assignment(assignment)

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
        """Replaced because we need our own permission manager stuff.
        """
        assignments = []
        principals_to_clear = []

        for s in new_settings:
            principal = s['id']
            selected_roles = frozenset(s['roles'])
            if not selected_roles:
                principals_to_clear.append(principal)
                continue

            assignments.append(SharingRoleAssignment(principal, selected_roles))

        manager = RoleAssignmentManager(self.context)
        if assignments:
            manager.reset(assignments)
        else:
            manager.clear_by_cause_and_principals(
                ASSIGNMENT_VIA_SHARING, principals_to_clear)

    def update_role_settings(self, new_settings, reindex=True):
        """Method Wrapper for the super method, to allow notify a
        LocalRolesModified event. Needed for adding a Journalentry after a
        role_settings change
        """
        new_settings = self.convert_loginnames_to_userid(new_settings)

        old_local_roles = dict(self.context.get_local_roles())
        self._update_role_settings(new_settings, reindex)

        if old_local_roles != dict(self.context.get_local_roles()):
            notify(
                LocalRolesModified(self.context, old_local_roles,
                                   self.context.get_local_roles()))
            return True

        return False

    def convert_loginnames_to_userid(self, settings):
        for setting in settings:
            if setting.get('type') == 'group':
                group = ogds_service().fetch_group(
                    setting[u'id'], groupname_as_fallback=True)
                if group and group.groupid != setting[u'id']:
                    setting[u'id'] = group.groupid

            elif setting.get('type') == 'user':
                user = ogds_service().fetch_user(
                    setting[u'id'], username_as_fallback=True)
                if user and user.userid != setting[u'id']:
                    setting[u'id'] = user.userid

        return settings

    def group_search_results(self):
        """Customization of the original method to also search on the
        group description attribute (configured in the plone registry), which
        is also displayed in the form when available.
        """

        def search_for_principal(hunter, search_term):
            group_attribute = api.portal.get_registry_record(
                name='group_title_ldap_attribute',
                interface=IOGDSSyncConfiguration)

            fields = ['id', 'title']
            if group_attribute:
                # search fields need to be utf-8 otherwise it leads to empty
                # search results with silent encoding errors.
                fields.append(group_attribute.encode('utf-8'))

            return merge_search_results(
                chain(*[hunter.searchGroups(**{field: search_term}) for field in fields]), 'groupid')

        def get_principal_by_id(group_id):
            portal_groups = getToolByName(self.context, 'portal_groups')
            return portal_groups.getGroupById(group_id)

        def get_principal_title(group, _):
            return group.getGroupTitleOrName()

        return self._principal_search_results(
            search_for_principal, get_principal_by_id,
            get_principal_title, 'group', 'groupid')

    def _principal_search_results(self,
                                  search_for_principal,
                                  get_principal_by_id,
                                  get_principal_title,
                                  principal_type,
                                  id_key):
        """A mapper for the original method, to constrain the users
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
        return groupmembers_url(groupid)


class WorkspaceSharingView(OpengeverSharingView):

    def _principal_search_results(self,
                                  search_for_principal,
                                  get_principal_by_id,
                                  get_principal_title,
                                  principal_type,
                                  id_key):
        """A mapper for the original method, to constrain the users
        list to only users having permissions on the workspace,
        except for administrators which can set permissions for any users.
        """

        all_principals = SharingView._principal_search_results(
            self,
            search_for_principal,
            get_principal_by_id,
            get_principal_title,
            principal_type,
            id_key)

        if not all_principals:
            return all_principals

        # Administrators can give permissions to any user
        if utils.is_administrator():
            return all_principals

        workspace_users = set(get_context_user_members_ids(
            self.context, disregard_block=True))
        results = [principal for principal in all_principals
                   if principal["id"] in workspace_users]
        return results


class SharingTab(OpengeverSharingView):
    """The sharing tab view, which show the standard sharin view,
    but wihtout the form.
    """

    template = ViewPageTemplateFile('templates/sharing_tab.pt')
