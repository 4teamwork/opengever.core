from opengever.base.utils import to_safe_html
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
            docs, subtasks = response.get_added_objects()

            if len(subtasks):
                transition = 'transition-add-subtask'

            elif len(docs):
                transition = 'transition-add-document'

        description = cls.registry.get(transition)

        if not description:
            description = NullResponseDescription

        return description(response)

    def __init__(self, response):
        self.response = response

    def msg(self):
        return _('transition_msg_default', u'Response added')

    def label(self):
        """Returns a short description of the executed transition.
        """
        return _('transition_label_default', u'Task opened')

    @property
    def _msg_mapping(self):
        """Returns the default mapping for the translated msg.
        Contains only the attribute `user`, which shows the link to the creator
        """
        return {'user': self.response.creator_link()}


class Reactivate(ResponseDescription):
    transition = 'task-transition-cancelled-open'
    css_class = 'reactivate'

    def msg(self):
        return _('transition_msg_reactivate', u'Reactivate by ${user}',
                 mapping=self._msg_mapping)

    def label(self):
        return _('transition_label_reactivate', u'Task reactivated')


ResponseDescription.add_description(Reactivate)


class Reject(ResponseDescription):
    transition = 'task-transition-open-rejected'
    css_class = 'refuse'

    def msg(self):
        if not self.response.get_change('responsible'):
            return _('old_transition_msg_reject',
                     default=u'Rejected by ${user}.',
                     mapping=self._msg_mapping)

        return _('transition_msg_reject',
                 u'Rejected by ${old_responsible}. Task assigned to '
                 'responsible ${new_responsible}',
                 mapping=self._msg_mapping)

    def label(self):
        return _('transition_label_reject', u'Task rejected')

    @property
    def _msg_mapping(self):
        mapping = super(Reject, self)._msg_mapping
        change = self.response.get_change('responsible')
        if change:
            mapping['old_responsible'] = Actor.lookup(change.get('before')).get_link()
            mapping['new_responsible'] = Actor.lookup(change.get('after')).get_link()
        return mapping


ResponseDescription.add_description(Reject)


class Resolve(ResponseDescription):
    transitions = ['task-transition-in-progress-resolved',
                   'task-transition-open-resolved']

    css_class = 'complete'

    def msg(self):
        return _('transition_msg_resolve', u'Resolved by ${user}',
                 mapping=self._msg_mapping)

    def label(self):
        return _('transition_label_resolve', u'Task resolved')


ResponseDescription.add_description(Resolve)


class Close(ResponseDescription):
    transitions = ['task-transition-in-progress-tested-and-closed',
                   'task-transition-open-tested-and-closed',
                   'task-transition-resolved-tested-and-closed',
                   'forwarding-transition-close']

    css_class = 'close'

    def msg(self):
        return _('transition_msg_close', u'Closed by ${user}',
                 mapping=self._msg_mapping)

    def label(self):
        return _('transition_label_close', u'Task closed')


ResponseDescription.add_description(Close)


class Cancel(ResponseDescription):
    transitions = ['task-transition-open-cancelled',
                   'task-transition-in-progress-cancelled']

    css_class = 'cancelled'

    def msg(self):
        return _('transition_msg_cancel', u'Cancelled by ${user}',
                 mapping=self._msg_mapping)

    def label(self):
        return _('transition_label_cancelled', u'Task cancelled')


ResponseDescription.add_description(Cancel)


class Accept(ResponseDescription):
    transitions = ['task-transition-open-in-progress',
                   'forwarding-transition-accept']

    css_class = 'accept'

    @property
    def _msg_mapping(self):
        mapping = super(Accept, self)._msg_mapping
        change = self.response.get_change('responsible')
        if change:
            mapping['old_responsible'] = Actor.lookup(change.get('before')).get_link()
            mapping['new_responsible'] = Actor.lookup(change.get('after')).get_link()

        return mapping

    def msg(self):
        # Accepting a team task changes the responsible.
        if self.response.get_change('responsible'):
            return _(u'transition_msg_accept_team_task',
                     default=u'Accepted by ${user}, responsible changed from '
                     '${old_responsible} to ${new_responsible}.',
                     mapping=self._msg_mapping)

        return _('transition_msg_accept', u'Accepted by ${user}',
                 mapping=self._msg_mapping)

    def label(self):
        return _('transition_label_accept', u'Task accepted')


ResponseDescription.add_description(Accept)


class Reopen(ResponseDescription):
    transition = 'task-transition-rejected-open'
    css_class = 'reopen'

    def msg(self):
        return _('transition_msg_reopen', u'Reopened by ${user}',
                 mapping=self._msg_mapping)

    def label(self):
        return _('transition_label_reopen', u'Task reopened')


ResponseDescription.add_description(Reopen)


class Revise(ResponseDescription):

    transition = 'task-transition-resolved-in-progress'
    css_class = 'revise'

    def msg(self):
        return _('transition_msg_revise', u'Revised by ${user}',
                 mapping=self._msg_mapping)

    def label(self):
        return _('transition_label_revise', u'Task revised')


ResponseDescription.add_description(Revise)


class Reassign(ResponseDescription):
    transitions = ['task-transition-reassign',
                   'forwarding-transition-reassign',
                   'forwarding-transition-reassign-refused']
    css_class = 'reassign'

    def msg(self):
        change = self.response.get_change('responsible')
        responsible_new = Actor.lookup(change.get('after')).get_link()
        responsible_old = Actor.lookup(change.get('before')).get_link()

        if not change.get('before') == self.response.creator:
          return _('transition_msg_delegated_reassign',
                   u'Reassigned from ${responsible_old} to '
                   u'${responsible_new} by ${user}',
                   mapping={'user': self.response.creator_link(),
                            'responsible_new': responsible_new,
                            'responsible_old': responsible_old})

        return _('transition_msg_reassign',
                 u'Reassigned from ${responsible_old} to '
                 u'${responsible_new}',
                 mapping={'responsible_new': responsible_new,
                          'responsible_old': responsible_old})

    def label(self):
        return _('transition_label_reassign', u'Task reassigned')


ResponseDescription.add_description(Reassign)


class ModifyDeadline(ResponseDescription):

    transition = 'task-transition-modify-deadline'
    css_class = 'modifyDeadline'

    def _format_date(self, date):
        return date.strftime('%d.%m.%Y').decode('utf-8')

    def msg(self):
        change = self.response.get_change('deadline')
        new_deadline = change.get('after')
        old_deadline = change.get('before')
        return _('transition_msg_modify_deadline',
                 u'Deadline modified from ${deadline_old} to ${deadline_new} '
                 u'by ${user}',
                 mapping={'user': self.response.creator_link(),
                          'deadline_old': self._format_date(old_deadline),
                          'deadline_new': self._format_date(new_deadline)})

    def label(self):
        return _('transition_label_modify_deadline', u'Task deadline modified')


ResponseDescription.add_description(ModifyDeadline)


class Delegate(ResponseDescription):
    """At the moment no delegate responses are created but this "response" is
    only used for its action css-class.

    """
    transition = 'task-transition-delegate'
    css_class = 'delegate'

    def msg(self):
        return u''


ResponseDescription.add_description(Delegate)


class Skip(ResponseDescription):
    transitions = ['task-transition-rejected-skipped',
                   'task-transition-planned-skipped']
    css_class = 'skip'

    def msg(self):
        return _('transition_msg_skip', u'Skipped by ${user}',
                 mapping=self._msg_mapping)

    def label(self):
        return _('transition_label_skip', u'Task skipped')


ResponseDescription.add_description(Skip)


class Refuse(ResponseDescription):

    transition = 'forwarding-transition-refuse'
    css_class = 'refuse'

    def msg(self):
        return _('transition_msg_refuse', u'Refused by ${user}',
                 mapping=self._msg_mapping)

    def label(self):
        return _('transition_label_refuse', u'Forwarding refused')


ResponseDescription.add_description(Refuse)


class AssignToDossier(ResponseDescription):

    transition = 'forwarding-transition-assign-to-dossier'
    css_class = 'assignDossier'

    def msg(self):
        successor = self.response.get_succesor()
        return _('transition_msg_assign_to_dossier',
                 u'Assigned to dossier by ${user} successor=${successor}',
                 mapping={'user': self.response.creator_link(),
                          'successor': successor.get_link()})

    def label(self):
        return _('transition_label_assign_to_dossier',
                 u'Forwarding assigned to Dossier')


ResponseDescription.add_description(AssignToDossier)


class SubTaskAdded(ResponseDescription):

    transition = 'transition-add-subtask'
    css_class = 'addSubtask'

    def msg(self):
        docs, subtasks = self.response.get_added_objects()

        label = u' '.join(
            [task.get_sql_object().get_link() for task in subtasks])

        return _('transition_add_subtask',
                 u'Subtask ${task} added by ${user}',
                 mapping={'user': self.response.creator_link(),
                          'task': label})

    def label(self):
        return _('transition_label_add_subtask', u'Subtask added to task')


ResponseDescription.add_description(SubTaskAdded)


class DocumentAdded(ResponseDescription):

    transition = 'transition-add-document'
    css_class = 'addDocument'

    def msg(self):
        docs, subtasks = self.response.get_added_objects()
        label = u' '.join([to_safe_html(doc.title) for doc in docs])

        return _('transition_add_document',
                 u'Document ${doc} added by ${user}',
                 mapping={'user': self.response.creator_link(),
                          'doc': label})

    def label(self):
        return _('transition_label_add_document',
                 u'Document added to Task')


ResponseDescription.add_description(DocumentAdded)


class TaskCommented(ResponseDescription):

    transition = 'task-commented'
    css_class = 'taskCommented'

    def msg(self):
        return _('msg_task_commented', u'Commented by ${user}',
                 mapping=self._msg_mapping)

    def label(self):
        return _('label_task_commented', u'Task commented')


ResponseDescription.add_description(TaskCommented)


class TaskAdded(ResponseDescription):

    transition = 'task-added'
    css_class = 'created'


ResponseDescription.add_description(TaskAdded)


class ForwardingAdded(ResponseDescription):

    transition = 'forwarding-added'
    css_class = 'created'


ResponseDescription.add_description(ForwardingAdded)


class NullResponseDescription(ResponseDescription):
    """Fallback description for responses without any transition information.
    """

    transition = None
    css_class = 'null-transition'

    def msg(self):
        return ''

    def label(self):
        return ''
