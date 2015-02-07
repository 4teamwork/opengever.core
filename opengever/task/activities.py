from opengever.ogds.base.actor import Actor
from opengever.task import _
from zope.i18n import translate


class TaskAddedDescription(object):

    def __init__(self, context, request, parent):
        self.context = context
        self.request = request
        self.parent = parent

    @property
    def kind(self):
        return _(u'task-added', default=u'Task added')

    @property
    def title(self):
        return self.context.title

    @property
    def summary(self):
        actor = Actor.lookup(self.context.Creator())
        msg = _('label_task_added', 'New task added by ${user}',
                mapping={'user': actor.get_label(with_principal=False)})
        return self.translate(msg)

    @property
    def description(self):
        msg = u'<table>'\
              '<tbody>'\
              '<tr><th>{label_task_title}</th><td>{value_task_title}</td></tr>'\
              '<tr><th>{label_deadline}</th><td>{value_deadline}</td></tr>'\
              '<tr><th>{label_task_type}</th><td>{value_task_type}</td></tr>'\
              '<tr><th>{label_dossier_title}</th><td>{value_dossier_title}</td></tr>'\
              '<tr><th>{label_text}</th><td>{value_text}</td></tr>'\
              '</tbody></table>'.format(
                  label_task_title=self.translate(_('label_task_title', u'Task title')),
                  value_task_title=self.title,
                  label_deadline=self.translate(_('label_deadline', u'Deadline')),
                  value_deadline=self.context.deadline,
                  label_task_type=self.translate(_('label_task_type', u'Task type')),
                  value_task_type=self.context.get_task_type_label(),
                  label_dossier_title=self.translate(_('label_dossier_title',
                                                       u'Dossier title')),
                  value_dossier_title=self.parent.title,
                  label_text=self.translate(_('label_text', u'Text')),
                  value_text=self.context.text)

        return msg

    def translate(self, msg):
        return translate(msg, context=self.request)
