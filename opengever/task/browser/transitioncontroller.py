from Acquisition import aq_parent
from opengever.base.interfaces import IInternalWorkflowTransition
from opengever.dossier.base import DOSSIER_STATES_OPEN
from opengever.globalindex.model.task import Task
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.ogds.base.utils import ogds_service
from opengever.task import FINISHED_TASK_STATES
from opengever.task.browser.delegate.main import DelegateTask
from opengever.task.browser.modify_deadline import ModifyDeadlineFormView
from opengever.task.interfaces import IDeadlineModifier
from opengever.task.task import ITask
from opengever.task.util import get_documents_of_task
from plone import api
from plone.protect.utils import addTokenToUrl
from Products.Five import BrowserView
from zExceptions import NotFound
from zope.globalrequest import getRequest
from zope.interface import implements
from zope.interface import Interface


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


def agency_guard(transition):
    """Decorator for marking a function as agency-guard for
    a specific `transition`.
    """
    def _agency_guard_decorator(func):
        assert getattr(func, '_action_transitions', None) is None, \
            '@action and @guard cannot be used for the same function.'
        if getattr(func, '_guard_transitions', None) is None:
            func._guard_transitions = []
        func._guard_transitions.append(transition)
        return func
    return _agency_guard_decorator


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
            return self.request.RESPONSE.redirect(addTokenToUrl(url))

    def _is_transition_possible(self, transition, include_agency, checker):
        guard = self._get_function_for_transition('guard', transition)
        # this is an unbound method

        if not guard:
            return None

        return guard(self, checker, include_agency)

    def is_transition_possible(self, transition, include_agency=True):
        """Returns `True` if the current user can execute the
        `transition` on the current task.
        """
        return self._is_transition_possible(
            transition, include_agency, get_checker(self.context))

    def get_transition_action(self, transition):
        """Returns the action URL for executing the `transition`
        on the current context.
        """

        action_url_generator = self._get_function_for_transition(
            'action', transition)

        if not action_url_generator:
            return ''

        return action_url_generator(
            self, transition, get_checker(self.context))

    # ------------ workflow implementation --------------

    @guard('task-transition-delegate')
    def delegate_guard(self, c, include_agency):
        return api.user.has_permission('Modify portal content', obj=self.context)

    @action('task-transition-delegate')
    def delegate_action(self, transition, c):
        # drop transition, it is not relevant here.
        return DelegateTask.url_for(self.context)

    @guard('task-transition-modify-deadline')
    def modify_deadline_guard(self, c, include_agency):
        return IDeadlineModifier(self.context).is_modify_allowed(
            include_agency=include_agency)

    @action('task-transition-modify-deadline')
    def modify_deadline_action(self, transition, c):
        return ModifyDeadlineFormView.url_for(self.context, transition)

    @guard('task-transition-open-planned')
    def planned_guard(self, transition, c):
        return IInternalWorkflowTransition.providedBy(getRequest())

    @guard('task-transition-planned-open')
    def open_guard(self, transition, c):
        return IInternalWorkflowTransition.providedBy(getRequest())

    @guard('task-transition-cancelled-open')
    def cancelled_to_open_guard(self, c, include_agency):
        """Checks if:
        - The containing dossier's state is not whitelisted
        - The current user is the issuer of the current task(context)
        """
        whitelisted_dossier_states = DOSSIER_STATES_OPEN
        containing_dossier = self.context.get_containing_dossier()
        if api.content.get_state(containing_dossier) not in whitelisted_dossier_states:
            return False

        if include_agency:
            return (c.current_user.is_issuer
                    or c.current_user.in_issuing_orgunits_inbox_group
                    or c.current_user.is_administrator)

        return c.current_user.is_issuer

    @action('task-transition-cancelled-open')
    def cancelled_to_open_action(self, transition, c):
        return self._addresponse_form_url(transition)

    @guard('task-transition-in-progress-resolved')
    def progress_to_resolved_guard(self, c, include_agency):
        """Checks if:
        - The current_user is the responsible.
        - All subtaskes are in a finished state(resolve, cancelled or closed).
        - The task has no successors

        Agency:
         - The task can also be resolved when user is not the responsible
        but in the responsible_org_unit's inbox group.
        """
        if not c.task.all_subtasks_finished:
            return False

        if c.task.has_successors and not c.request.is_remote:
            return False

        if include_agency:
            return (c.current_user.is_responsible
                    or c.current_user.in_responsible_orgunits_inbox_group
                    or c.current_user.is_administrator)
        else:
            return c.current_user.is_responsible

    @guard('task-transition-in-progress-resolved')
    @task_type_category('unidirectional_by_value')
    def unival_progress_to_resolved_guard(self, c, include_agency):
        return False

    @action('task-transition-in-progress-resolved')
    def progress_to_resolved_action(self, transition, c):
        return self._addresponse_form_url(transition)

    @action('task-transition-in-progress-resolved')
    @task_type_category('bidirectional_by_reference')
    @task_type_category('bidirectional_by_value')
    def bi_progress_to_resolved_action(self, transition, c):
        if c.task.is_successor and not c.task.is_forwarding_successor:
            return '%s/@@complete_successor_task?transition=%s' % (
                self.context.absolute_url(), transition)
        else:
            return self._addresponse_form_url(transition)

    @guard('task-transition-in-progress-tested-and-closed')
    def progress_to_closed_guard(self, c, include_agency):
        """This transition is by default not available. It is only available
        for unidirectional_by_value tasks.
        """
        return False

    @guard('task-transition-in-progress-tested-and-closed')
    @task_type_category('unidirectional_by_value')
    def unival_progress_to_closed_guard(self, c, include_agency):
        """Checks if:
        - The current user is the responsible or a member of the inbox group.
        - All subtaskes are rejected, cancelled or closed.
        - The task has no successors or is a remote request
        """

        if not c.task.all_subtasks_finished:
            return False

        if c.task.has_successors and not c.request.is_remote:
            return False

        if include_agency:
            return (c.current_user.is_responsible
                    or c.current_user.in_responsible_orgunits_inbox_group
                    or c.current_user.is_administrator)
        else:
            return c.current_user.is_responsible

    @action('task-transition-in-progress-tested-and-closed')
    def progress_to_closed_action(self, transition, c):
        return self._addresponse_form_url(transition)

    @action('task-transition-in-progress-tested-and-closed')
    @task_type_category('unidirectional_by_reference')
    @task_type_category('unidirectional_by_value')
    def uni_progress_to_closed_action(self, transition, c):
        if c.task.is_successor and not c.task.is_forwarding_successor:
            return '%s/@@complete_successor_task?transition=%s' % (
                self.context.absolute_url(),
                transition)
        else:
            return self._addresponse_form_url(transition)

    @guard('task-transition-open-cancelled')
    def open_to_cancelled_guard(self, c, include_agency):
        """Checks if:
        - The task is not a subtask of a tasktemplate process
        - The current user is the issuer
        """

        if self.context.is_from_tasktemplate and self.context.get_is_subtask():
            return False

        if include_agency:
            return (c.current_user.is_issuer
                    or c.current_user.in_issuing_orgunits_inbox_group
                    or c.current_user.is_administrator)

        return c.current_user.is_issuer

    @guard('task-transition-in-progress-cancelled')
    def progress_to_cancelled_guard(self, c, include_agency):
        """Checks if:
        The task is generated from tasktemplate and its the main task.
        """
        return self.context.is_from_tasktemplate and not \
            ITask.providedBy(aq_parent(self.context))

    @action('task-transition-in-progress-cancelled')
    def progress_to_cancelled_action(self, transition, c):
        return self._addresponse_form_url(transition)

    @action('task-transition-open-cancelled')
    def open_to_cancelled_action(self, transition, c):
        return self._addresponse_form_url(transition)

    @guard('task-transition-open-in-progress')
    def open_to_progress_guard(self, c, include_agency):
        """Checks if ...
        - The current user is the responsible or a member of the inbox group.
        """
        if include_agency:
            return (c.current_user.is_responsible
                    or c.current_user.in_responsible_orgunits_inbox_group
                    or c.current_user.is_administrator)

        return c.current_user.is_responsible

    @action('task-transition-open-in-progress')
    def open_to_progress_action(self, transition, c):
        if c.task.is_assigned_to_current_admin_unit:
            return self._addresponse_form_url(transition)
        else:
            return '%s/@@accept_choose_method' % self.context.absolute_url()

    @guard('task-transition-open-in-progress')
    @task_type_category('unidirectional_by_reference')
    def uniref_open_to_progress_guard(self, c, include_agency):
        return False

    @guard('task-transition-open-rejected')
    def open_to_rejected_guard(self, c, include_agency):
        """Checks if ...
        - The current user is the responsible or a member of the inbox group.
        """

        if include_agency:
            return (c.current_user.is_responsible
                    or c.current_user.in_responsible_orgunits_inbox_group
                    or c.current_user.is_administrator)

        return c.current_user.is_responsible

    @action('task-transition-open-rejected')
    def open_to_rejected_action(self, transition, c):
        return self._addresponse_form_url(transition)

    @guard('task-transition-open-resolved')
    def open_to_resolved_guard(self, c, include_agency):
        """Checks if:
        - The Task is is_bidirectional
        - The current user is the responsible or a member of the inbox group.
        """

        if include_agency:
            return (c.current_user.is_responsible
                    or c.current_user.in_responsible_orgunits_inbox_group
                    or c.current_user.is_administrator)

        return c.current_user.is_responsible

    @guard('task-transition-open-resolved')
    @task_type_category('unidirectional_by_reference')
    @task_type_category('unidirectional_by_value')
    def uni_open_to_resolved_guard(self, c, include_agency):
        """Transition is not available for unidirectional tasks.
        """
        return False

    @action('task-transition-open-resolved')
    def open_to_resolved_action(self, transition, c):
        return self._addresponse_form_url(transition)

    @guard('task-transition-open-tested-and-closed')
    def open_to_closed_guard(self, c, include_agency):
        """Checks if:
        - The current user is the issuer
        """

        if include_agency:
            return (c.current_user.is_issuer
                    or c.current_user.in_issuing_orgunits_inbox_group
                    or c.current_user.is_administrator)

        return c.current_user.is_issuer

    @action('task-transition-open-tested-and-closed')
    def open_to_closed_action(self, transition, c):
        return self._addresponse_form_url(transition)

    @guard('task-transition-open-tested-and-closed')
    @task_type_category('unidirectional_by_reference')
    def uniref_open_to_closed_guard(self, c, include_agency):
        """Checks if:
        - It's a unidirectional_byrefrence task
        - Current user is the responsible or a member of the inbox group.
        """
        if include_agency:
            return (c.current_user.is_responsible
                    or c.current_user.in_responsible_orgunits_inbox_group
                    or c.current_user.is_administrator)

        return c.current_user.is_responsible

    @action('task-transition-open-tested-and-closed')
    @task_type_category('unidirectional_by_reference')
    def uniref_open_to_closed_action(self, transition, c):
        if c.task.is_assigned_to_current_admin_unit:
            return self._addresponse_form_url(transition)

        elif len(get_documents_of_task(
                self.context, include_mails=True)) == 0:
            return self._addresponse_form_url(transition)

        else:
            return '%s/@@close-task-wizard_select-documents' % (
                self.context.absolute_url())

    @guard('task-transition-reassign')
    def reassign_guard(self, c, include_agency):
        return api.user.has_permission('Modify portal content', obj=self.context)

    @action('task-transition-reassign')
    def reassign_action(self, transition, c):
        return '%s/@@assign-task?form.widgets.transition=%s' % (
            self.context.absolute_url(),
            transition)

    @guard('task-transition-rejected-open')
    def rejected_to_open_guard(self, c, include_agency):
        """Checks if:
        - The current user is the issuer of the task"""

        if include_agency:
            return c.current_user.is_issuer or c.current_user.is_administrator

        return c.current_user.is_issuer

    @action('task-transition-rejected-open')
    def rejected_to_open_action(self, transition, c):
        return self._addresponse_form_url(transition)

    @guard('task-transition-rejected-skipped')
    def rejected_to_skipped_guard(self, c, include_agency):
        """Checks if:
        - The current user is the issuer of the task
        - The task is part of a task process
        """
        if not self.context.is_from_sequential_tasktemplate:
            return False

        if include_agency:
            return c.current_user.is_issuer or c.current_user.is_administrator

        return c.current_user.is_issuer

    @action('task-transition-rejected-skipped')
    def rejected_to_skipped_action(self, transition, c):
        return self._addresponse_form_url(transition)

    @guard('task-transition-planned-skipped')
    def planned_to_skipped_guard(self, c, include_agency):
        """Checks if:
        - The current user is the issuer of the task"""

        # The check that the task is part of a task sequence is unnecessary,
        # because only tasks from a sequene can be in the planned state.

        if include_agency:
            return c.current_user.is_issuer or c.current_user.is_administrator

        return c.current_user.is_issuer

    @action('task-transition-planned-skipped')
    def planned_to_skipped_action(self, transition, c):
        return self._addresponse_form_url(transition)

    @guard('task-transition-skipped-open')
    def skipped_to_open_guard(self, c, include_agency):
        """Checks if:
        - The current user is the issuer of the task"""

        if include_agency:
            return c.current_user.is_issuer or c.current_user.is_administrator

        return c.current_user.is_issuer

    @action('task-transition-skipped-open')
    def skipped_to_open_action(self, transition, c):
        return self._addresponse_form_url(transition)

    @guard('task-transition-resolved-tested-and-closed')
    def resolved_to_closed_guard(self, c, include_agency):
        """Checks if:
        - The current user is the issuer of the task"""

        if include_agency:
            return (c.current_user.is_issuer
                    or c.current_user.in_issuing_orgunits_inbox_group
                    or c.current_user.is_administrator)

        return c.current_user.is_issuer

    @action('task-transition-resolved-tested-and-closed')
    def resolved_to_closed_action(self, transition, c):
        return self._addresponse_form_url(transition)

    @guard('task-transition-resolved-in-progress')
    def resolved_to_progress_guard(self, c, include_agency):
        """Checks if:
        - The current user is the issuer of the task"""

        if c.current_user.is_issuer:
            return True

        if include_agency:
            return (c.current_user.is_responsible
                    or c.current_user.in_responsible_orgunits_inbox_group
                    or c.current_user.is_administrator)

        return c.current_user.is_responsible

    @action('task-transition-resolved-in-progress')
    def resolved_to_progress_action(self, transition, c):
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

    def _addresponse_form_url(self, transition):
        """Returns the redirect url to the addresponse, passing `transition`.
        """
        return '%s/addresponse?form.widgets.transition=%s' % (
            self.context.absolute_url(),
            transition)


class Checker(object):

    def __init__(self, task, request, current_user):
        self._task = task
        self._request = request
        self._current_user = current_user

    @property
    def current_user(self):
        return CurrentUserChecker(self._current_user, self._task)

    @property
    def task(self):
        return TaskChecker(self._task)

    @property
    def request(self):
        return RequestChecker(self._request)


class CurrentUserChecker(object):

    def __init__(self, current_user, task):
        self.current_user = current_user
        self.task = task

    @property
    def is_issuer(self):
        return self.task.issuer_actor.corresponds_to(self.current_user)

    @property
    def is_responsible(self):
        return self.task.responsible_actor.corresponds_to(self.current_user)

    @property
    def in_issuing_orgunits_inbox_group(self):
        """Returns true, if the current user is within the inbox group of
        the issuing orgunit.

        returns false, if the task is private. This deactivates agency-support
        for private tasks
        """
        if self.task.is_private:
            return False

        inbox = self.task.get_issuing_org_unit().inbox()
        return self.current_user in inbox.assigned_users()

    @property
    def in_responsible_orgunits_inbox_group(self):
        """Returns true, if the current user is within the inbox group of
        the responsible orgunit.

        returns false, if the task is private. This deactivates agency-support
        for private tasks
        """
        if self.task.is_private:
            return False

        inbox = self.task.get_assigned_org_unit().inbox()
        return self.current_user in inbox.assigned_users()

    @property
    def is_administrator(self):
        current = api.user.get_current()
        return bool(current.has_role('Administrator')
                    or current.has_role('Manager'))


class TaskChecker(object):

    def __init__(self, task):
        self.task = task

    @property
    def all_subtasks_finished(self):

        task = self.task

        if task.predecessor is not None:
            query = Task.query.subtasks_by_tasks([task, task.predecessor])
        else:
            query = Task.query.subtasks_by_task(task)

        query = query.filter(
            ~Task.query._attribute('review_state').in_(FINISHED_TASK_STATES))

        if query.count() > 0:
            return False
        return True

    @property
    def has_successors(self):
        return bool(self.task.successors)

    @property
    def is_successor(self):
        return self.task.is_successor

    @property
    def is_forwarding_successor(self):
        return self.task.predecessor.is_forwarding

    @property
    def is_assigned_to_current_admin_unit(self):
        org_unit = self.task.get_assigned_org_unit()
        return org_unit.admin_unit == get_current_admin_unit()


class RequestChecker(object):

    def __init__(self, request):
        self.request = request

    @property
    def is_remote(self):
        return bool(self.request.get_header('X-OGDS-AUID', False))

    @property
    def is_successor_process(self):
        return bool(self.request.get('X-CREATING-SUCCESSOR', False))


def get_checker(context):
    return Checker(
        context.get_sql_object(), context.REQUEST,
        ogds_service().fetch_current_user())
