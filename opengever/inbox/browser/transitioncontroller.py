"""Contains a Controller wich checks the Transitions"""
from opengever.ogds.base.interfaces import IContactInformation
from opengever.task.browser.transitioncontroller import TaskTransitionController
from opengever.task.browser.transitioncontroller import guard, action
from zope.component import getUtility


class ForwardingTransitionController(TaskTransitionController):
    """see IForwardingTransitionController
    """

    @guard('forwarding-transition-accept')
    @guard('forwarding-transition-refuse')
    def is_accept_possible(self):
        """Check if the user is in the inbox group of the responsible client.
        """

        if not self._is_multiclient_setup():
            return False
        elif (not self._is_task_on_responsible_client() and
              not self._is_succesor_forwarding_proccses()):
            return False
        else:
            return self._is_inbox_group_user()

    @action('forwarding-transition-accept')
    def accept_action(self, transition):
        """redirect to the accept_choose_method Wizzard"""

        return '%s/@@accept_choose_method' % (
            self.context.absolute_url())

    @guard('forwarding-transition-assign-to-dossier')
    @guard('forwarding-transition-reassign')
    @guard('forwarding-transition-close')
    def is_assign_to_dossier_or_reassign_possible(self):
        """Check it the user is in the inbox group of the current client.
        """
        return self._is_current_inbox_group_user()

    @action('forwarding-transition-assign-to-dossier')
    def assign_to_dossier_action(self, transition):
        """redirect to the choose method view
        """
        return '%s/@@assign_choose_method' % (
            self.context.absolute_url())

    @action('forwarding-transition-reassign')
    def reassign_action(self, transition):
        """redirect to the assign task form,
        which allows to set a new responsible.
        """
        return '%s/@@assign-task?form.widgets.transition=%s' % (
            self.context.absolute_url(),
            transition)

    @action('forwarding-transition-refuse')
    def refuse_action(self, transition):
        """redirect to the assign task form,
        so that it automaticly set the home inbox as responsible
        """
        return '%s/@@refuse-task?form.widgets.transition=%s' % (
            self.context.absolute_url(),
            transition)

    @action('forwarding-transition-close')
    def close_action(self, transition):
        """redirect to the addresponse form, the closing mechanism
        (storing in a yearfolder) would be started from event handler.
        """
        return self._addresponse_form_url(transition)

    def _is_current_inbox_group_user(self):
        """Checks with the help of the contact information utility
        if the current user is in the inbox group of the current client"""

        info = getUtility(IContactInformation)
        return info.is_user_in_inbox_group()

    def _is_succesor_forwarding_proccses(self):
        """Check if the request is directly from
        the forwarding successor handler."""

        if self.request.get('X-CREATING-SUCCESSOR') == True:
            return True
        return False
