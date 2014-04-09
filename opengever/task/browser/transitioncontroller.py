from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from opengever.ogds.base.interfaces import IContactInformation
from opengever.ogds.base.utils import get_client_id
from opengever.task.interfaces import ISuccessorTaskController
from opengever.task.util import get_documents_of_task
from zExceptions import NotFound
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.interface import Interface, implements

TASK_CLOSED_STATES = ['task-state-tested-and-closed',
                      'task-state-rejected',
                      'task-state-cancelled']


class ITaskTransitionController(Interface):
    """Interface for a controller view for checking,
    if certain transitions should be available or not"""

    def is_transition_possible(transition):
        """Returns `True` if the current user can execute the
        `transition` on the current task.
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


def task_type_category(category):
    """Decorator for making a guard or action specific to a task type
    category.
    """
    def _category_decorator(func):
        if getattr(func, '_filter_categories', None) is None:
            func._filter_categories = []
        func._filter_categories.append(category)
        return func
    return _category_decorator


class TaskTransitionController(BrowserView):
    """Controller View: see ITaskTransitionController"""

    implements(ITaskTransitionController)

    # ------------ public interface --------------

    def __call__(self):
        transition = self.request.get('transition')
        if not self.is_transition_possible(transition):
            raise NotFound

        else:
            url = self.get_transition_action(transition)
            return self.request.RESPONSE.redirect(url)

    def is_transition_possible(self, transition):
        """Returns `True` if the current user can execute the
        `transition` on the current task.
        """

        # do not check the guards for adminstrators
        if self._is_administrator():
            return True

        guard = self._get_function_for_transition('guard', transition)
        # this is an unbound method

        if not guard:
            return None

        return guard(self)

    def get_transition_action(self, transition):
        """Returns the action URL for executing the `transition`
        on the current context.
        """

        action_url_generator = self._get_function_for_transition(
            'action', transition)

        if not action_url_generator:
            return ''

        # this is an unbound method
        return action_url_generator(self, transition)

    # ------------ workflow implementation --------------

    @guard('task-transition-cancelled-open')
    def cancelled_to_open_guard(self):
        """Checks if:
        - The current user is the issuer of the current task(context)"""
        return self._is_issuer()

    @action('task-transition-cancelled-open')
    def cancelled_to_open_action(self, transition):
        return self._addresponse_form_url(transition)

    @guard('task-transition-in-progress-resolved')
    def progress_to_resolved_guard(self):
        """Checks if:
        - The responsible is the current user or a inbox_group user.
        - All subtaskes are resolve, cancelled or closed.
        - The task has no successors
        """
        return (self._is_responsible_or_inbox_group_user() and
                self._is_substasks_closed() and
                (not self._has_successors() or self._is_remote_request()))

    @guard('task-transition-in-progress-resolved')
    @task_type_category('unidirectional_by_value')
    def unival_progress_to_resolved_guard(self):
        return False

    @action('task-transition-in-progress-resolved')
    def progress_to_resolved_action(self, transition):
        return self._addresponse_form_url(transition)

    @action('task-transition-in-progress-resolved')
    @task_type_category('bidirectional_by_reference')
    @task_type_category('bidirectional_by_value')
    def bi_progress_to_resolved_action(self, transition):
        if self._is_close_successor_wizard_possible(transition):
            return '%s/@@complete_successor_task?transition=%s' % (
                self.context.absolute_url(),
                transition)
        else:
            return self._addresponse_form_url(transition)

    @guard('task-transition-in-progress-tested-and-closed')
    def progress_to_closed_guard(self):
        """This transition is by default not available. It is only available
        for unidirectional_by_value tasks.
        """
        return False

    @guard('task-transition-in-progress-tested-and-closed')
    @task_type_category('unidirectional_by_value')
    def unival_progress_to_closed_guard(self):
        """Checks if:
        - The current user is the responsible or a member of the inbox group.
        - All subtaskes are resolved, cancelled or closed.
        - The task has no successors or is a remote request
        """
        return (self._is_responsible_or_inbox_group_user() and
                self._is_substasks_closed() and
                (not self._has_successors() or self._is_remote_request()))

    @action('task-transition-in-progress-tested-and-closed')
    def progress_to_closed_action(self, transition):
        return self._addresponse_form_url(transition)

    @action('task-transition-in-progress-tested-and-closed')
    @task_type_category('unidirectional_by_reference')
    @task_type_category('unidirectional_by_value')
    def uni_progress_to_closed_action(self, transition):
        if self._is_close_successor_wizard_possible(transition):
            return '%s/@@complete_successor_task?transition=%s' % (
                self.context.absolute_url(),
                transition)
        else:
            return self._addresponse_form_url(transition)

    @guard('task-transition-open-cancelled')
    def open_to_cancelled_guard(self):
        """Checks if:
        - The current user is the issuer."""
        return self._is_issuer()

    @action('task-transition-open-cancelled')
    def open_to_cancelled_action(self, transition):
        return self._addresponse_form_url(transition)

    @guard('task-transition-open-in-progress')
    def open_to_progress_guard(self):
        """Checks if ...
        - The current user is the responsible or a member of the inbox group.
        """
        return self._is_responsible_or_inbox_group_user()

    @action('task-transition-open-in-progress')
    def open_to_progress_action(self, transition):
        if not self._is_multiclient_setup():
            return self._addresponse_form_url(transition)

        elif self._is_task_on_responsible_client():
            return self._addresponse_form_url(transition)

        else:
            return '%s/@@accept_choose_method' % self.context.absolute_url()

    @guard('task-transition-open-in-progress')
    @task_type_category('unidirectional_by_reference')
    def uniref_open_to_progress_guard(self):
        return False

    @guard('task-transition-open-rejected')
    def open_to_rejected_guard(self):
        """Checks if ...
        - The current user is the responsible or a member of the inbox group.
        """
        return self._is_responsible_or_inbox_group_user()

    @action('task-transition-open-rejected')
    def open_to_rejected_action(self, transition):
        return self._addresponse_form_url(transition)

    @guard('task-transition-open-resolved')
    def open_to_resolved_guard(self):
        """Checks if:
        - The Task is is_bidirectional
        - The current user is the responsible or a member of the inbox group.
        """
        return self._is_responsible_or_inbox_group_user()

    @guard('task-transition-open-resolved')
    @task_type_category('unidirectional_by_reference')
    @task_type_category('unidirectional_by_value')
    def uni_open_to_resolved_guard(self):
        """Transition is not available for unidirectional tasks.
        """
        return False

    @action('task-transition-open-resolved')
    def open_to_resolved_action(self, transition):
        return self._addresponse_form_url(transition)

    @action('task-transition-open-resolved')
    @task_type_category('bidirectional_by_reference')
    @task_type_category('bidirectional_by_value')
    def bi_open_to_resolved_action(self, transition):
        if self._is_close_successor_wizard_possible(transition):
            return '%s/@@complete_successor_task?transition=%s' % (
                self.context.absolute_url(),
                transition)
        else:
            return self._addresponse_form_url(transition)

    @guard('task-transition-open-tested-and-closed')
    def open_to_closed_guard(self):
        """Checks if:
        - The current user is the issuer
        """
        return self._is_issuer_or_inbox_group_user()

    @action('task-transition-open-tested-and-closed')
    def open_to_closed_action(self, transition):
        return self._addresponse_form_url(transition)

    @guard('task-transition-open-tested-and-closed')
    @task_type_category('unidirectional_by_reference')
    def uniref_open_to_closed_guard(self):
        """Checks if:
        - It's a unidirectional_byrefrence task
        - Current user is the responsible or a member of the inbox group.
        """
        return self._is_responsible_or_inbox_group_user()

    @action('task-transition-open-tested-and-closed')
    @task_type_category('unidirectional_by_reference')
    def uniref_open_to_closed_action(self, transition):
        if not self._is_multiclient_setup():
            return self._addresponse_form_url(transition)

        elif self._is_task_on_responsible_client():
            return self._addresponse_form_url(transition)

        elif len(get_documents_of_task(
                self.context, include_mails=True)) == 0:
            return self._addresponse_form_url(transition)

        else:
            return '%s/@@close-task-wizard_select-documents' % (
                self.context.absolute_url())

    @guard('task-transition-reassign')
    def reassign_guard(self):
        return True

    @action('task-transition-reassign')
    def reassign_action(self, transition):
        return '%s/@@assign-task?form.widgets.transition=%s' % (
            self.context.absolute_url(),
            transition)

    @guard('task-transition-rejected-open')
    def rejected_to_open_guard(self):
        """Checks if:
        - The current user is the issuer of the task"""
        return self._is_issuer()

    @action('task-transition-rejected-open')
    def rejected_to_open_action(self, transition):
        return self._addresponse_form_url(transition)

    @guard('task-transition-resolved-tested-and-closed')
    def resolved_to_closed_guard(self):
        """Checks if:
        - The current user is the issuer of the task"""
        return self._is_issuer_or_inbox_group_user()

    @action('task-transition-resolved-tested-and-closed')
    def resolved_to_closed_action(self, transition):
        return self._addresponse_form_url(transition)

    @guard('task-transition-resolved-in-progress')
    def resolved_to_progress_guard(self):
        """Checks if:
        - The current user is the issuer of the task"""
        return (
            self._is_issuer() or
            self._is_responsible_or_inbox_group_user())

    @action('task-transition-resolved-in-progress')
    def resolved_to_progress_action(self, transition):
        return self._addresponse_form_url(transition)

    # ------------ helper functions --------------
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

        functions = self._get_functions_with(argname, transition)
        return self._filter_function_for_tasktype(functions)

    def _filter_function_for_tasktype(self, functions):
        """Picks the right function from a list of `functions`, based on the
        task_type_category decorator used on the functions.
        """
        if len(functions) == 0:
            return None

        elif len(functions) == 1:
            return functions[0]

        category = self.context.task_type_category
        default = None

        for func in functions:
            filter_categories = getattr(func, '_filter_categories', None)
            if filter_categories is None:
                default = func
            elif category in filter_categories:
                return func

        return default

    def _get_functions_with(self, argname, value):
        """Returns all functions of the transition controller,
        where `value` is in the value of the function-attribute `argname`.
        """

        functions = []
        instance = self.__class__

        for name in dir(instance):
            obj = getattr(instance, name, None)
            argvalue = getattr(obj, argname, None)
            if argvalue is not None and value in argvalue:
                functions.append(obj)

        return functions

    def _is_issuer(self, include_inbox_group=False):
        """Checks if the current user is the issuer of the
        current task(current context)"""

        info = getUtility(IContactInformation)

        if not info.is_inbox(self.context.issuer):
            member_id = getMultiAdapter((self.context, self.request),
                name='plone_portal_state').member().id
            if member_id == self.context.issuer:
                return True
            elif include_inbox_group and self._is_issuer_inbox_group_user():
                return True
            else:
                return False

        else:
            inbox_groupid = info.get_groupid_of_inbox(self.context.issuer)
            return info.is_group_member(
                inbox_groupid,
                getMultiAdapter((self.context, self.request),
                                name='plone_portal_state').member().id
                )

    def _is_issuer_or_inbox_group_user(self):
        """Checks if the current user is the issuer of the
        current task(current context) or a user of the current inbox group"""

        return self._is_issuer(include_inbox_group=True)

    def _is_responsible(self):
        """Checks if the current user is the issuer of the
        current task(current context)"""

        return getMultiAdapter((self.context, self.request),
            name='plone_portal_state').member().id == self.context.responsible

    def _is_inbox_group_user(self):
        """Checks with the help of the contact information utility
        if the current user is in the inbox group"""

        info = getUtility(IContactInformation)
        return info.is_user_in_inbox_group(
            client_id=self.context.responsible_client)

    def _is_issuer_inbox_group_user(self):
        """Checks with the helpt of the contact information utility
        if the current user is in the inbox group of the current client.
        """
        info = getUtility(IContactInformation)
        if self._is_remote_request() or info.is_user_in_inbox_group():
            return True
        return False

    def _is_responsible_or_inbox_group_user(self):
        """Checks if the current user is the responsible
        or in the inbox_group"""

        return self._is_responsible() or self._is_inbox_group_user()

    def _is_substasks_closed(self):
        """Checks if all subtasks are done(resolve, cancelled or closed)"""

        wft = self.context.portal_workflow
        wf = wft.get(wft.getChainFor(self.context)[0])
        states = [s for s in wf.states]

        for state in TASK_CLOSED_STATES:
            states.pop(states.index(state))

        query = {
            'path': {
                'query': '/'.join(self.context.getPhysicalPath()),
                'depth': -1},
            'portal_type': 'opengever.task.task',
            'review_state': states}

        if len(self.context.getFolderContents(query)) > 1:
            return False
        else:
            return True

    def _is_remote_request(self):
        """checks if the current request cames from a remote client.
        For example a task over a mutliple clients."""

        if self.request.get_header('X-OGDS-CID', None):
            return True
        else:
            return False

    def _has_successors(self):
        """checks is the task has some successors
        """
        if ISuccessorTaskController(self.context).get_successors():
            return True
        return False

    def _is_multiclient_setup(self):
        info = getUtility(IContactInformation)
        return len(info.get_clients()) > 1

    def _is_task_on_responsible_client(self):
        """Returns true if the current client is the responsible-client of
        the task.
        """
        return get_client_id() == self.context.responsible_client

    def _addresponse_form_url(self, transition):
        """Returns the redirect url to the addresponse, passing `transition`.
        """
        return '%s/addresponse?form.widgets.transition=%s' % (
            self.context.absolute_url(),
            transition)

    def _is_close_successor_wizard_possible(self, transition):
        if not self._is_responsible_or_inbox_group_user():
            return False

        elif not self.context.predecessor:
            return False

        # check if the predessecor is a forwarding
        # in this case the successor wizard isn't possible and necessary
        elif ISuccessorTaskController(self.context).get_predecessor(
                ).task_type == u'forwarding_task_type':
            return False

        else:
            return True

    def _is_administrator(self):
        """check if the user is a adminstrator"""

        member = getToolByName(
            self.context, 'portal_membership').getAuthenticatedMember()

        return member.has_role('Administrator') or member.has_role('Manager')
