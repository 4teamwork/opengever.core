from DateTime import DateTime
from Products.CMFPlone.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage
from five import grok
from opengever.base.interfaces import IRedirector
from opengever.ogds.base.interfaces import IContactInformation
from opengever.ogds.base.interfaces import ITransporter
from opengever.ogds.base.utils import remote_request, get_client_id
from opengever.task import _
from opengever.task.interfaces import ISuccessorTaskController
from opengever.task.task import ITask
from opengever.task.util import add_simple_response
from plone.directives import form
from plone.formwidget.autocomplete import AutocompleteFieldWidget
from plone.z3cform import layout
from z3c.form.button import buttonAndHandler
from z3c.form.field import Fields
from z3c.form.form import Form
from zope import schema
from zope.component import getUtility
from zope.lifecycleevent import modified
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
import os.path


class ISuccessorTaskSchema(form.Schema):
    """Schema interface for choosing one of the assigned clients when creating
    a successor task.
    """

    client = schema.Choice(
        title=_(u'label_sucessor_target_client',
                default=u'Target client for successor task'),
        description=_(u'help_successor_target_client',
                      default=u'Choose on which client to create the '
                      'successor task.'),
        vocabulary='opengever.ogds.base.AssignedClientsVocabulary',
        required=True)

    dossier = schema.Choice(
        title=_(u'label_successor_target_dossier', default=u'Target Dossier'),
        description=_(u'help_successor_target_dossier',
                      default=u'Select the target dossier on the client '
                      'selected above.'),
        vocabulary=u'opengever.ogds.base.HomeDossiersVocabulary',
        required=True,
        )



class SuccessorTaskForm(Form):
    """Successor task form.
    """

    fields = Fields(ISuccessorTaskSchema)
    fields['dossier'].widgetFactory = AutocompleteFieldWidget
    label=_(u'title_create_successor_task', default=u'Create successor task')
    ignoreContext = True

    @buttonAndHandler(_(u'button_continue', default=u'Continue'))
    def handle_continue(self, action):
        data, errors = self.extractData()
        if not errors:
            trans = getUtility(ITransporter)
            successor_controller = ISuccessorTaskController(self.context)
            info = getUtility(IContactInformation)

            # transport task
            response = trans.transport_to(self.context, data['client'],
                                          data['dossier'])
            target_task_path = response.read()

            # connect tasks and change state of successor
            response = remote_request(
                data['client'], '@@cleanup-successor-task',
                path=target_task_path,
                data={'oguid': successor_controller.get_oguid()})

            if response.read().strip() != 'ok':
                raise Exception('Cleaning up the successor task failed on the'
                                'remote client %s' % data['client'])

            # copy documents
            for doc in self.get_documents():
                trans.transport_to(doc, data['client'], target_task_path)

            # create a response indicating that a response was created
            successor_oguid = successor_controller.get_oguid_by_path(
                target_task_path, data['client'])
            add_simple_response(self.context, successor_oguid=successor_oguid)

            # redirect to target in new window
            client = info.get_client_by_id(data['client'])
            target_url = os.path.join(client.public_url, target_task_path,
                                      '@@edit')

            if get_client_id() != data['client']:
                # foreign client (open in popup)
                redirector = IRedirector(self.request)
                redirector.redirect(target_url, target='_blank')

                # add status message and redirect current window back to task
                IStatusMessage(self.request).addStatusMessage(
                    _(u'info_created_successor_task',
                      u'The successor task was created.'), type='info')

                return self.request.RESPONSE.redirect(
                    self.context.absolute_url())

            else:
                # not foreign client (regular redirect)
                # add status message and redirect current window back to task
                IStatusMessage(self.request).addStatusMessage(
                    _(u'info_created_successor_task',
                      u'The successor task was created.'), type='info')

                return self.request.RESPONSE.redirect(target_url)

    @buttonAndHandler(_(u'button_cancel', default=u'Cancel'))
    def handle_cancel(self, action):
        return self.request.RESPONSE.redirect('.')



    def get_documents(self):
        """All documents which are either within the current task or defined
        as related items.
        """
        # find documents within the task
        brains = self.context.getFolderContents(
            full_objects=False,
            contentFilter={'portal_type': 'opengever.document.document'})
        for doc in brains:
            yield doc.getObject()
        # find referenced documents
        relatedItems = getattr(self.context, 'relatedItems', None)
        if relatedItems:
            for rel in self.context.relatedItems:
                yield rel.to_object


class CreateSuccessorTask(layout.FormWrapper, grok.CodeView):
    grok.context(ITask)
    grok.name('create-successor-task')
    grok.require('zope2.View')
    form = SuccessorTaskForm

    def __init__(self, *args, **kwargs):
        layout.FormWrapper.__init__(self, *args, **kwargs)
        grok.CodeView.__init__(self, *args, **kwargs)



class CleanupSuccessor(grok.CodeView):
    """Do cleanup tasks after creating a successor:
    - add a global reference to the predecessor
    - move the successor task in a special initial state
    """

    grok.context(ITask)
    grok.name('cleanup-successor-task')

    grok.require('zope2.View')

    def render(self):
        self.set_predecessor()
        self.set_workflow_state()
        self.remove_responsible()
        return 'ok'

    def set_predecessor(self):
        oguid = self.request.get('oguid', None)
        if not oguid:
            raise ValueError('No valid oguid found in request.')

        scontroller = ISuccessorTaskController(self.context)
        scontroller.set_predecessor(oguid)

    def set_workflow_state(self):
        state = 'task-state-new-successor'
        mtool = getToolByName(self.context, 'portal_membership')
        wtool = getToolByName(self.context, 'portal_workflow')
        current_user_id = mtool.getAuthenticatedMember().getId()
        wf_ids = wtool.getChainFor(self.context)
        if wf_ids:
            wf_id = wf_ids[0]
            comment = 'Created successor.'
            wtool.setStatusOf(wf_id, self.context, {'review_state': state,
                                                    'action' : state,
                                                    'actor': current_user_id,
                                                    'time': DateTime(),
                                                    'comments': comment,})

            wfs = {wf_id: wtool.getWorkflowById(wf_id)}
            wtool._recursiveUpdateRoleMappings(self.context, wfs)
            self.context.reindexObjectSecurity()

    def remove_responsible(self):
        """Remove the responsible. This solves a problem with the
        responsible_client and responsible fields in combination with the
        autocomplete widget. It makes anyway sence that the users has to select
        a new responsible.
        """
        task = ITask(self.context)
        task.responsible_client = None
        task.responsible = None
        self.context.reindexObject()


@grok.subscribe(ITask, IObjectModifiedEvent)
def change_successor_state_after_edit(task, event):
    """After creating a successor the task is has a special successor initial
    state because the user needs to be able to edit the task once.
    After the user has edited the task we move it to the default initial state.
    """

    # the event is fired multiple times when the task was transported, so we
    # need to verify that the request was not called by another client
    request = task.REQUEST
    if request.get_header('X-OGDS-AC', None) or \
            request.get_header('X-OGDS-CID', None):
        return

    from_review_state = 'task-state-new-successor'
    to_review_state = 'task-state-open'

    wtool = getToolByName(task, 'portal_workflow')
    review_state = wtool.getInfoFor(task, 'review_state', None)

    if review_state == from_review_state:

        mtool = getToolByName(task, 'portal_membership')
        current_user_id = mtool.getAuthenticatedMember().getId()
        wf_ids = wtool.getChainFor(task)

        if wf_ids:
            wf_id = wf_ids[0]
            comment = 'Initial state after editing successor metadata.'
            wtool.setStatusOf(wf_id, task, {'review_state': to_review_state,
                                            'action' : to_review_state,
                                            'actor': current_user_id,
                                            'time': DateTime(),
                                            'comments': comment,})
            wfs = {wf_id: wtool.getWorkflowById(wf_id)}
            wtool._recursiveUpdateRoleMappings(task, wfs)

            modified(task)
