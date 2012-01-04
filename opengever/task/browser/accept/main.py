"""This module contains the general components of the accept task wizard. It
especially contains the view initializing the accept task process and
deciding whether to use the wizard and it also contains the first wizard
step, where the user has to choose the method of participation.
"""

from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from five import grok
from opengever.ogds.base.utils import get_client_id
from opengever.task import _
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
from zope.intid.interfaces import IIntIds
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm


class AcceptTask(grok.View):
    grok.context(ITask)
    grok.name('accept_task')
    grok.require('cmf.AddPortalContent')

    def render(self):
        url = '@@accept_choose_method'
        return self.request.RESPONSE.redirect(url)


class AcceptWizardFormMixin(object):
    """This form wizard mixin class is used by wizard step forms and makes
    the wizard aware. It provides information about the steps for displaying
    the progress bar and also provides a mechanism for passing data along the
    steps.
    """

    steps = (

        ('accept_choose_method',
         _(u'accept_step_1', default=u'Step 1')),

        ('...', u'...'),
        )

    label = _(u'title_accept_task', u'Accept task')
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
            yield {'key': key,
                   'value': self.request.get(key, '')}


method_vocabulary = SimpleVocabulary([
                SimpleTerm(value=u'participate',
                           title=_(u'accept_method_participate',
                                   default=u"process in issuer's dossier")),

                SimpleTerm(value=u'existing_dossier',
                           title=_(u'accept_method_existing_dossier',
                                   default=u'file in existing dossier')),

                SimpleTerm(value=u'new_dossier',
                           title=_(u'accept_method_new_dossier',
                                   default=u'file in new dossier'))])


class IChooseMethodSchema(Schema):

    method = schema.Choice(
        title=_('label_accept_choose_method',
                default=u'Accept the task and ...'),
        vocabulary=method_vocabulary,
        required=True)


class ChooseMethodStepForm(AcceptWizardFormMixin, Form):
    fields = Fields(IChooseMethodSchema)
    fields['method'].widgetFactory[INPUT_MODE] = RadioFieldWidget

    step_name = 'accept_choose_method'

    @buttonAndHandler(_(u'button_continue', default=u'Continue'),
                      name='save')
    def handle_continue(self, action):
        data, errors = self.extractData()

        if not errors:
            method = data.get('method')
            if method == 'participate':
                url = '%s/@@accept_participate' % self.context.absolute_url()
                return self.request.RESPONSE.redirect(url)

            elif method == 'existing_dossier':
                # XXX multi client redirect
                # XXX use successor task adapter for getting oguid
                intids = getUtility(IIntIds)
                iid = intids.getId(self.context)
                oguid = '%s:%s' % (get_client_id(), str(iid))

                portal_url = getToolByName(self.context, 'portal_url')
                # XXX: should "ordnungssystem" really be hardcode?
                url = '@@accept_choose_dossier?oguid=%s' % oguid
                return self.request.RESPONSE.redirect('/'.join((
                            portal_url(), 'ordnungssystem', url)))

            elif method == 'new_dossier':
                # XXX: redirect to target client
                # XXX use successor task adapter for getting oguid
                intids = getUtility(IIntIds)
                iid = intids.getId(self.context)
                oguid = '%s:%s' % (get_client_id(), str(iid))

                portal_url = getToolByName(self.context, 'portal_url')
                # XXX: should "ordnungssystem" really be hardcode?
                url = '@@accept_select_repositoryfolder?oguid=%s' % oguid
                return self.request.RESPONSE.redirect('/'.join((
                            portal_url(), 'ordnungssystem', url)))

    @buttonAndHandler(_(u'button_cancel', default=u'Cancel'))
    def handle_cancel(self, action):
        return self.request.RESPONSE.redirect('.')


class ChooseMethodStepView(FormWrapper, grok.View):
    grok.context(ITask)
    grok.name('accept_choose_method')
    grok.require('cmf.AddPortalContent')

    form = ChooseMethodStepForm

    def __init__(self, *args, **kwargs):
        FormWrapper.__init__(self, *args, **kwargs)
        grok.View.__init__(self, *args, **kwargs)
