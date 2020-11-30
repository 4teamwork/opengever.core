from ftw.upgrade import UpgradeStep
from opengever.activity import notification_center
from opengever.activity.model import Subscription
from opengever.activity.roles import WORKSPACE_MEMBER_ROLE
from opengever.base.model import create_session
from opengever.workspace.participation.browser.manage_participants import ManageParticipants
from opengever.workspace.todo import ToDo
from zope.globalrequest import getRequest
import logging


logger = logging.getLogger('ftw.upgrade')


class CorrectToDoWatchers(UpgradeStep):
    """Correct to do watchers.
    """

    deferrable = True

    def __call__(self):
        self.center = notification_center()
        self.session = create_session()

        # Because WorkspaceWatcherManager.new_participant_added not only added
        # the new participant as watcher to all ToDos but also with the
        # participants'role in the workspace instead of WORKSPACE_MEMBER_ROLE ,
        # as role, we can identify the wrongly added subscriptions by their role.
        roles = ["WorkspaceGuest", "WorkspaceMember", "WorkspaceAdmin"]
        subscriptions = Subscription.query.filter(Subscription.role.in_(roles))

        todos = set()
        for subscription in subscriptions:
            resource = subscription.resource
            obj = resource.oguid.resolve_object()
            if not isinstance(obj, ToDo):
                logger.warning(
                    'Subscription {} is not on a ToDo. '
                    'Skipping.'.format(subscription))
                continue
            self.session.delete(subscription)
            todos.add(obj)

        # Now we make sure that all workspace participants are watchers from
        # the todos in the workspace.
        for todo in todos:
            self._add_all_workspace_users_as_watchers(todo)

    def _add_all_workspace_users_as_watchers(self, todo):
        """Copy from WorkspaceWatcherManager
        """
        workspace = todo.get_containing_workspace()
        manager = ManageParticipants(workspace, getRequest())

        for member in manager.get_participants():
            self.center.add_watcher_to_resource(
                todo, member["userid"], WORKSPACE_MEMBER_ROLE)
