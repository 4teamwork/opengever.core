from ftw.upgrade.interfaces import IDuringUpgrade
from opengever.base.placeful_workflow import assign_placeful_workflow
from opengever.base.response import COMMENT_RESPONSE_TYPE
from opengever.base.response import IResponseContainer
from opengever.base.response import OBJECT_CREATED_RESPONSE_TYPE
from opengever.base.response import Response
from opengever.base.role_assignments import RoleAssignmentManager
from opengever.base.role_assignments import SharingRoleAssignment
from opengever.workspace.activities import ToDoAssignedActivity
from opengever.workspace.activities import ToDoClosedActivity
from opengever.workspace.activities import ToDoCommentedActivity
from opengever.workspace.activities import ToDoReopenedActivity
from opengever.workspace.activities import WorkspaceWatcherManager
from opengever.workspace.indexers import INDEXED_IN_MEETING_SEARCHABLE_TEXT
from opengever.workspace.interfaces import IWorkspace
from opengever.workspace.todo import COMPLETE_TODO_TRANSITION
from opengever.workspace.workspace import IWorkspaceSchema
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from zope.container.interfaces import IContainerModifiedEvent
from zope.globalrequest import getRequest


def configure_workspace_root(root, event):
    assign_placeful_workflow(root, "opengever_workspace_policy")


def assign_admin_role_and_responsible_to_workspace_creator(workspace, event):
    """The creator of the workspace should have the Admin role,
    so that the she / he can access the workspace.
    """
    owner_userid = workspace.Creator()
    if owner_userid:
        # During bundle import, Creator() may return the empty string.
        # Make sure to not assign any local roles in that case.
        assignment = SharingRoleAssignment(owner_userid, ['WorkspaceAdmin'])
        RoleAssignmentManager(workspace).add_or_update_assignment(assignment)

        IWorkspaceSchema(workspace).responsible = owner_userid


def check_delete_preconditions(todolist, event):
    """Its only possible to remove todolist if they are empty.
    """

    # Ignore plone site deletions
    if IPloneSiteRoot.providedBy(event.object):
        return

    # Ignore workspace deletions
    if IWorkspace.providedBy(event.object):
        return

    if len(todolist.objectValues()):
        raise ValueError(
            'The todolist is not empty, therefore deletion is not allowed.')


def is_attribute_changed(event, attribute, schema):
    """When modified throught the form, the attribute name is found
    in the event attributes, whereas when done through the API,
    the qualified name is used instead.
    """
    qualified = ".".join([schema, attribute])
    attribute_names = set((qualified, attribute))
    for desc in event.descriptions:
        for attr in desc.attributes:
            if attr in attribute_names:
                return True
    return False


def todo_added(todo, event):
    workspace = todo.get_containing_workspace()
    WorkspaceWatcherManager(workspace).new_todo_added(todo)
    if todo.responsible is not None:
        ToDoAssignedActivity(todo, getRequest()).record()

    IResponseContainer(todo).add(Response(OBJECT_CREATED_RESPONSE_TYPE))


def todo_review_state_changed(todo, event):
    if not IDuringUpgrade.providedBy(getRequest()):
        # Don't create activities during upgrades.
        #
        # This avoids issues, specifically with
        # upgrade 20211105114219_add_completed_state_for_todos, where otherwise
        # we would issue SQL statements that may fail if certain SQL schema
        # migrations haven't been run yet. See CA-3574 for details.
        if event.action == COMPLETE_TODO_TRANSITION:
            ToDoClosedActivity(todo, getRequest()).record()
        else:
            ToDoReopenedActivity(todo, getRequest()).record()

    todo.reindexObject(idxs=['is_completed'])


def todo_modified(todo, event):
    if IContainerModifiedEvent.providedBy(event):
        return

    if is_attribute_changed(event, "responsible", "IToDoSchema"):
        workspace = todo.get_containing_workspace()
        WorkspaceWatcherManager(workspace).todo_responsible_modified(todo)
        ToDoAssignedActivity(todo, getRequest()).record()


def response_added(todo, event):
    if event.response.response_type == COMMENT_RESPONSE_TYPE:
        ToDoCommentedActivity(todo,
                              getRequest(),
                              event.response_container,
                              event.response).record()


def index_containing_meeting_searchable_text(agendaitem):
    # SearchableText is not in the catalog, so to avoid reindexing the
    # full object, we also reindex the UID.
    agendaitem.get_containing_meeting().reindexObject(idxs=['UID', 'SearchableText'])


def workspace_meeting_agendaitem_added(agendaitem, event):
    index_containing_meeting_searchable_text(agendaitem)


def workspace_meeting_agendaitem_modified(agendaitem, event):
    if IContainerModifiedEvent.providedBy(event):
        return

    index_meeting = False
    for field in INDEXED_IN_MEETING_SEARCHABLE_TEXT:
        if is_attribute_changed(event, field, "IWorkspaceMeetingAgendaItemSchema"):
            index_meeting = True
            break
    if index_meeting:
        index_containing_meeting_searchable_text(agendaitem)
