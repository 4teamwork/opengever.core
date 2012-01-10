"""This module contains the general components of the accept task wizard. It
especially contains the view initializing the accept task process and
deciding whether to use the wizard and it also contains the first wizard
step, where the user has to choose the method of participation.
"""

from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from five import grok
from opengever.ogds.base.interfaces import IContactInformation
from opengever.ogds.base.utils import get_client_id
from opengever.task import _
from opengever.task.browser.accept.storage import IAcceptTaskStorageManager
from opengever.task.browser.accept.utils import accept_task_with_response
from opengever.task.interfaces import ISuccessorTaskController
from opengever.task.task import ITask
from plone.directives.form import Schema
from plone.z3cform.layout import FormWrapper
from z3c.form.browser.radio import RadioFieldWidget
from z3c.form.button import buttonAndHandler
from z3c.form.field import Fields
from z3c.form.form import Form
from z3c.form.interfaces import INPUT_MODE
from z3c.form.validator import SimpleFieldValidator
from z3c.form.validator import WidgetValidatorDiscriminators
from zope import schema
from zope.component import getUtility
from zope.interface import Invalid
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm


class AcceptTask(grok.View):
    grok.context(ITask)
    grok.name('accept_task')
    grok.require('cmf.AddPortalContent')

    def render(self):
        """Decides how the task is resolved.

        Callees:
        1) Actions -> Accept on the task
        2) Add -> Response on the task, then select "accept" transition, but
        only if is_successing_possible() returns `True`

        Rules / use cases:
        - If we have a single client setup, 1) will accept the task directly
        and 2) accepts it directly too, but giving the user a chance to set
        a response text.
        Accepting directly over 1) is in this case cohorent with the other
        transitions used directly in the actions menu.

        - If we have a multi client setup and the responsible_task is a
        foreign task, the user needs to decide how to work on the task
        (directly or with a successor task). So 1) and 2) will redirect to the
        accept wizard.

        - If we have a multi client setup but the task is client internal,
        then we don't use the wizard. But we should not directly accept the
        task with 1), because the user may expect the accept wizard, where
        he can define a response text - so we use the normal response form.
        """

        if not self.is_wizard_active():
            url = 'direct_response?form.widgets.transition=' + \
                'task-transition-open-in-progress'

        elif self.is_successing_possible():
            url = '@@accept_choose_method'

        else:
            url = 'addresponse?form.widgets.transition=' + \
                'task-transition-open-in-progress'

        return self.request.RESPONSE.redirect(
            '/'.join((self.context.absolute_url(), url)))

    def is_wizard_active(self):
        """The wizard is only active in multi client setup.
        """
        info = getUtility(IContactInformation)
        return len(info.get_clients()) > 1

    def is_successing_possible(self):
        """Creating successor tasks is only allowed if the responsible_client
        of the task is another client than the current one, and the wizard
        is active.
        """
        if not self.is_wizard_active():
            return False

        elif self.context.responsible_client == get_client_id():
            return False

        else:
            return True


class AcceptWizardFormMixin(object):
    """This form wizard mixin class is used by wizard step forms and makes
    the wizard aware. It provides information about the steps for displaying
    the progress bar and also provides a mechanism for passing data along the
    steps.
    """

    steps = (

        ('accept_choose_method',
         _(u'step_1', default=u'Step 1')),

        ('...', u'...'),
        )

    label = _(u'title_accept_task', u'Accept task')
    template = ViewPageTemplateFile(
        '../templates/wizard_wrappedform.pt')
    ignoreContext = True

    passed_data = ['oguid']

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


@grok.provider(IContextSourceBinder)
def method_vocabulary_factory(context):
    info = getUtility(IContactInformation)
    client = info.get_client_by_id(context.responsible_client)

    return SimpleVocabulary([
            SimpleTerm(
                value=u'participate',
                title=_(u'accept_method_participate',
                        default=u"process in issuer's dossier")),

            SimpleTerm(
                value=u'existing_dossier',
                title=_(u'accept_method_existing_dossier',
                        default=u'file in existing dossier in ${client}',
                        mapping={'client': client.title})),

            SimpleTerm(
                value=u'new_dossier',
                title=_(u'accept_method_new_dossier',
                        default=u'file in new dossier in ${client}',
                        mapping={'client': client.title}))])


class IChooseMethodSchema(Schema):

    method = schema.Choice(
        title=_('label_accept_choose_method',
                default=u'Accept the task and ...'),
        source=method_vocabulary_factory,
        required=True)

    text = schema.Text(
        title=_(u'label_response', default=u'Response'),
        description=_(u'help_accept_task_response',
                      default=u'Enter a answer text which will be shown '
                      u'as response when the task is accepted.'),
        required=False)


class MethodValidator(SimpleFieldValidator):

    def validate(self, value):
        super(MethodValidator, self).validate(value)

        # The user should not be able to create a dossier or use on existing
        # dossier on a remote client if he does not participate in this
        # client.
        if value != u'participate':
            mtool = getToolByName(self.context, 'portal_membership')
            userid = mtool.getAuthenticatedMember().getId()

            info = getUtility(IContactInformation)
            client = info.get_client_by_id(self.context.responsible_client)
            user = info.get_user(userid)

            if user not in client.users_group.users:
                msg = _(u'You are not assigned to the responsible client '
                        u'(${client}). You can only process the task in the '
                        u'issuers dossier.',
                        mapping={'client': client.title})
                raise Invalid(msg)

WidgetValidatorDiscriminators(MethodValidator,
                              field=IChooseMethodSchema['method'])
grok.global_adapter(MethodValidator)


class ChooseMethodStepForm(AcceptWizardFormMixin, Form):
    fields = Fields(IChooseMethodSchema)
    fields['method'].widgetFactory[INPUT_MODE] = RadioFieldWidget

    step_name = 'accept_choose_method'

    @buttonAndHandler(_(u'button_continue', default=u'Continue'),
                      name='save')
    def handle_continue(self, action):
        data, errors = self.extractData()

        if not errors:
            dm = getUtility(IAcceptTaskStorageManager)
            dm.update(data, task=self.context)

            method = data.get('method')
            if method == 'participate':
                accept_task_with_response(self.context, data['text'])
                IStatusMessage(self.request).addStatusMessage(
                    _(u'The task has been accepted.'), 'info')
                return self.request.response.redirect(
                    self.context.absolute_url())

            elif method == 'existing_dossier':
                info = getUtility(IContactInformation)
                client = info.get_client_by_id(
                    self.context.responsible_client)
                oguid = ISuccessorTaskController(self.context).get_oguid()

                # push session data to target client
                dm.push_to_remote_client(client.client_id, oguid)

                # XXX: should "ordnungssystem" really be hardcode?
                url = '%s/ordnungssystem/@@accept_choose_dossier?oguid=%s' % (
                    client.public_url,
                    oguid)
                return self.request.RESPONSE.redirect(url)

            elif method == 'new_dossier':
                info = getUtility(IContactInformation)
                client = info.get_client_by_id(
                    self.context.responsible_client)
                oguid = ISuccessorTaskController(self.context).get_oguid()

                # push session data to target client
                dm.push_to_remote_client(client.client_id, oguid)

                # XXX: should "ordnungssystem" really be hardcode?
                url = '/'.join((
                        client.public_url,
                        'ordnungssystem',
                        '@@accept_select_repositoryfolder?oguid=%s' % oguid))
                return self.request.RESPONSE.redirect(url)

    @buttonAndHandler(_(u'button_cancel', default=u'Cancel'))
    def handle_cancel(self, action):
        return self.request.RESPONSE.redirect('.')

    def updateWidgets(self):
        if self.request.form.get('form.widgets.text', None) is None:
            if self.request.get('oguid', None) is None:
                oguid = ISuccessorTaskController(self.context).get_oguid()
                self.request.set('oguid', oguid)

            dm = getUtility(IAcceptTaskStorageManager)
            text = dm.get('text', oguid=self.request.get('oguid'))

            if text:
                self.request.set('form.widgets.text', text)

        super(ChooseMethodStepForm, self).updateWidgets()


class ChooseMethodStepView(FormWrapper, grok.View):
    grok.context(ITask)
    grok.name('accept_choose_method')
    grok.require('cmf.AddPortalContent')

    form = ChooseMethodStepForm

    def __init__(self, *args, **kwargs):
        FormWrapper.__init__(self, *args, **kwargs)
        grok.View.__init__(self, *args, **kwargs)
