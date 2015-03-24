from opengever.ogds.base.actor import Actor
from opengever.task import _
from opengever.task.activities import TaskAddedActivity
from plone import api
from Products.CMFPlone import PloneMessageFactory


class ForwardingAddedActivity(TaskAddedActivity):
    """Activity representation for adding a task."""

    @property
    def kind(self):
        return PloneMessageFactory(u'forwarding-added',
                                   default=u'Forwarding added')

    @property
    def summary(self):
        actor = Actor.lookup(self.context.Creator())
        msg = _('label_forwarding_added', u'New forwarding added by ${user}',
                mapping={'user': actor.get_label(with_principal=False)})
        return self.translate(msg)

    def collects_description_data(self):
        """Returns a list with [label, value] pairs.
        """
        return [
            [self.translate(_('label_task_title', u'Task title')),
             self.title],
            [self.translate(_('label_deadline', u'Deadline')),
             api.portal.get_localized_time(str(self.context.deadline))],
            [self.translate(_('label_text', u'Text')),
             self.context.text]
        ]
