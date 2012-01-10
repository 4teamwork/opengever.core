from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from five import grok
from opengever.task import _
from opengever.task.task import ITask


class DelegateTask(grok.View):
    grok.context(ITask)
    grok.name('delegate_task')
    grok.require('opengever.task.AddTask')

    def render(self):
        url = '%s/@@delegate_recipients' % self.context.absolute_url()
        return self.request.RESPONSE.redirect(url)


class DelegateWizardFormMixin(object):

    steps = (

        ('delegate_recipients',
         _(u'step_1', default=u'Step 1')),

        ('delegate_metadata',
         _(u'step_2', default=u'Step 2')),
        )

    label = _(u'title_delegate_task', u'Delegate task')
    template = ViewPageTemplateFile(
        '../templates/wizard_wrappedform.pt')
    ignoreContext = True

    passed_data = []

    def wizard_steps(self):
        current_reached = False

        for name, label in self.steps:
            classes = ['wizard-step-%s' % name]
            if name == self.step_name:
                current_reached = True
                classes.append('selected')

            elif not current_reached:
                classes.append('visited')

            yield {'name': name,
                   'label': label,
                   'class': ' '.join(classes)}

    def get_passed_data(self):
        for key in self.passed_data:
            value = self.request.get(key, '')
            if hasattr(value, '__iter__'):
                for val in value:
                    yield {'key': '%s:list' % key,
                           'value': val}

            else:
                yield {'key': key,
                       'value': value}
