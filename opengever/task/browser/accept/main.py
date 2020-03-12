"""This module contains the general components of the accept task wizard. It
especially contains the view initializing the accept task process and
deciding whether to use the wizard and it also contains the first wizard
step, where the user has to choose the method of participation.
"""

from opengever.base.browser.wizard import BaseWizardStepForm
from opengever.base.browser.wizard.interfaces import IWizardDataStorage
from opengever.globalindex.handlers.task import sync_task
from opengever.ogds.models.service import ogds_service
from opengever.task import _
from opengever.task.browser.accept.utils import accept_task_with_response
from opengever.task.interfaces import ISuccessorTaskController
from plone.supermodel.model import Schema
from plone.z3cform.layout import FormWrapper
from Products.statusmessages.interfaces import IStatusMessage
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
from zope.interface import provider
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm


class AcceptWizardFormMixin(BaseWizardStepForm):

    steps = (

        ('accept_choose_method',
         _(u'step_1', default=u'Step 1')),

        ('...', u'...'),
        )

    label = _(u'title_accept_task', u'Accept task')

    passed_data = ['oguid']


@provider(IContextSourceBinder)
def method_vocabulary_factory(context):
    org_unit = context.get_responsible_org_unit()

    # decision it's a forwarding or a task
    if context.task_type == 'forwarding_task_type':
        return SimpleVocabulary([
                SimpleTerm(
                    value=u'forwarding_participate',
                    title=_(u'accept_method_forwarding_participate',
                            default=u"... store in ${client}'s inbox",
                            mapping={'client': org_unit.label()})),

                SimpleTerm(
                    value=u'existing_dossier',
                    title=_(u'accept_method_forwarding_existing_dossier',
                            default=u"... store in  ${client}'s inbox and process in an existing dossier on ${client}",
                            mapping={'client': org_unit.label()})),

                SimpleTerm(
                    value=u'new_dossier',
                    title=_(u'accept_method_forwarding_new_dossier',
                            default=u"... store in  ${client}'s inbox and process in a new dossier on ${client}",
                            mapping={'client': org_unit.label()}))])

    else:
        return SimpleVocabulary([
                SimpleTerm(
                    value=u'participate',
                    title=_(u'accept_method_participate',
                            default=u"process in issuer's dossier")),

                SimpleTerm(
                    value=u'existing_dossier',
                    title=_(u'accept_method_existing_dossier',
                            default=u'file in existing dossier in ${client}',
                            mapping={'client': org_unit.label()})),

                SimpleTerm(
                    value=u'new_dossier',
                    title=_(u'accept_method_new_dossier',
                            default=u'file in new dossier in ${client}',
                            mapping={'client': org_unit.label()}))])


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
    """The user should not be able to create a dossier or use on existing
    dossier on a remote orgunit if he does not participate in this unit.
    """

    def validate(self, value):
        super(MethodValidator, self).validate(value)

        if value != u'participate':
            org_unit = self.context.get_responsible_org_unit()

            if org_unit not in ogds_service().assigned_org_units():
                msg = _(u'You are not assigned to the responsible client '
                        u'(${client}). You can only process the task in the '
                        u'issuers dossier.',
                        mapping={'client': org_unit.id()})
                raise Invalid(msg)


WidgetValidatorDiscriminators(MethodValidator,
                              field=IChooseMethodSchema['method'])


class ChooseMethodStepForm(AcceptWizardFormMixin, Form):
    fields = Fields(IChooseMethodSchema)
    fields['method'].widgetFactory[INPUT_MODE] = RadioFieldWidget

    step_name = 'accept_choose_method'

    @property
    def label(self):
        if self.context.task_type == 'forwarding_task_type':
            _(u'title_accept_forwarding', u'Accept forwarding')

        return _(u'title_accept_task', u'Accept task')

    @buttonAndHandler(_(u'button_continue', default=u'Continue'),
                      name='save')
    def handle_continue(self, action):
        data, errors = self.extractData()

        if not errors:
            oguid = ISuccessorTaskController(self.context).get_oguid()

            # set forwarding flag
            if self.context.task_type == 'forwarding_task_type':
                is_forwarding = True
            else:
                is_forwarding = False

            dm = getUtility(IWizardDataStorage)
            dmkey = 'accept:%s' % oguid
            dm.set(dmkey, u'is_forwarding', is_forwarding)
            dm.set(dmkey, u'is_only_assign', False)
            dm.update(dmkey, data)

            method = data.get('method')

            if method == 'participate':
                accept_task_with_response(self.context, data['text'])
                sync_task(self.context, None)

                IStatusMessage(self.request).addStatusMessage(
                    _(u'The task has been accepted.'), 'info')
                return self.request.response.redirect(
                    self.context.absolute_url())

            elif method == 'forwarding_participate':
                """only store the forwarding in the inbox and
                create a successor forwrding"""

                admin_unit = self.context.get_responsible_admin_unit()

                # push session data to target unit
                dm.push_to_remote_client(dmkey, admin_unit.id())
                url = '%s/@@accept_store_in_inbox?oguid=%s' % (
                    admin_unit.public_url, oguid)

                return self.request.RESPONSE.redirect(url)

            elif method == 'existing_dossier':
                admin_unit = self.context.get_responsible_admin_unit()

                # push session data to target unit
                dm.push_to_remote_client(dmkey, admin_unit.id())

                url = '%s/@@accept_choose_dossier?oguid=%s' % (
                    admin_unit.public_url, oguid)
                return self.request.RESPONSE.redirect(url)

            elif method == 'new_dossier':
                admin_unit = self.context.get_responsible_admin_unit()
                oguid = ISuccessorTaskController(self.context).get_oguid()

                # push session data to target client
                dm.push_to_remote_client(dmkey, admin_unit.id())

                url = '/'.join((
                        admin_unit.public_url,
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

            dm = getUtility(IWizardDataStorage)
            dmkey = 'accept:%s' % self.request.get('oguid')
            text = dm.get(dmkey, 'text')

            if text:
                self.request.set('form.widgets.text', text)

        super(ChooseMethodStepForm, self).updateWidgets()
        if self.context.task_type == 'forwarding_task_type':
            self.widgets.get('method').label = _(
                u'label_accept_forwarding_choose_method',
                default="Accept forwarding and ...")


class ChooseMethodStepView(FormWrapper):

    form = ChooseMethodStepForm
