from zope.interface import Interface
from Products.Five import BrowserView


class IForwardingTransitionController(Interface):
    """Interface for a controller view for checking, if certain
    transitions of the forwarding worfklow are available for the
    current user in the current object state.
    """

    def is_accept_possible(self):
        """Checks, whether the transition forwarding-transition-accept
        is possible and allowed at the moment.
        """

    def is_assign_to_dossier_possible(self):
        """Checks, whether the transition
        forwarding-transition-assign-to-dossier is possible and allowed
        at the moment.
        """

    def is_close_possible(self):
        """Checks, whether the transition forwarding-transition-close
        is possible and allowed at the moment.
        """

    def is_refuse_possible(self):
        """Checks, whether the transition forwarding-transition-refuse
        is possible and allowed at the moment.
        """


class ForwardingTransitionController(BrowserView):
    """see IForwardingTransitionController
    """

    def is_accept_possible(self):
        """see IForwardingTransitionController
        """
        ogview = self.context.restrictedTraverse('@@opengever_view')
        responsible_client = self.context.responsible_client

        # accept only possible for users assigned to the
        # responsible client
        if not ogview.is_user_assigned_to_client(responsible_client):
            return False

        # accept is not possible if the responsible client is the current
        # client, since accept creates a successor forwarding in the
        # responsible client's inbox (which is here and may cause
        # duplicates)
        if responsible_client == ogview.client_id():
            return False

        return True

    def is_assign_to_dossier_possible(self):
        """see IForwardingTransitionController
        """
        ogview = self.context.restrictedTraverse('@@opengever_view')
        stateview = self.context.restrictedTraverse(
            '@@plone_portal_state')

        # Manager user can assign always:
        if 'Manager' in stateview.member().getRolesInContext(
            self.context):
            return True

        # transition is only possible if the user is assigned to this
        # client:
        if not ogview.is_user_assigned_to_client():
            return False

        return True

    def is_close_possible(self):
        """see IForwardingTransitionController
        """
        ogview = self.context.restrictedTraverse('@@opengever_view')
        stateview = self.context.restrictedTraverse(
            '@@plone_portal_state')

        # Manager user can close always:
        if 'Manager' in stateview.member().getRolesInContext(
            self.context):
            return True

        # transition is only possible if the user is assigned to this
        # client:
        if not ogview.is_user_assigned_to_client():
            return False

        return True

    def is_refuse_possible(self):
        """see IForwardingTransitionController
        """

        ogview = self.context.restrictedTraverse('@@opengever_view')
        responsible_client = self.context.responsible_client

        # accept only possible for users assigned to the
        # responsible client
        if not ogview.is_user_assigned_to_client(responsible_client):
            return False

        # accept is not possible if the responsible client is the current
        # client, since accept creates a successor forwarding in the
        # responsible client's inbox (which is here and may cause
        # duplicates)
        if responsible_client == ogview.client_id():
            return False

        return True
