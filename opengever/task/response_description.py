from opengever.ogds.base.actor import Actor
from opengever.task import _


class ResponseDescription(object):
    registry = None

    @classmethod
    def add_description(cls, subcls):
        if not cls.registry:
            cls.registry = {}

        if hasattr(subcls, 'transition'):
            cls.registry[subcls.transition] = subcls
        else:
            for transition_id in subcls.transitions:
                cls.registry[transition_id] = subcls

    @classmethod
    def get(cls, response=None, transition=None):
        if response:
            transition = response.transition
        if not transition:
            transition = 'transition-add-subtask'

        description = cls.registry.get(transition)

        if not description:
            raise ValueError(
                'No description configured for transition {}'.format(transition))

        return description(response)

    def __init__(self, response):
        self.response = response

    def msg(self):
        return _('transition_label_default', 'Response added')

    @property
    def _msg_mapping(self):
        """Returns the default mapping for the translated msg.
        Contains only the attribute `user`, which shows the link to the creator
        """
        return {'user':self.response.creator_link()}


class Reactivate(ResponseDescription):
    transition = 'task-transition-cancelled-open'
    css_class = 'clearfix'

    def msg(self):
        return _('transition_label_reactivate', 'Reactivate by ${user}',
                 mapping=self._msg_mapping)

ResponseDescription.add_description(Reactivate)


class Reject(ResponseDescription):
    transition = 'task-transition-open-rejected'
    css_class = 'refuse'

    def msg(self):
        return _('transition_label_reject', 'Rejected by ${user}',
                 mapping=self._msg_mapping)

ResponseDescription.add_description(Reject)


class Resolve(ResponseDescription):
    transitions = ['task-transition-in-progress-resolved',
                   'task-transition-open-resolved']

    css_class = 'complete'

    def msg(self):
        return _('transition_label_resolve', 'Resolved by ${user}',
                 mapping=self._msg_mapping)

ResponseDescription.add_description(Resolve)


class Close(ResponseDescription):
    transitions = ['task-transition-in-progress-tested-and-closed',
                   'task-transition-open-tested-and-closed',
                   'task-transition-resolved-tested-and-closed',
                   'forwarding-transition-close']

    css_class = 'close'

    def msg(self):
        return _('transition_label_close', 'Closed by ${user}',
                 mapping=self._msg_mapping)

ResponseDescription.add_description(Close)


class Cancel(ResponseDescription):
    transition = 'task-transition-open-cancelled'
    css_class = 'cancelled'

    def msg(self):
        return _('transition_label_cancel', 'Cancelled by ${user}',
                 mapping=self._msg_mapping)

ResponseDescription.add_description(Cancel)


class Accept(ResponseDescription):
    transitions = ['task-transition-open-in-progress',
                   'forwarding-transition-accept']

    css_class = 'accept'

    def msg(self):
        return _('transition_label_accept', 'Accepted by ${user}',
                 mapping=self._msg_mapping)

ResponseDescription.add_description(Accept)


class Reopen(ResponseDescription):
    transition = 'task-transition-rejected-open'
    css_class = 'reopen'

    def msg(self):
        return _('transition_label_reopen', 'Reopened by ${user}',
                 mapping=self._msg_mapping)

ResponseDescription.add_description(Reopen)


class Revise(ResponseDescription):

    transition = 'task-transition-resolved-in-progress'
    css_class = 'revise'

    def msg(self):
        return _('transition_label_revise', 'Revised by ${user}',
                 mapping=self._msg_mapping)

ResponseDescription.add_description(Revise)


class Reassign(ResponseDescription):
    transitions = ['task-transition-reassign',
                   'forwarding-transition-reassign',
                   'forwarding-transition-reassign-refuse']
    css_class = 'reassign'

    def msg(self):
        change = self.response.get_change('responsible')
        responsible_new = Actor.lookup(change.get('after')).get_link()
        responsible_old = Actor.lookup(change.get('before')).get_link()

        return _('transition_label_reassign',
                 'Reassigned from ${responsible_old} to ${responsible_new} by ${user}',
                 mapping={'user': self.response.creator_link(),
                          'responsible_new': responsible_new,
                          'responsible_old': responsible_old})

ResponseDescription.add_description(Reassign)


class Refuse(ResponseDescription):

    transition = 'forwarding-transition-refuse'
    css_class = 'refuse'

    def msg(self):
        return _('transition_label_refuse', 'Refused by ${user}',
                 mapping=self._msg_mapping)

ResponseDescription.add_description(Refuse)


class AssignToDossier(ResponseDescription):

    transition = 'forwarding-transition-assign-to-dossier'
    css_class = 'assignDossier'

    def msg(self):
        return _('transition_label_assign_to_dossier',
                 'Assigned to dossier by ${user} (successor=${successor}',
                 mapping={'user':self.response.creator_link(),
                          'successor': self.get_succesor().get_link()})

ResponseDescription.add_description(AssignToDossier)


class SubTaskAdded(ResponseDescription):

    transition = 'transition-add-subtask'
    css_class = 'addSubtask'

    def msg(self):
        return _('transition_add_subtask', 'Subtask added by ${user}',
                 mapping=self._msg_mapping)

ResponseDescription.add_description(SubTaskAdded)
