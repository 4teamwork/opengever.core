from opengever.base.browser.wizard import BaseWizardStepForm
from opengever.task import _


class DelegateTask(object):

    @classmethod
    def url_for(cls, context):
        return '{}/@@delegate_recipients'.format(context.absolute_url())


class DelegateWizardFormMixin(BaseWizardStepForm):

    steps = (

        ('delegate_recipients',
         _(u'step_1', default=u'Step 1')),

        ('delegate_metadata',
         _(u'step_2', default=u'Step 2')),
        )

    label = _(u'title_delegate_task', u'Delegate task')
