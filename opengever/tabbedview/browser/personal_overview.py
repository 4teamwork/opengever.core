from Products.CMFPlone.utils import getToolByName
from five import grok
from ftw.tabbedview.browser.tabbed import TabbedView
from ftw.table import helper
from opengever.globalindex.interfaces import ITaskQuery
from opengever.ogds.base.interfaces import IContactInformation
from opengever.ogds.base.utils import get_client_id
from opengever.tabbedview.browser.tabs import Documents, Dossiers, Tasks
from opengever.tabbedview.browser.tasklisting import GlobalTaskListingTab
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.component import getUtility
from zope.interface import Interface
import AccessControl


def authenticated_member(context):
    return context.portal_membership.getAuthenticatedMember().getId()


def remove_control_columns(columns):
    """Removes the control columns from list of columns and returns it back.
    """

    def _filterer(item):
        try:
            transform = item[1]
        except KeyError:
            return True
        else:
            if transform in (helper.draggable, helper.path_checkbox):
                return False
            else:
                return True

    return filter(_filterer, columns)


def remove_subdossier_column(columns):
    """Removes the subdossier column from list of columns and returns it back.
    """

    def _filterer(item):

        if isinstance(item, dict) and item['column'] == 'containing_subdossier':
            return False
        else:
            return True

    return filter(_filterer, columns)




class PersonalOverview(TabbedView):
    """The personal overview view show all documents and dossier
    where the actual user is the responsible.
    """

    default_tabs = [
        {'id': 'mydossiers', 'icon': None, 'url': '#', 'class': None},
        {'id': 'mydocuments', 'icon': None, 'url': '#', 'class': None},
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
        user = AccessControl.getSecurityManager().getUser()
        if user == AccessControl.SecurityManagement.SpecialUsers.nobody:
            login = self.context.portal_url() + '/login'
            return self.request.RESPONSE.redirect(login)

        if not self.user_is_allowed_to_view():
            catalog = getToolByName(self.context, 'portal_catalog')
            repos = catalog(portal_type='opengever.repository.repositoryroot')
            repo_url = repos[0].getURL()
            return self.request.RESPONSE.redirect(repo_url)

        else:
            return super(PersonalOverview, self).__call__()

    def get_tabs(self):

        info = getUtility(IContactInformation)
        is_admin = info.is_user_in_inbox_group()

        if is_admin:
            return self.default_tabs + self.admin_tabs
        else:
            return self.default_tabs

    def user_is_allowed_to_view(self):
        """Returns True if the current client is one of the user's home
        clients and he therefore is allowed to view the PersonalOverview,
        False otherwise.
        """

        info = getUtility(IContactInformation)
        return info.is_client_assigned()


class MyDossiers(Dossiers):
    grok.name('tabbedview_view-mydossiers')
    grok.require('zope2.View')
    grok.context(Interface)

    search_options = {'responsible': authenticated_member,
                      'is_subdossier':False}

    enabled_actions = [
        'pdf_dossierlisting',
        'export_dossiers',
        'reset_tableconfiguration',
        ]

    major_actions = ['pdf_dossierlisting']

    @property
    def view_name(self):
        return self.__name__.split('tabbedview_view-')[1]



class MyDocuments(Documents):
    grok.name('tabbedview_view-mydocuments')
    grok.require('zope2.View')
    grok.context(Interface)

    search_options = {'Creator': authenticated_member,
                      'trashed': False}

    enabled_actions = ['reset_tableconfiguration',]
    major_actions = []
    columns = remove_control_columns(Documents.columns)
    columns = remove_subdossier_column(columns)
    selection = ViewPageTemplateFile("no_selection_amount.pt")

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
    """A listing view,
    wich show all task where the actual user is the responsible.

    This listing is based on opengever.globalindex (sqlalchemy) and respects
    the basic features of tabbedview such as searching and batching.
    """

    grok.name('tabbedview_view-mytasks')
    grok.require('zope2.View')
    grok.context(Interface)

    enabled_actions = major_actions = [
        'pdf_taskslisting',
        'export_tasks',
        'reset_tableconfiguration',
        ]

    major_actions = [
        'pdf_taskslisting',
        ]

    def get_base_query(self):
        """Returns the base search query (sqlalchemy)i
        """

        portal_state = self.context.unrestrictedTraverse(
            '@@plone_portal_state')
        userid = portal_state.member().getId()

        query_util = getUtility(ITaskQuery)

        # show all tasks assigned to this user ..
        query = query_util._get_tasks_for_responsible_query(userid,
                                                            self.sort_on,
                                                            self.sort_order)

        # .. and assigned to the current client
        query = query.filter_by(assigned_client=get_client_id())
        return query

class IssuedTasks(Tasks):
    """List all tasks where I'm the issuer and which are physically stored on
    the current client.
    """

    grok.name('tabbedview_view-myissuedtasks')
    grok.require('zope2.View')
    grok.context(Interface)

    enabled_actions = [
        'pdf_taskslisting',
        'export_tasks',
        'reset_tableconfiguration',
        ]

    major_actions = ['pdf_taskslisting']

    search_options = {'issuer': authenticated_member,}

    columns = remove_subdossier_column(Tasks.columns)


class AllTasks(MyTasks):
    """Lists all tasks assigned to this clients.
    Bases on MyTasks
    """

    grok.name('tabbedview_view-alltasks')
    grok.require('zope2.View')
    grok.context(Interface)

    enabled_actions = [
        'pdf_taskslisting',
        'export_tasks',
        'reset_tableconfiguration',
        ]

    major_actions = ['pdf_taskslisting']

    def get_base_query(self):
        """Returns the base search query (sqlalchemy)
        """

        query_util = getUtility(ITaskQuery)
        return query_util._get_tasks_for_assigned_client_query(
            get_client_id(), self.sort_on, self.sort_order)


class AllIssuedTasks(Tasks):
    """List all tasks which are stored physically on this client.
    """

    grok.name('tabbedview_view-allissuedtasks')
    grok.require('zope2.View')
    grok.context(Interface)

    enabled_actions = [
        'pdf_taskslisting',
        'export_tasks',
        'reset_tableconfiguration',
        ]

    major_actions = ['pdf_taskslisting']

    columns = remove_subdossier_column(Tasks.columns)
