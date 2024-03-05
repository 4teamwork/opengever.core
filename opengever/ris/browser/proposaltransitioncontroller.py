from opengever.ris import is_ris_feature_enabled
from opengever.ris import RIS_VIEW_TRANSITION_CANCEL
from opengever.ris import RIS_VIEW_TRANSITION_REACTIVATE
from opengever.ris import RIS_VIEW_TRANSITION_SUBMIT
from opengever.ris.interfaces import IRisSettings
from plone import api
from plone.protect.utils import addTokenToUrl
from Products.Five import BrowserView
from zExceptions import NotFound
from zope.interface import Interface


class IProposalTransitionController(Interface):
    """Interface for a controller view for checking,
    if certain transitions should be available or not"""

    def is_transition_possible(transition):
        """Returns `True` if the current user can execute the
        `transition` on the current proposal.
        """

    def get_transition_action(transition):
        """Returns the action URL for executing the `transition`
        on the current context.
        """


def guard(transition):
    """Decorator for marking a function as guard for
    a specific `transition`.
    """
    def _guard_decorator(func):
        assert getattr(func, '_action_transitions', None) is None, \
            '@action and @guard cannot be used for the same function.'
        if getattr(func, '_guard_transitions', None) is None:
            func._guard_transitions = []
        func._guard_transitions.append(transition)
        return func
    return _guard_decorator


def action(transition):
    """Decorator for marking a function as action for a
    sepcific `transition`.
    """
    def _action_decorator(func):
        assert getattr(func, '_guard_transitions', None) is None, \
            '@action and @guard cannot be used for the same function.'
        if getattr(func, '_action_transitions', None) is None:
            func._action_transitions = []
        func._action_transitions.append(transition)
        return func
    return _action_decorator


class ProposalTransitionController(BrowserView):

    def __call__(self):
        transition = self.request.get('transition')
        if not self.is_transition_possible(transition):
            raise NotFound

        url = self.get_transition_action(transition)
        return self.request.RESPONSE.redirect(addTokenToUrl(url))

    def get_transition_action(self, transition):
        action_url_generator = self._get_function_for_transition(
            'action', transition)

        return action_url_generator(self, transition)

    def is_transition_possible(self, transition):
        """Returns `True` if the current user can execute the
        `transition` on proposal..
        """
        if not is_ris_feature_enabled():
            return False

        guard = self._get_function_for_transition('guard', transition)
        if not guard:
            return True

        return guard(self)

    def _modify_workflow_state_url(self, view, transition):
        """Returns the url to the addtransitioncomment view for transition.
        """
        ris_url = api.portal.get_registry_record(
            name='base_url', interface=IRisSettings
        ).rstrip("/")
        return '{}/{}?context={}'.format(
            ris_url,
            view,
            self.context.absolute_url())

    @guard('proposal-transition-cancel')
    def cancel_guard(self):
        return api.user.has_permission(
            'Modify portal content',
            obj=self.context.get_containing_dossier(),
        )

    @action('proposal-transition-cancel')
    def cancel_action(self, transition):
        return self._modify_workflow_state_url(
            RIS_VIEW_TRANSITION_CANCEL, transition,
        )

    @guard('proposal-transition-reopen')
    def reopen_guard(self):
        return api.user.has_permission(
            'Modify portal content',
            obj=self.context.get_containing_dossier(),
        )

    @action('proposal-transition-reopen')
    def reopen_action(self, transition):
        return self._modify_workflow_state_url(
            RIS_VIEW_TRANSITION_REACTIVATE, transition,
        )

    @guard('proposal-transition-submit')
    def submit_guard(self):
        return (
            api.user.has_permission('Modify portal content', obj=self.context)
        )

    @guard('proposal-transition-submit-to-meeting')
    def submit_to_meeting_guard(self):
        return (
            api.user.has_permission('Modify portal content', obj=self.context)
        )

    @action('proposal-transition-submit')
    def submit_action(self, transition):
        return self._modify_workflow_state_url(
            RIS_VIEW_TRANSITION_SUBMIT, transition,
        )

    @guard('proposal-transition-decide')
    def decide_guard(self):
        return (
            api.user.has_permission('Modify portal content',
                                    obj=self.context.get_containing_dossier())
        )

    @guard('proposal-transition-reject')
    def reject_guard(self):
        return (
            api.user.has_permission('Modify portal content',
                                    obj=self.context.get_containing_dossier())
        )

    @guard('proposal-transition-schedule')
    def schedule_guard(self):
        return (
            api.user.has_permission('Modify portal content',
                                    obj=self.context.get_containing_dossier())
        )

    @guard('proposal-transition-unschedule')
    def unschedule_guard(self):
        return (
            api.user.has_permission('Modify portal content',
                                    obj=self.context.get_containing_dossier())
        )

    @guard('proposal-transition-unschedule-to-dossier')
    def unschedule_to_dossier_guard(self):
        return (
            api.user.has_permission('Modify portal content',
                                    obj=self.context.get_containing_dossier())
        )

    def _get_function_for_transition(self, type_, transition):
        """Returns the appropriate function (guard or action) for a
        transition.

        Arguments:
        type_ -- Either "guard" or "action"
        transition -- Name of the transition
        """

        if type_ == 'guard':
            argname = '_guard_transitions'
        elif type_ == 'action':
            argname = '_action_transitions'
        else:
            raise ValueError('type_ must be "guard" or "action"')

        return self._get_function_with(argname, transition)

    def _get_function_with(self, argname, value):
        """Returns all functions of the transition controller,
        where `value` is in the value of the function-attribute `argname`.
        """

        instance = self.__class__

        for name in dir(instance):
            obj = getattr(instance, name, None)
            argvalue = getattr(obj, argname, None)
            if argvalue is not None and value in argvalue:
                return obj

        return None
