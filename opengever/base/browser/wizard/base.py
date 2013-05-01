from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class BaseWizardStepForm(object):
    """Mixin class for creating wizard step forms.

    Example usage:

    >>> from five import grok
    >>> from opengever.base.browser.wizard import BaseWizardStepForm
    >>> from plone.z3cform.layout import FormWrapper
    >>> from z3c.form.field import Fields
    >>> from z3c.form.form import Form
    >>> from zope.interface import Interface

    >>> class FirstWizardStep(BaseWizardStepForm, Form):
    ...     step_name = 'first-step'  # must match steps config
    ...     label = _(u'Fancy wizard')  # form title (h1)
    ...
    ...     # list of steps for displaying progress bar
    ...     steps = (
    ...         ('first-step', _(u'first-step')),
    ...         ('second-step', _(u'second-step')))
    ...
    ...     passed_data = ['key']  # list of request-keys which are passed on
    ...     fields = Fields(IFirstStepSchema)  # your zope schema

    >>> class FirstWizardStepView(FormWrapper, grok.View):
    ...     grok.context(Interface)
    ...     grok.name('first-step')
    ...     grok.require('zope2.View')
    ...
    ...     form = FirstWizardStep
    ...
    ...     def __init__(self, *args, **kwargs):
    ...          FormWrapper.__init__(self, *args, **kwargs)
    ...          grok.View.__init__(self, *args, **kwargs)
    """

    ignoreContext = True

    steps = (('no-step', 'No step configured'),)

    template = ViewPageTemplateFile('wizard_wrappedform.pt')

    label = 'wizard'
    step_title = None

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
