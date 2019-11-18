"""Contains a view for completeing a task which has a predecesser. Completeing
the successor also completes the predecesser and the user can choose documents
related to the successor task to deliver to issuer by attaching them to the
predecessor task.
"""

from Acquisition import aq_inner
from Acquisition import aq_parent
from opengever.base.browser.wizard.interfaces import IWizardDataStorage
from opengever.base.interfaces import IReferenceNumber
from opengever.base.request import dispatch_request
from opengever.base.request import tracebackify
from opengever.base.transport import Transporter
from opengever.base.utils import ok_response
from opengever.document.versioner import Versioner
from opengever.globalindex.model.task import Task
from opengever.tabbedview.helper import linked
from opengever.task import _
from opengever.task import util
from opengever.base.response import IResponseContainer
from opengever.task.interfaces import ISuccessorTaskController
from opengever.task.validators import NoCheckedoutDocsValidator
from persistent.list import PersistentList
from plone.supermodel.model import Schema
from plone.z3cform.layout import FormWrapper
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from z3c.form import validator
from z3c.form.browser.checkbox import CheckBoxFieldWidget
from z3c.form.button import buttonAndHandler
from z3c.form.field import Fields
from z3c.form.form import Form
from z3c.form.interfaces import HIDDEN_MODE
from z3c.relationfield import RelationValue
from zExceptions import Unauthorized
from zope import schema
from zope.app.intid.interfaces import IIntIds
from zope.component import getUtility, getAdapter
from zope.event import notify
from zope.i18n import translate
from zope.interface import provider
from zope.lifecycleevent import ObjectAddedEvent
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary
import AccessControl
import json


@provider(IContextSourceBinder)
def deliverable_documents_vocabulary(context):
    """All documents and mails in the current dossier are deliverable.
    """

    finder = getAdapter(context, name='parent-dossier-finder')
    dossier = finder.find_dossier()
    if not dossier:
        raise RuntimeError('Could not find parent dossier.')

    catalog = getToolByName(dossier, 'portal_catalog')
    brains = catalog(
        portal_type=['opengever.document.document', 'ftw.mail.mail'],
        path='/'.join(dossier.getPhysicalPath()))

    # Create the vocabulary.
    terms = []
    intids = getUtility(IIntIds)
    for brain in brains:
        doc = brain.getObject()
        key = str(intids.getId(doc))
        label = '%s (%s, %s)' % (
            doc.Title(),
            IReferenceNumber(doc).get_number(),
            aq_parent(aq_inner(doc)).Title())

        terms.append(SimpleVocabulary.createTerm(key, key, label))

    return SimpleVocabulary(terms)


class ICompleteSuccessorTaskSchema(Schema):

    documents = schema.List(
        title=_(u'label_complete_documents',
                default=u'Documents to deliver'),
        description=_(u'help_complete_documents',
                      default=u'Select the documents you want to deliver to '
                      u'the issuer of the task. They will be attached to the '
                      u'original task of the issuer.'),
        required=False,

        value_type=schema.Choice(
            source=deliverable_documents_vocabulary,
            ))

    text = schema.Text(
        title=_(u'label_response', default=u'Response'),
        description=_(u'help_complete_task_response',
                      default=u'Enter a answer text which will be shown '
                      u'as response when the task is completed.'),
        required=False)

    # hidden: used to pass on the transition
    transition = schema.Choice(
        title=_("label_transition", default="Transition"),
        source=util.getTransitionVocab,
        required=True)


validator.WidgetValidatorDiscriminators(
    NoCheckedoutDocsValidator, field=ICompleteSuccessorTaskSchema['documents'])


class CompleteSuccessorTaskForm(Form):
    fields = Fields(ICompleteSuccessorTaskSchema)
    fields['documents'].widgetFactory = CheckBoxFieldWidget

    allow_prefill_from_GET_request = True  # XXX

    label = _(u'title_complete_task', u'Complete task')
    ignoreContext = True

    @buttonAndHandler(_(u'button_save', default=u'Save'),
                      name='save')
    def handle_save(self, action):
        data, errors = self.extractData()

        if not errors:
            # Syncing the workflow change is done during document delivery
            # (see deliver_documents_and_complete_task) therefore we skip
            # the workflow syncing.
            util.change_task_workflow_state(self.context,
                                            data['transition'],
                                            disable_sync=True,
                                            text=data['text'])

            response = IResponseContainer(self.context).list()[-1]
            self.deliver_documents_and_complete_task(data, response)

            msg = _(u'The documents were delivered to the issuer and the '
                    u'tasks were completed.')
            IStatusMessage(self.request).addStatusMessage(msg, 'info')

            url = self.context.absolute_url()
            return self.request.RESPONSE.redirect(url)

    @buttonAndHandler(_(u'button_cancel', default=u'Cancel'))
    def handle_cancel(self, action):
        url = self.context.absolute_url()
        return self.request.RESPONSE.redirect(url)

    def updateWidgets(self):
        if self.request.form.get('form.widgets.transition', None) is None:
            self.request.set('form.widgets.transition',
                             self.request.get('transition'))

        # Use text passed from response-add-form.
        if self.request.form.get('form.widgets.text', None) is None:
            dm = getUtility(IWizardDataStorage)
            oguid = ISuccessorTaskController(self.context).get_oguid()
            dmkey = 'delegate:%s' % oguid
            text = dm.get(dmkey, 'text')
            if text:
                self.request.set('form.widgets.text', text)

        Form.updateWidgets(self)

        self.widgets['transition'].mode = HIDDEN_MODE

    def deliver_documents_and_complete_task(self, formdata, response):
        """Delivers the selected documents to the predecesser task and
        complete the task:

        - Copy the documents to the predecessor task (no new responses)
        - Execute workflow transition (no new response)
        - Add a new response indicating the workflow transition, the added
        documents and containing the entered response text.
        """

        predecessor = Task.query.by_oguid(self.context.predecessor)

        transporter = Transporter()
        intids = getUtility(IIntIds)

        data = {'documents': [],
                'text': formdata['text'],
                'transition': formdata['transition']}

        related_ids = []
        if getattr(self.context, 'relatedItems'):
            related_ids = [item.to_id for item in self.context.relatedItems]

        for doc_intid in formdata['documents']:
            doc = intids.getObject(int(doc_intid))
            data['documents'].append(transporter.extract(doc))

            # add a releation when a document from the dossier was selected
            if int(doc_intid) not in related_ids:
                # check if its a relation
                if aq_parent(aq_inner(doc)) != self.context:
                    # add relation to doc on task
                    if self.context.relatedItems:
                        self.context.relatedItems.append(
                            RelationValue(int(doc_intid)))
                    else:
                        self.context.relatedItems = [
                            RelationValue(int(doc_intid))]

                    # add response change entry for this relation
                    response.add_related_item(RelationValue(int(doc_intid)))

                    # set relation flag
                    doc._v__is_relation = True
                    response.add_change('relatedItems',
                        '',
                        linked(doc, doc.Title()),
                        _(u'label_related_items', default=u"Related Items"))

                else:
                    # add entry to the response for this document
                    response.added_objects.append(RelationValue(int(doc_intid)))
            else:
                # append only the relation on the response
                doc._v__is_relation = True
                response.add_change('relatedItems',
                    '',
                    linked(doc, doc.Title()),
                    _(u'label_related_items', default=u"Related Items"))

        request_data = {'data': json.dumps(data)}
        response = dispatch_request(
            predecessor.admin_unit_id,
            '@@complete_successor_task-receive_delivery',
            predecessor.physical_path,
            data=request_data)

        response_body = response.read()
        if response_body.strip() != 'OK':
            raise Exception('Delivering documents and updating task failed '
                            'on remote client %s.' % predecessor.admin_unit_id)


class CompleteSuccessorTask(FormWrapper):

    form = CompleteSuccessorTaskForm


@tracebackify
class CompleteSuccessorTaskReceiveDelivery(BrowserView):
    """This view is called by the complete-sucessor-task form while
    completeing the task. It is called on the client of the predecessor and
    makes the necessary changes regarding the predecessor task:

    - Copy the documents to the predecessor task (no new responses)
    - Execute workflow transition (no new response)
    - Add a new response indicating the workflow transition, the added
    documents and containing the entered response text.
    """

    def __call__(self):
        data = self.request.get('data', None)
        assert data is not None, 'Bad request: no delivery data found'
        data = json.loads(data)

        if self.is_already_delivered(data):
            return ok_response()

        mtool = getToolByName(self.context, 'portal_membership')
        member = mtool.getAuthenticatedMember()

        if not member.checkPermission('Add portal content', self.context):
            raise Unauthorized()

        # Set the "X-CREATING-SUCCESSOR" flag for preventing the event
        # handler from creating additional responses per added document.
        self.request.set('X-CREATING-SUCCESSOR', True)

        # Create the delivered documents:
        transporter = Transporter()
        documents = []

        message = _(
            u'version_message_resolved_task',
            default=u'Document copied from task (task resolved)')

        if data.get(
            'transition') == 'task-transition-in-progress-tested-and-closed':
            message = _(
                u'version_message_closed_task',
                default=u'Document copied from task (task closed)')

        for item in data['documents']:
            doc = transporter.create(item, self.context)
            Versioner(doc).set_custom_initial_version_comment(message)

            # append `RE:` prefix to the document title
            doc.title = '%s: %s' % (
                translate(
                    _(u'answer_prefix', default=u'RE'),
                    context=self.context.REQUEST),
                doc.title)

            documents.append(doc)
            notify(ObjectAddedEvent(doc))

        # This view is only called as the receiving part of a transition
        # syncing, so no workflow syncing is necessary.
        util.change_task_workflow_state(
            self.context, data['transition'], text=data['text'],
            disable_sync=True, added_objects=documents)

        return ok_response()

    def is_already_delivered(self, data):
        """When the sender has a conflict error but the reseiver already
        added the response, this view is called a second / third time in
        conflict resolution. We need to detect whether it is already done
        and not fail.
        """

        response_container = IResponseContainer(self.context)
        if len(response_container) == 0:
            return False

        last_response = response_container.list()[-1]
        current_user = AccessControl.getSecurityManager().getUser()

        if last_response.transition == data['transition'] and \
                last_response.creator == current_user.getId():
            return True

        else:
            return False
