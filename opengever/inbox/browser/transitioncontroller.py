"""Contains a Controller wich checks the Transitions"""
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.task.browser.transitioncontroller import guard, action
from opengever.task.browser.transitioncontroller import TaskTransitionController


class ForwardingTransitionController(TaskTransitionController):
    """see IForwardingTransitionController
    """

    @guard('forwarding-transition-accept')
    @guard('forwarding-transition-refuse')
    def is_accept_possible(self, conditions, include_agency):
        """Check if the user is in the inbox group of the responsible client.
        """

        if conditions.is_assigned_to_current_admin_unit and \
           not conditions.is_successor_process:
            return False

        return conditions.is_responsible

    def _is_task_assigned_to_current_admin_unit(self):
        return self.context.get_responsible_admin_unit() == get_current_admin_unit()

    @action('forwarding-transition-accept')
    def accept_action(self, transition):
        """redirect to the accept_choose_method Wizzard"""

        return '%s/@@accept_choose_method' % (
            self.context.absolute_url())

    @guard('forwarding-transition-assign-to-dossier')
    @guard('forwarding-transition-reassign')
    @guard('forwarding-transition-close')
    @guard('forwarding-transition-reassign-refused')
    def is_assign_to_dossier_or_reassign_possible(self, conditions, include_agency):
        """Check it the user is in the inbox group of the current client.
        """
        if include_agency:
            return (conditions.is_assigned_to_current_admin_unit and
                    conditions.is_responsible_orgunit_agency_member)

        return (conditions.is_assigned_to_current_admin_unit and
                conditions.is_responsible)

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

    @action('forwarding-transition-reassign-refused')
    def reassign_refused_action(self, transition):
        """redirect to the assign refused forwarding form,
        which allows to set a new responsible and responsible_client."""

        return '%s/@@assign-forwarding?form.widgets.transition=%s' % (
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
        """redirect to the close-forwarding form, which handle the whole
        closing mechanism (storing in a yearfolder).
        """
        return '%s/@@close-forwarding' % (self.context.absolute_url())

    def _is_successor_forwarding_process(self):
        """Check if the request is directly from
        the forwarding successor handler."""

        return bool(self.request.get('X-CREATING-SUCCESSOR', False))
