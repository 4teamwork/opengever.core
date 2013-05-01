from five import grok
from opengever.base.browser.wizard import BaseWizardStepForm
from opengever.task import _
from opengever.task.task import ITask


class DelegateTask(grok.View):
    grok.context(ITask)
    grok.name('delegate_task')
    grok.require('opengever.task.AddTask')

    def render(self):
        url = '%s/@@delegate_recipients' % self.context.absolute_url()
        return self.request.RESPONSE.redirect(url)


class DelegateWizardFormMixin(BaseWizardStepForm):

    steps = (

        ('delegate_recipients',
         _(u'step_1', default=u'Step 1')),

        ('delegate_metadata',
         _(u'step_2', default=u'Step 2')),
        )

    label = _(u'title_delegate_task', u'Delegate task')
