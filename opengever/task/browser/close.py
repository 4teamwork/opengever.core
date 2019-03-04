"""A wizard, activated when a uniref task is closed. The user can copy
related documents to his own client with this wizard.

"""
from opengever.base.browser.wizard import BaseWizardStepForm
from opengever.base.browser.wizard.interfaces import IWizardDataStorage
from opengever.base.interfaces import IReferenceNumber
from opengever.base.request import dispatch_request
from opengever.base.request import tracebackify
from opengever.base.source import RepositoryPathSourceBinder
from opengever.base.utils import ok_response
from opengever.dossier.base import DOSSIER_STATES_OPEN
from opengever.globalindex.model.task import Task
from opengever.task import _
from opengever.task.adapters import IResponseContainer
from opengever.task.interfaces import ISuccessorTaskController
from opengever.task.interfaces import ITaskDocumentsTransporter
from opengever.task.util import change_task_workflow_state
from opengever.task.util import get_documents_of_task
from plone import api
from plone.supermodel.model import Schema
from plone.z3cform.layout import FormWrapper
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from z3c.form.browser.checkbox import CheckBoxFieldWidget
from z3c.form.button import buttonAndHandler
from z3c.form.field import Fields
from z3c.form.form import Form
from z3c.form.validator import SimpleFieldValidator
from z3c.form.validator import WidgetValidatorDiscriminators
from z3c.relationfield.schema import RelationChoice
from zope import schema
from zope.app.intid.interfaces import IIntIds
from zope.component import getUtility
from zope.interface import Invalid
from zope.interface import provider
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary


class CloseTaskWizardStepFormMixin(BaseWizardStepForm):

    steps = (
        ('close-task-wizard_select-documents',
         _(u'step_1', default=u'Step 1')),

        ('close-task-wizard_choose-dossier',
         _(u'step_2', default=u'Step 2')))

    label = _(u'title_close_task', u'Close task')

    passed_data = ['oguid']


@provider(IContextSourceBinder)
def related_documents_vocabulary(task):
    intids = getUtility(IIntIds)

    terms = []
    for doc in get_documents_of_task(task, include_mails=True):
        key = str(intids.getId(doc))
        label = '%s (%s)' % (
            doc.Title(),
            IReferenceNumber(doc).get_number())

        terms.append(SimpleVocabulary.createTerm(key, key, label))

    return SimpleVocabulary(terms)


class ISelectDocumentsSchema(Schema):

    text = schema.Text(
        title=_(u'label_response', default=u'Response'),
        description=_(u'help_accept_task_response',
                      default=u'Enter a answer text which will be shown '
                      u'as response when the task is accepted.'),
        required=False)

    documents = schema.List(
        title=_(u'label_close_documents',
                default=u'Documents to copy'),
        description=_(u'help_close_documents',
                      default=u'You can copy attached documents to your '
                      u'client by selecting here the documents to copy.'),
        required=False,

        value_type=schema.Choice(
            source=related_documents_vocabulary,
            ))


class SelectDocumentsStepForm(CloseTaskWizardStepFormMixin, Form):
    fields = Fields(ISelectDocumentsSchema)
    fields['documents'].widgetFactory = CheckBoxFieldWidget

    step_name = 'close-task-wizard_select-documents'

    @buttonAndHandler(_(u'button_continue', default=u'Continue'),
                      name='save')
    def handle_continue(self, action):
        data, errors = self.extractData()

        if not errors:
            oguid = ISuccessorTaskController(self.context).get_oguid()

            dm = getUtility(IWizardDataStorage)
            dmkey = 'close:%s' % oguid
            dm.update(dmkey, data)

            if len(data['documents']) == 0:
                self.close_task(data.get('text'))
                return self.request.RESPONSE.redirect(
                    self.context.absolute_url())

            else:
                admin_unit = self.context.get_responsible_admin_unit()
                dm.push_to_remote_client(dmkey, admin_unit.id())

                url = '/'.join((
                    admin_unit.public_url,
                    '@@close-task-wizard_choose-dossier?oguid=%s' % (oguid)))
                return self.request.RESPONSE.redirect(url)

    @buttonAndHandler(_(u'button_cancel', default=u'Cancel'),
                      name='cancel')
    def handle_cancel(self, action):
        return self.request.RESPONSE.redirect(self.context.absolute_url())

    def close_task(self, text):
        change_task_workflow_state(
            self.context, 'task-transition-open-tested-and-closed', text=text)


class SelectDocumentsStepView(FormWrapper):

    form = SelectDocumentsStepForm


class IChooseDossierSchema(Schema):

    dossier = RelationChoice(
        title=_(u'label_close_choose_dossier',
                default=u'Target dossier'),
        description=_(u'help_close_choose_dossier',
                      default=u'Choose the target dossier where the '
                      'documents should be filed.'),
        required=True,

        source=RepositoryPathSourceBinder(
            object_provides='opengever.dossier.behaviors.dossier.'
            'IDossierMarker',
            review_state=DOSSIER_STATES_OPEN,
            navigation_tree_query={
                'object_provides': [
                    'opengever.repository.repositoryroot.IRepositoryRoot',
                    'opengever.repository.repositoryfolder.'
                    'IRepositoryFolderSchema',
                    'opengever.dossier.behaviors.dossier.IDossierMarker',
                    ],
                'review_state': [
                    'repositoryroot-state-active',
                    'repositoryfolder-state-active'] + DOSSIER_STATES_OPEN,
                }))


class DossierValidator(SimpleFieldValidator):

    def validate(self, value):
        super(DossierValidator, self).validate(value)

        document_addable = False
        for fti in value.allowedContentTypes():
            if fti.id == 'opengever.document.document':
                document_addable = True
                break

        if not document_addable:
            msg = _(u'You cannot add documents to the selected dossier. '
                    u'Either the dossier is closed or you do not have the '
                    u'privileges.')
            raise Invalid(msg)


WidgetValidatorDiscriminators(DossierValidator,
                              field=IChooseDossierSchema['dossier'])


class ChooseDossierStepForm(CloseTaskWizardStepFormMixin, Form):
    fields = Fields(IChooseDossierSchema)
    step_name = 'close-task-wizard_choose-dossier'

    @buttonAndHandler(_(u'button_save', default=u'Save'),
                      name='save')
    def handle_save(self, action):
        data, errors = self.extractData()

        if not errors:
            oguid = self.request.get('oguid')
            dm = getUtility(IWizardDataStorage)
            dmkey = 'close:%s' % oguid
            task = Task.query.by_oguid(oguid)

            self.copy_documents(
                task, data['dossier'], dm.get(dmkey, 'documents'))
            self.close_task(task, dm.get(dmkey, 'text'))

            return self.request.RESPONSE.redirect(
                '{}#documents'.format(data['dossier'].absolute_url()))

    @buttonAndHandler(_(u'button_cancel', default=u'Cancel'),
                      name='cancel')
    def handle_cancel(self, action):
        portal_url = getToolByName(self.context, 'portal_url')
        url = '%s/resolve_oguid?oguid=%s' % (
            portal_url(), self.request.get('oguid'))
        return self.request.RESPONSE.redirect(url)

    def close_task(self, task, text):
        response = dispatch_request(
            task.admin_unit_id,
            u'@@close-task-wizard-remote_close',
            path=task.physical_path,
            data={'text': text.encode('utf-8') if text else u''})

        response_data = response.read().strip()
        if response_data != 'OK':
            raise Exception(
                'Could not close task on remote site %s (%s)' % (
                    task.admin_unit_id,
                    task.physical_path))

    def copy_documents(self, task, dossier, documents):
        doc_transporter = getUtility(ITaskDocumentsTransporter)

        comment = _(u'version_message_closed_task',
                    default=u'Document copied from task (task closed)')
        intids_mapping = doc_transporter.copy_documents_from_remote_task(
            task, dossier, documents=documents, comment=comment)

        IStatusMessage(self.request).addStatusMessage(
            _(u'${num} documents were copied.',
              mapping={'num': len(intids_mapping)}), 'info')


class ChooseDossierStepView(FormWrapper):

    form = ChooseDossierStepForm


class ChooseDosserStepRedirecter(BrowserView):
    """Remote clients redirect usually to the site root, but this step needs
    to be called on the repository root.

    The remote client does not know the URL to the repository root, so it
    redirects to the site root. This view just redirects to the repository
    root, passing the parameters on.
    """

    def __call__(self):
        root = self.context.restrictedTraverse(
            '@@primary_repository_root').get_primary_repository_root()

        url = '%s/@@close-task-wizard_choose-dossier?%s' % (
            root.absolute_url(),
            self.request.get('QUERY_STRING'))

        return self.request.RESPONSE.redirect(url)


@tracebackify
class CloseTaskView(BrowserView):
    """This view closes the task. It is either called directly, if no
    documents are selected to be copied or after choosing the target dossier
    and copying the documents.
    It is not context sensitive.
    """

    transition = 'task-transition-open-tested-and-closed'

    def __call__(self):
        text = safe_unicode(self.request.get('text'))

        if self.is_already_done():
            return ok_response(self.request)

        change_task_workflow_state(self.context, self.transition, text=text)
        return ok_response(self.request)

    def is_already_done(self):
        """This method returns `True` if this exact request was already
        executed.
        This is the case when the sender client has a conflict error when
        committing and the sender-request needs to be re-done. In this case
        this view is called another time but the changes were already made
        and committed - so we need to return "OK" and do nothing.
        """
        response_container = IResponseContainer(self.context)
        if len(response_container) == 0:
            return False

        last_response = response_container[-1]
        if last_response.transition == self.transition and \
           api.user.get_current().getId() == last_response.creator:
            return True

        return False
