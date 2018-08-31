from AccessControl import getSecurityManager
from AccessControl import SecurityManagement
from AccessControl import Unauthorized
from ftw.tabbedview.browser.tabbed import TabbedView
from opengever.activity import is_activity_feature_enabled
from opengever.globalindex.model.task import Task
from opengever.latex.opentaskreport import is_open_task_report_allowed
from opengever.meeting import is_meeting_feature_enabled
from opengever.meeting.browser.documents.proposalstab import ProposalListingTab
from opengever.meeting.model.proposal import Proposal
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.ogds.base.utils import get_current_org_unit
from opengever.ogds.base.utils import ogds_service
from opengever.ogds.models.group import Group
from opengever.ogds.models.group import groups_users
from opengever.ogds.models.team import Team
from opengever.tabbedview import _
from opengever.tabbedview import LOG
from opengever.tabbedview.browser.tabs import Documents
from opengever.tabbedview.browser.tabs import DocumentsProxy
from opengever.tabbedview.browser.tabs import Dossiers
from opengever.tabbedview.browser.tasklisting import GlobalTaskListingTab
from plone import api
from plone.memoize.view import memoize_contextless
from Products.CMFPlone.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from sqlalchemy.exc import OperationalError


def authenticated_member(context):
    return context.portal_membership.getAuthenticatedMember().getId()


def remove_subdossier_column(columns):
    """Removes the subdossier column from list of columns and returns it back.
    """
    def _filterer(item):
        if isinstance(item, dict) and \
           item['column'] == 'containing_subdossier':
            return False
        return True

    return filter(_filterer, columns)


class PersonalOverview(TabbedView):
    """The personal overview view show all documents and dossier
    where the actual user is the responsible.
    """

    template = ViewPageTemplateFile("personal_overview.pt")

    default_tabs = [
        {'id': 'mydossiers', 'icon': None, 'url': '#', 'class': None},
        {'id': 'mydocuments-proxy', 'icon': None, 'url': '#', 'class': None},
        {'id': 'mytasks', 'icon': None, 'url': '#', 'class': None},
        {'id': 'myissuedtasks', 'icon': None, 'url': '#', 'class': None},
    ]

    admin_tabs = [
        {'id': 'alltasks', 'icon': None, 'url': '#', 'class': None},
        {'id': 'allissuedtasks', 'icon': None, 'url': '#', 'class': None},
        ]

    def __call__(self):
        """If user is not allowed to view PersonalOverview, redirect him
        to the repository root, otherwise behave like always.
        """
        user = getSecurityManager().getUser()
        if user == SecurityManagement.SpecialUsers.nobody:
            raise Unauthorized

        if not self.user_is_allowed_to_view():
            catalog = getToolByName(self.context, 'portal_catalog')
            repos = catalog(portal_type='opengever.repository.repositoryroot')
            repo_url = repos[0].getURL()
            return self.request.RESPONSE.redirect(repo_url)
        else:
            if is_open_task_report_allowed():
                # Somehow if only the pdf-open-task-report action is available
                # plone's `showEditableBorder` assumes that the edit-bar should
                # be hidden.
                # So we have to force the edit bar if the user can generate an
                # open task report.
                api.portal.get().REQUEST.set('enable_border', True)
            return self.template(self)

    def personal_overview_title(self):
        current_user = ogds_service().fetch_current_user()
        if current_user:
            user_name = current_user.label(with_principal=False)
        else:
            user_name = api.user.get_current().getUserName()

        return _('personal_overview_title',
                 default='Personal Overview: ${user_name}',
                 mapping=dict(user_name=user_name))

    def _is_user_admin(self):
        m_tool = getToolByName(self.context, 'portal_membership')
        member = m_tool.getAuthenticatedMember()
        if member:
            if member.has_role('Administrator') \
                    or member.has_role('Manager'):
                return True
        return False

    @property
    def notification_tabs(self):
        tabs = []
        if is_activity_feature_enabled():
            tabs.append(
                {'id': 'mynotifications',
                 'title': _('label_my_notifications',
                            default=u'My notifications'),
                 'icon': None, 'url': '#', 'class': None})

        return tabs

    @property
    def meeting_tabs(self):
        tabs = []
        if is_meeting_feature_enabled():
            tabs.append(
                {'id': 'myproposals',
                 'title': _('label_my_proposals', default=u'My proposals'),
                 'icon': None, 'url': '#', 'class': None})

        return tabs

    def get_tabs(self):
        tabs = self.default_tabs + self.meeting_tabs + self.notification_tabs
        if self.is_user_allowed_to_view_additional_tabs():
            tabs += self.admin_tabs

        return tabs

    def is_user_allowed_to_view_additional_tabs(self):
        """The additional tabs Alltasks and AllIssuedTasks are only shown
        to adminsitrators and users of the current inbox group.
        """
        inbox = get_current_org_unit().inbox()
        current_user = ogds_service().fetch_current_user()
        return current_user in inbox.assigned_users() or self._is_user_admin()

    @memoize_contextless
    def user_is_allowed_to_view(self):
        """Returns True if the current client is one of the user's home
        clients or an administrator and he therefore is allowed to view
        the PersonalOverview, False otherwise.
        """
        try:
            current_user = ogds_service().fetch_current_user()
            if get_current_admin_unit().is_user_assigned(current_user):
                return True
            elif self._is_user_admin():
                return True
        except OperationalError as e:
            LOG.exception(e)

        return False


class MyDossiers(Dossiers):
    """List the dossiers where the current user is the responsible."""

    search_options = {'responsible': authenticated_member,
                      'is_subdossier': False}

    enabled_actions = [
        'pdf_dossierlisting',
        'export_dossiers',
        ]

    major_actions = ['pdf_dossierlisting']

    @property
    def view_name(self):
        return self.__name__.split('tabbedview_view-')[1]


class MyDocumentsProxy(DocumentsProxy):
    """The proxy view for documents created by the current user."""

    listview = "tabbedview_view-mydocuments"
    galleryview = "tabbedview_view-mydocuments-gallery"


class MyDocuments(Documents):
    """List the documents created by the current user."""

    search_options = {'Creator': authenticated_member,
                      'trashed': False}

    enabled_actions = [
        'zip_selected',
        'export_documents',
    ]

    major_actions = []

    @property
    def columns(self):
        """Gets the columns wich wich will be displayed
        """
        remove_columns = ['containing_subdossier']
        columns = []

        for col in super(MyDocuments, self).columns:
            if isinstance(col, dict) and \
                    col.get('column') in remove_columns:
                pass  # remove this column
            else:
                columns.append(col)

        return columns

    @property
    def view_name(self):
        return self.__name__.split('tabbedview_view-')[1]


class MyTasks(GlobalTaskListingTab):
    """A listing view, which lists all tasks where the given
    user is responsible. It queries all admin units.

    This listing is based on opengever.globalindex (sqlalchemy) and respects
    the basic features of tabbedview such as searching and batching.
    """

    enabled_actions = [
        'pdf_taskslisting',
        'export_tasks',
        ]

    major_actions = [
        'pdf_taskslisting',
        ]

    def get_base_query(self):
        userid = api.user.get_current().getId()
        responsibles = [
            team.actor_id() for team in
            Team.query.join(Group).join(groups_users).filter_by(userid=userid)]
        responsibles.append(userid)

        return Task.query.by_responsibles(responsibles)


class IssuedTasks(GlobalTaskListingTab):
    """A ListingView list all tasks where the given user is the issuer.
    Queries all admin units.
    """

    enabled_actions = [
        'pdf_taskslisting',
        'export_tasks',
        ]

    major_actions = ['pdf_taskslisting']

    def get_base_query(self):
        portal_state = self.context.unrestrictedTraverse(
            '@@plone_portal_state')
        userid = portal_state.member().getId()

        return Task.query.users_issued_tasks(userid)


class MyProposals(ProposalListingTab):
    """List proposals issued by the current user."""

    def get_base_query(self):
        return Proposal.query.by_issuer(api.user.get_current().getId())


class AllTasks(GlobalTaskListingTab):
    """Lists all tasks assigned to this clients.
    Bases on MyTasks
    """

    enabled_actions = [
        'pdf_taskslisting',
        'export_tasks',
        ]

    major_actions = ['pdf_taskslisting']

    def get_base_query(self):
        return Task.query.by_assigned_org_unit(get_current_org_unit())


class AllIssuedTasks(GlobalTaskListingTab):
    """List all tasks which are stored physically on this client.
    """

    enabled_actions = [
        'pdf_taskslisting',
        'export_tasks',
        ]

    major_actions = ['pdf_taskslisting']

    def get_base_query(self):
        return Task.query.by_issuing_org_unit(get_current_org_unit())
