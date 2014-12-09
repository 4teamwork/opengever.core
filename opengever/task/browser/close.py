"""A wizard, activated when a uniref task is closed. The user can copy
related documents to his own client with this wizard.

"""
from five import grok
from opengever.base.browser.wizard import BaseWizardStepForm
from opengever.base.browser.wizard.interfaces import IWizardDataStorage
from opengever.base.interfaces import IReferenceNumber
from opengever.base.oguid import Oguid
from opengever.base.source import RepositoryPathSourceBinder
from opengever.dossier.base import DOSSIER_STATES_OPEN
from opengever.globalindex.model.task import Task
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.ogds.base.utils import ogds_service
from opengever.task import _
from opengever.task.interfaces import ISuccessorTaskController
from opengever.task.interfaces import ITaskDocumentsTransporter
from opengever.task.task import ITask
from opengever.task.util import change_task_workflow_state
from opengever.task.util import CustomInitialVersionMessage
from opengever.task.util import get_documents_of_task
from plone.directives.form import Schema
from plone.z3cform.layout import FormWrapper
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from Products.statusmessages.interfaces import IStatusMessage
from z3c.form.browser.checkbox import CheckBoxFieldWidget
from z3c.form.button import buttonAndHandler
from z3c.form.field import Fields
from z3c.form.form import Form
from z3c.form.validator import SimpleFieldValidator
from z3c.form.validator import WidgetValidatorDiscriminators
from z3c.relationfield.schema import RelationChoice
from zExceptions import NotFound
from zope import schema
from zope.app.intid.interfaces import IIntIds
from zope.component import getUtility
from zope.interface import Interface
from zope.interface import Invalid
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary
import urllib


class CloseTaskWizardStepFormMixin(BaseWizardStepForm):

    steps = (
        ('close-task-wizard_select-documents',
         _(u'step_1', default=u'Step 1')),

        ('close-task-wizard_choose-dossier',
         _(u'step_2', default=u'Step 2')))

    label = _(u'title_close_task', u'Close task')

    passed_data = ['oguid']


@grok.provider(IContextSourceBinder)
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
                url = '/'.join((
                    self.context.absolute_url(),
                    '@@close-task-wizard_close?oguid=%s' % oguid))
                return self.request.RESPONSE.redirect(url)

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


class SelectDocumentsStepView(FormWrapper, grok.View):
    grok.context(ITask)
    grok.name('close-task-wizard_select-documents')
    grok.require('cmf.AddPortalContent')

    form = SelectDocumentsStepForm

    def __init__(self, *args, **kwargs):
        FormWrapper.__init__(self, *args, **kwargs)
        grok.View.__init__(self, *args, **kwargs)


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
                'review_state': ['repositoryroot-state-active',
                                 'repositoryfolder-state-active'] +
                                 DOSSIER_STATES_OPEN,
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
grok.global_adapter(DossierValidator)


class ChooseDossierStepForm(CloseTaskWizardStepFormMixin, Form):
    fields = Fields(IChooseDossierSchema)
    step_name = 'close-task-wizard_choose-dossier'

    @buttonAndHandler(_(u'button_save', default=u'Save'),
                      name='save')
    def handle_save(self, action):
        data, errors = self.extractData()

        if not errors:
            dm = getUtility(IWizardDataStorage)

            oguid = self.request.get('oguid')
            dmkey = 'close:%s' % oguid

            task = Task.query.by_oguid(oguid)
            source_admin_unit = ogds_service().fetch_admin_unit(
                task.admin_unit_id)

            self.copy_documents(task, data['dossier'],
                                dm.get(dmkey, 'documents'))

            redirect_data = {
                'oguid': oguid,
                'redirect_url': '%s#documents' % (
                    data['dossier'].absolute_url())}

            url = '/'.join((
                source_admin_unit.public_url,
                '@@close-task-wizard_close?%s' % urllib.urlencode(
                    redirect_data)))
            return self.request.RESPONSE.redirect(url)

    @buttonAndHandler(_(u'button_cancel', default=u'Cancel'),
                      name='cancel')
    def handle_cancel(self, action):
        portal_url = getToolByName(self.context, 'portal_url')
        url = '%s/resolve_oguid?oguid=%s' % (
            portal_url(), self.request.get('oguid'))
        return self.request.RESPONSE.redirect(url)

    def copy_documents(self, task, dossier, documents):
        doc_transporter = getUtility(ITaskDocumentsTransporter)

        with CustomInitialVersionMessage(
            _(u'version_message_closed_task',
              default=u'Document copied from task (task closed)'),
            dossier.REQUEST):
            intids_mapping = doc_transporter.copy_documents_from_remote_task(
                task, dossier, documents=documents)

        IStatusMessage(self.request).addStatusMessage(
            _(u'${num} documents were copied.',
              mapping={'num': len(intids_mapping)}), 'info')


class ChooseDossierStepView(FormWrapper, grok.View):
    grok.context(Interface)
    grok.name('close-task-wizard_choose-dossier')
    grok.require('zope2.View')

    form = ChooseDossierStepForm

    def __init__(self, *args, **kwargs):
        FormWrapper.__init__(self, *args, **kwargs)
        grok.View.__init__(self, *args, **kwargs)


class ChooseDosserStepRedirecter(grok.View):
    """Remote clients redirect usually to the site root, but this step needs
    to be called on the repository root.

    The remote client does not know the URL to the repository root, so it
    redirects to the site root. This view just redirects to the repository
    root, passing the parameters on.
    """

    grok.context(IPloneSiteRoot)
    grok.name('close-task-wizard_choose-dossier')
    grok.require('zope2.View')

    def render(self):
        root = self.context.restrictedTraverse(
            '@@primary_repository_root').get_primary_repository_root()

        url = '%s/@@close-task-wizard_choose-dossier?%s' % (
            root.absolute_url(),
            self.request.get('QUERY_STRING'))

        return self.request.RESPONSE.redirect(url)


class CloseTaskView(grok.View):
    """This view closes the task. It is either called directly, if no
    documents are selected to be copied or after choosing the target dossier
    and copying the documents.
    It is not context sensitive.
    """

    grok.context(Interface)
    grok.name('close-task-wizard_close')
    grok.require('zope2.View')

    def render(self):
        task = self.get_task()
        text = self.get_text()

        transition = 'task-transition-open-tested-and-closed'
        change_task_workflow_state(task, transition, text=text)

        redirect_url = self.request.get('redirect_url', None)
        if redirect_url is None:
            redirect_url = task.absolute_url()

        return self.request.RESPONSE.redirect(redirect_url)

    def get_task(self):
        intids = getUtility(IIntIds)
        membership = getToolByName(self.context, 'portal_membership')
        oguid = Oguid.parse(self.request.get('oguid'))

        if get_current_admin_unit().id() != oguid.admin_unit_id:
            raise NotFound

        task = intids.getObject(oguid.int_id)
        if not membership.checkPermission('Add portal content', task):
            raise NotFound

        return task

    def get_text(self):
        dm = getUtility(IWizardDataStorage)

        oguid = self.request.get('oguid')
        dmkey = 'close:%s' % oguid
        return dm.get(dmkey, 'text')
