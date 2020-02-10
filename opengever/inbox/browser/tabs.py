from opengever.globalindex.model.task import Task
from opengever.ogds.base.utils import get_current_org_unit
from opengever.tabbedview.browser.tabs import Documents
from opengever.tabbedview.browser.tabs import Tasks
from opengever.tabbedview.browser.tabs import Trash
from opengever.tabbedview.browser.tasklisting import GlobalTaskListingTab
from opengever.tabbedview.helper import external_edit_link
from opengever.tabbedview.browser.bumblebee_gallery import BumblebeeGalleryMixin


def _get_current_org_unit_id(context):
    """Used as wrapper for the document search_option.
    Because `ftw.tabbedview.ListingView._search_options`
    pass the context to callable search_options.
    """
    return get_current_org_unit().id()


def get_current_inbox_principal(context):
    return get_current_org_unit().inbox().id()


class AssignedInboxTasks(GlobalTaskListingTab):
    """Listing of tasks (including forwardings) which the
    responsible is the inbox of the current selected org unit."""

    enabled_actions = [
        'pdf_taskslisting',
        'export_tasks',
        ]

    major_actions = [
        'pdf_taskslisting',
        ]

    def get_base_query(self):
        """Returns the base search query (sqlalchemy),
        wich only select tasks assigned to the current inbox.
        """
        current_inbox = get_current_org_unit().inbox().id()
        return Task.query.users_tasks(current_inbox)


class IssuedInboxTasks(GlobalTaskListingTab):
    """Listing of tasks (including forwardings) which the
    the inbox of the current selected org unit is the issuer."""

    enabled_actions = [
        'pdf_taskslisting',
        'export_tasks',
        ]

    major_actions = [
        'pdf_taskslisting',
        ]

    def get_base_query(self):
        """Returns the base search query (sqlalchemy),
        wich only select tasks assigned to the current inbox.
        """
        current_inbox = get_current_org_unit().inbox().id()
        return Task.query.users_issued_tasks(current_inbox)


class ClosedForwardings(Tasks):

    types = ['opengever.inbox.forwarding', ]
    enabled_actions = []
    major_actions = []
    filterlist_available = False


class InboxDocuments(Documents):
    """Lists documents directly inside the inbox, which are marked
    with the current org unit.
    """

    # do not list documents in forwardings
    depth = 1

    disabled_actions = ['create_proposal',
                        'submit_additional_documents']

    @property
    def columns(self):
        """Remove default columns `containing_subdossier`, `checked_out`
        and `external_edit`.
        """
        remove_columns = ['containing_subdossier', 'checked_out', 'reference']
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
                   if action not in self.disabled_actions]

        actions += ['create_forwarding']
        return actions

    @property
    def major_actions(self):
        """Defines wich actions are major Actions"""
        actions = super(InboxDocuments, self).major_actions
        actions += ['create_forwarding']
        return actions


class InboxDocumentsGallery(BumblebeeGalleryMixin, InboxDocuments):
    """Bumblebee gallery for inbox documents
    """
    depth = 1


class InboxTrash(Trash):
    """Inboxs trash view: shows only trashed document which are marked
    with the current org unit.

    Columns: the default columns `containing_subdossier` and `checked_out`
    are removed."""

    search_options = {'trashed': True}

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
