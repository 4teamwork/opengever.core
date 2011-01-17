from opengever.task.task import ITask, Task
from plone.directives import form
from zope.interface import implements


class IForwarding(ITask):
    """Schema interface for forwardings.
    """

    # common fieldset
    form.omitted('task_type')
    form.omitted('relatedItems')

    # additional fieldset
    form.omitted('expectedStartOfWork')
    form.omitted('expectedDuration')
    form.omitted('expectedCost')
    form.omitted('effectiveDuration')
    form.omitted('effectiveCost')
    form.omitted('date_of_completion')


class Forwarding(Task):
    implements(IForwarding)

    @property
    def task_type_category(self):
        return None
