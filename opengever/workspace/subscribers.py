from opengever.base.role_assignments import RoleAssignmentManager
from opengever.base.role_assignments import SharingRoleAssignment
from opengever.workspace.activities import ToDoAssignedActivity
from opengever.workspace.activities import ToDoClosedActivity
from opengever.workspace.activities import ToDoCommentedActivity
from opengever.workspace.activities import ToDoReopenedActivity
from opengever.workspace.activities import WorkspaceWatcherManager
from plone import api
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from zExceptions import Forbidden
from zope.container.interfaces import IContainerModifiedEvent
from zope.globalrequest import getRequest


def assign_owner_role_on_creation(workspace, event):
    """The creator of the workspace should have the WorkspaceOwner role,
    so that the she / he can access the workspace.
    """
    owner_userid = workspace.Creator()
    assignment = SharingRoleAssignment(owner_userid, ['WorkspaceOwner'])
    RoleAssignmentManager(workspace).add_or_update_assignment(assignment)


def check_delete_preconditions(todolist, event):
    """Its only possible to remove todolist if they are empty.
    """

    # Ignore plone site deletions
    if IPloneSiteRoot.providedBy(event.object):
        return

    if len(todolist.objectValues()):
        raise ValueError(
            'The todolist is not empty, therefore deletion is not allowed.')


class ForbiddenByToDoLimit(Forbidden):
    """Hard limit for the number of ToDos allowed in a
    workspace has been reached."""


TODO_NUMBER_LIMIT = 500


def check_todo_add_preconditions(todo, event):
    """We set a hard limit on the number of todos in a workspace
    """
    catalog = api.portal.get_tool("portal_catalog")
    todos = catalog.unrestrictedSearchResults(
                path=event.newParent.absolute_url_path(),
                portal_type=todo.portal_type)
    if len(todos) >= TODO_NUMBER_LIMIT:
        raise ForbiddenByToDoLimit()


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


def todo_modified(todo, event):
    if IContainerModifiedEvent.providedBy(event):
        return

    if is_attribute_changed(event, "responsible", "IToDoSchema"):
        workspace = todo.get_containing_workspace()
        WorkspaceWatcherManager(workspace).todo_responsible_modified(todo)
        ToDoAssignedActivity(todo, getRequest()).record()

    if is_attribute_changed(event, "completed", "IToDoSchema"):
        if todo.completed:
            ToDoClosedActivity(todo, getRequest()).record()
        else:
            ToDoReopenedActivity(todo, getRequest()).record()


def response_added(todo, event):
    ToDoCommentedActivity(todo,
                          getRequest(),
                          event.response_container,
                          event.response).record()
