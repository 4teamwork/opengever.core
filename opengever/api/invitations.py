from opengever.api.participations import ParticipationsGet
from opengever.workspace.participation.browser.manage_participants import ManageParticipants


class InvitationsGet(ParticipationsGet):
    """API Endpoint which returns a list of all invitations for the current
    workspace.

    GET workspace/@invitations HTTP/1.1
    """

    def _items(self):
        manager = ManageParticipants(self.context, self.request)
        return manager.get_pending_invitations()
