"""This module contains the general components of the assign forwarding
to a dossier wizard. It especially contains the view initializing
the assign orwarding to a dossier process"""

from five import grok
from opengever.base.browser.wizard import BaseWizardStepForm
from opengever.base.browser.wizard.interfaces import IWizardDataStorage
from opengever.task import _
from opengever.task.interfaces import ISuccessorTaskController
from opengever.task.task import ITask
from plone.directives.form import Schema
from plone.z3cform.layout import FormWrapper
from z3c.form.browser.radio import RadioFieldWidget
from z3c.form.button import buttonAndHandler
from z3c.form.field import Fields
from z3c.form.form import Form
from z3c.form.interfaces import INPUT_MODE
from zope import schema
from zope.component import getUtility
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm


class AssignToDossierWizardFormMixin(BaseWizardStepForm):

    steps = (

        ('assign_choose_method',
         _(u'step_1', default=u'Step 1')),

        ('...', u'...'),
        )

    label = _(u'title_assign_to_dossier', u'Assign to Dossier')

    passed_data = ['oguid']


@grok.provider(IContextSourceBinder)
def method_vocabulary_factory(context):

    return SimpleVocabulary([
            SimpleTerm(value=u'existing_dossier',
                title=_(u'existing_dossier', default=u'existing dossier',)),

            SimpleTerm(value=u'new_dossier',
                title=_(u'new_dossier', default=u'new dossier',)),
            ])


class IAssignToDossierMethodSchema(Schema):

    method = schema.Choice(
        title=_('label_assign_choose_method',
                default=u'Assign to a ...'),
        source=method_vocabulary_factory,
        required=True)

    text = schema.Text(
        title=_(u'label_response', default=u'Response'),
        description=_(u'help_assign_to_dossier_task_response',
                      default=u'Enter a answer text which will be shown '
                      u'as response on the succesor task.'),
        required=False)


class ChooseMethodStepForm(AssignToDossierWizardFormMixin, Form):
    fields = Fields(IAssignToDossierMethodSchema)
    fields['method'].widgetFactory[INPUT_MODE] = RadioFieldWidget

    step_name = 'assign_choose_method'

    @buttonAndHandler(_(u'button_continue', default=u'Continue'),
                      name='save')
    def handle_continue(self, action):
        data, errors = self.extractData()

        if not errors:

            oguid = ISuccessorTaskController(self.context).get_oguid()

            # set forwarding flag
            is_forwarding = True

            dm = getUtility(IWizardDataStorage)
            dmkey = 'accept:%s' % oguid
            dm.set(dmkey, u'is_forwarding', is_forwarding)
            # activate the assign to dossier mode
            dm.set(dmkey, u'is_only_assign', True)
            dm.update(dmkey, data)

            method = data.get('method')

            if method == 'existing_dossier':
                url = '{}/@@accept_choose_dossier?oguid={}'.format(
                    self.context.get_responsible_org_unit().public_url(),
                    oguid)
                return self.request.RESPONSE.redirect(url)

            elif method == 'new_dossier':
                oguid = ISuccessorTaskController(self.context).get_oguid()
                url = '{}/@@accept_select_repositoryfolder?oguid={}'.format(
                    self.context.get_responsible_org_unit().public_url(),
                    oguid)
                return self.request.RESPONSE.redirect(url)

    @buttonAndHandler(_(u'button_cancel', default=u'Cancel'))
    def handle_cancel(self, action):
        return self.request.RESPONSE.redirect('.')

    def updateWidgets(self):
        if self.request.form.get('form.widgets.text', None) is None:
            if self.request.get('oguid', None) is None:
                oguid = ISuccessorTaskController(self.context).get_oguid()
                self.request.set('oguid', oguid)

            dm = getUtility(IWizardDataStorage)
            dmkey = 'accept:%s' % self.request.get('oguid')
            text = dm.get(dmkey, 'text')

            if text:
                self.request.set('form.widgets.text', text)

        super(ChooseMethodStepForm, self).updateWidgets()


class ChooseMethodStepView(FormWrapper, grok.View):
    grok.context(ITask)
    grok.name('assign_choose_method')
    grok.require('cmf.AddPortalContent')

    form = ChooseMethodStepForm

    def __init__(self, *args, **kwargs):
        FormWrapper.__init__(self, *args, **kwargs)
        grok.View.__init__(self, *args, **kwargs)
