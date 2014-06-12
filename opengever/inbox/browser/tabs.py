from five import grok
from opengever.globalindex.interfaces import ITaskQuery
from opengever.inbox.inbox import IInbox
from opengever.inbox.yearfolder import IYearFolder
from opengever.ogds.base.utils import get_client_id
from opengever.ogds.base.utils import get_current_org_unit
from opengever.tabbedview.browser.tabs import Documents
from opengever.tabbedview.browser.tabs import Tasks
from opengever.tabbedview.browser.tabs import Trash
from opengever.tabbedview.browser.tasklisting import GlobalTaskListingTab
from opengever.tabbedview.helper import external_edit_link
from zope.component import getUtility


def get_current_inbox_principal(context):

    return 'inbox:%s' % get_client_id()


class AssignedInboxTasks(GlobalTaskListingTab):
    """Listing of tasks (including forwardings) which the
    responsible is the current inbox."""

    grok.name('tabbedview_view-assigned_inbox_tasks')
    grok.require('zope2.View')
    grok.context(IInbox)

    def get_base_query(self):
        """Returns the base search query (sqlalchemy),
        wich only select tasks assigned to the current inbox.
        """

        query_util = getUtility(ITaskQuery)
        query = query_util._get_tasks_for_responsible_query(
            get_current_inbox_principal(self.context),
            self.sort_on,
            self.sort_order)

        return query


class IssuedInboxTasks(Tasks):
    """Listing of local tasks (including forwardings) which the
    issuer is the current inbox."""

    grok.name('tabbedview_view-issued_inbox_tasks')
    grok.require('zope2.View')
    grok.context(IInbox)

    search_options = {'issuer': get_current_inbox_principal}

    types = ['opengever.task.task', 'opengever.inbox.forwarding']

    @property
    def columns(self):
        """Drop the containing_subdossier column from the column list
        """
        remove_columns = ['containing_subdossier', ]
        columns = []

        for col in super(IssuedInboxTasks, self).columns:
            if col.get('column') not in remove_columns:
                columns.append(col)

        return columns

    def update_config(self):
        """Remove the default path filter to the current context.
        It should search tasks over the complete client."""

        super(IssuedInboxTasks, self).update_config()
        self.filter_path = None


class ClosedForwardings(Tasks):

    grok.name('tabbedview_view-closed-forwardings')
    grok.context(IYearFolder)
    grok.require('zope2.View')

    types = ['opengever.inbox.forwarding', ]
    enabled_actions = []
    major_actions = []


def _get_current_org_unit_id(context):
    """Used as wrapper for the document search_option.
    Because `ftw.tabbedview.ListingView._search_options`
    pass the context to callable search_options.
    """
    return get_current_org_unit().id()


class InboxDocuments(Documents):
    """Lists documents directly inside the inbox, which are marked
    with the current org unit.
    """

    grok.context(IInbox)

    # do not list documents in forwardings
    depth = 1

    search_options = {'client_id': _get_current_org_unit_id}

    @property
    def columns(self):
        """Remove default columns `containing_subdossier`, `checked_out`
        and `external_edit`.
        """
        remove_columns = ['containing_subdossier', 'checked_out']
        columns = []

        for col in super(InboxDocuments, self).columns:
            if isinstance(col, dict) and \
                    col.get('column') in remove_columns:
                pass
            elif isinstance(col, tuple) and col[1] == external_edit_link:
                pass
            else:
                columns.append(col)

        return columns

    @property
    def enabled_actions(self):
        """Defines the enabled Actions"""
        actions = super(InboxDocuments, self).enabled_actions
        actions = [action for action in actions
                   if action not in (
                    'create_task',
                    'copy_documents_to_remote_client',
                    'move_items',)]

        actions += ['create_forwarding']
        return actions

    @property
    def major_actions(self):
        """Defines wich actions are major Actions"""
        actions = super(InboxDocuments, self).major_actions
        actions = [action for action in actions
                   if action not in ('create_task',)]
        actions += ['create_forwarding']
        return actions


class InboxTrash(Trash):
    """Special Trash view,
    some columns from the standard Trash view are disabled"""

    grok.context(IInbox)

    @property
    def columns(self):
        """Remove default columns `containing_subdossier`, `checked_out`
        and `external_edit`.
        """

        remove_columns = ['containing_subdossier', 'checked_out']
        columns = []
        for col in super(InboxTrash, self).columns:
            if isinstance(col, dict) and \
                    col.get('column') in remove_columns:
                pass
            elif isinstance(col, tuple) and \
                    col[1] == external_edit_link:
                pass
            else:
                columns.append(col)

        return columns
