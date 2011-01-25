"""Provides a custom forwarding implementation used
for forwardings.
"""

from Acquisition import aq_inner, aq_parent
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from Products.statusmessages.interfaces import IStatusMessage
from copy import deepcopy
from datetime import datetime
from five import grok
from opengever.base.interfaces import IRedirector
from opengever.inbox import _
from opengever.inbox.forwarding import IForwarding
from opengever.inbox.inbox import IInbox
from opengever.ogds.base.interfaces import IContactInformation
from opengever.ogds.base.interfaces import ITransporter
from opengever.ogds.base.utils import remote_request, get_client_id
from opengever.task.adapters import IResponse as IPersistentResponse
from opengever.task.adapters import IResponseContainer
from opengever.task.browser.successor import CleanupSuccessor
from opengever.task.interfaces import ISuccessorTaskController
from opengever.task.response import AddForm, SingleAddFormView
from opengever.task.response import IResponse, Response
from opengever.task.task import ITask
from opengever.task.transporter import IResponseTransporter
from plone.dexterity.utils import createContentInContainer
from plone.formwidget.contenttree import ObjPathSourceBinder
from z3c.form import field, button
from z3c.form.browser import radio
from z3c.form.interfaces import HIDDEN_MODE
from z3c.relationfield.schema import RelationChoice
from zope.app.intid.interfaces import IIntIds
from zope.component import getUtility
from zope.interface.interface import Attribute
from zope.lifecycleevent import modified
import AccessControl
import os.path


class IForwardingResponse(IResponse):

    target_dossier = RelationChoice(
        title=_(u'label_target_dossier',
                default=u'Target dossier'),
        default=None,
        required=False,
        source=ObjPathSourceBinder(
            object_provides='opengever.dossier.behaviors.dossier.' +\
                'IDossierMarker',
            navigation_tree_query={
                'object_provides':
                    ['Products.CMFPlone.interfaces.siteroot.' +\
                         'IPloneSiteRoot',
                     'opengever.repository.repositoryroot.' +\
                         'IRepositoryRoot',
                     'opengever.repository.repositoryfolder.' +\
                         'IRepositoryFolderSchema',
                     'opengever.dossier.behaviors.dossier.' +\
                         'IDossierMarker']
                }))


class ForwardingResponseAddForm(AddForm):
    """Custom addform for forwarding-responses.
    """
    fields = field.Fields(IForwardingResponse)
    fields['transition'].widgetFactory = radio.RadioFieldWidget
    fields = fields.omit('date_of_completion')

    def updateWidgets(self):
        super(ForwardingResponseAddForm, self).updateWidgets()
        self.widgets['relatedItems'].mode = HIDDEN_MODE
        # self.widgets['transition'].mode = HIDDEN_MODE
        assign_trans = u'forwarding-transition-assign-to-dossier'
        if assign_trans not in self.widgets['transition'].value:
            self.widgets['target_dossier'].mode = HIDDEN_MODE
            self.fields['target_dossier'].field.required = False
            self.widgets['target_dossier'].required = False
        else:
            self.fields['target_dossier'].field.required = True
            self.widgets['target_dossier'].required = True

    @button.buttonAndHandler(_(u'save', default='Save'),
                             name='save', )
    def handleSubmit(self, action):
        data, errors = self.extractData()
        if errors:
            return

        wftool = getToolByName(self.context, 'portal_workflow')
        workflow = wftool.getWorkflowById(wftool.getChainFor(
                self.context)[0])
        transition_id = data['transition']
        if type(transition_id) in (list, tuple):
            transition_id = transition_id[0]
        transition = workflow.transitions[transition_id]
        new_state_id = transition.new_state_id

        # ASSIGN TO DOSSIER
        if transition_id == 'forwarding-transition-assign-to-dossier':
            target_task = self.assign_to_dossier(data)

        # CREATE RESPONSE
        response = super(ForwardingResponseAddForm, self).handleSubmit(
            action.form, action)

        # add relation to response
        if transition_id == 'forwarding-transition-assign-to-dossier':
            taskSTC = ISuccessorTaskController(target_task)
            response.successor_oguid = taskSTC.get_oguid()

        # ACCEPT
        if transition_id == 'forwarding-transition-accept':
            self.create_successor_forwarding(data)

        # REFUSE
        if transition_id == 'forwarding-transition-refuse':
            self.ressign_refusing(response)

        if new_state_id == 'forwarding-state-closed':
            # When the forwarding is closed, we need to move it to the
            # folder for the current year (a kind of an archive). If there
            # is no folder, create it.

            # search the inbox
            inbox = self.context
            while not IPloneSiteRoot.providedBy(inbox):
                if IInbox.providedBy(inbox):
                    break
                else:
                    inbox = aq_parent(aq_inner(inbox))

            # get or create the year folder
            year = datetime.now().strftime('%Y')
            folder = inbox.get(year, None)

            _sm = AccessControl.getSecurityManager()
            AccessControl.SecurityManagement.newSecurityManager(
                self.request,
                AccessControl.SecurityManagement.SpecialUsers.system)
            try:
                if not folder:
                    # for creating the folder, we need to be a superuser since
                    # normal user should not be able to add year folders.
                    folder = createContentInContainer(
                        inbox, 'opengever.inbox.yearfolder',
                        title=str(year))

                # move forwarding into folder
                parent = aq_parent(aq_inner(self.context))
                clipboard = parent.manage_cutObjects((self.context.getId(),))
                folder.manage_pasteObjects(clipboard)

            except:
                AccessControl.SecurityManagement.setSecurityManager(
                    _sm)
                raise
            else:
                AccessControl.SecurityManagement.setSecurityManager(
                    _sm)

            # show status message
            msg = _(u'info_forwarding_move_to_yearfolder',
                    default=u'The forwarding was moved to the '
                    'yearfolder ${year}',
                    mapping=dict(year=str(year)))

            IStatusMessage(self.request).addStatusMessage(
                msg, type='info')

    @button.buttonAndHandler(_(u'cancel', default='Cancel'),
                             name='cancel', )
    def handleCancel(self, action):
        return self.request.RESPONSE.redirect('.')

    def create_successor_forwarding(self, data):
        """"Accepting" means we create a successor-forwarding on the
        responsible_client (which the user should be assigned to)
        and link them together."""
        info = getUtility(IContactInformation)
        trans = getUtility(ITransporter)
        successor_controller = ISuccessorTaskController(self.context)

        client = info.get_client_by_id(self.context.responsible_client)
        if client not in info.get_assigned_clients():
            # this should never happen
            RuntimeError('The user should be assigned to client %s' %
                         self.context.responsible_client)

        # send the the task to the remote client
        result = trans.transport_to(self.context, client.client_id,
                                          'eingangskorb')
        target_task_path = result['path']

        # copy documents. we need to create a intids mapping
        # (intid on our client : intid on remote client) for
        # being able in the response transporter to change fix
        # the intids of relation values.
        intids_mapping = {}
        intids = getUtility(IIntIds)
        for doc in self.get_documents():
            result = trans.transport_to(doc, client.client_id,
                                        target_task_path)
            intids_mapping[intids.queryId(doc)] = result['intid']

        # copy responses
        response_transporter = IResponseTransporter(self.context)
        response_transporter.send_responses(
            client.client_id, target_task_path, intids_mapping)

        # connect tasks and change state of successor
        response = remote_request(
            client.client_id, '@@cleanup-successor-task',
            path=target_task_path,
            data={'oguid': successor_controller.get_oguid()})

        if response.read().strip() != 'ok':
            raise Exception('Cleaning up the successor task failed on '
                            'the remote client %s' % client.client_id)

        # add to the just-created response a "link" to the successor
        successor_oguid = successor_controller.get_oguid_by_path(
            target_task_path, client.client_id)
        response.successor_oguid = successor_oguid

        # redirect to target in new window
        client = info.get_client_by_id(client.client_id)
        target_url = os.path.join(client.public_url, target_task_path,
                                  '@@edit')
        redirector = IRedirector(self.request)
        redirector.redirect(target_url, target='_blank')

        # add status message and redirect current window back to task
        IStatusMessage(self.request).addStatusMessage(
            _(u'info_created_successor_forwarding',
              u'The successor forwarding was created.'), type='info')

    def get_documents(self):
        """All documents which are either within the current task or
        defined as related items.
        """
        # find documents within the task
        brains = self.context.getFolderContents(
            full_objects=False,
            contentFilter={'portal_type': ['opengever.document.document',
                                           'ftw.mail.mail']})
        for doc in brains:
            yield doc.getObject()
        # find referenced documents
        relatedItems = getattr(self.context, 'relatedItems', None)
        if relatedItems:
            for rel in self.context.relatedItems:
                yield rel.to_object

    def ressign_refusing(self, response):
        """ When refusing, reassign forwarding to the inbox of the client
        which raised the forwarding, so that it can be reassigned
        afterwards to another client / person.
        """
        new_client = get_client_id()

        # change responsible client
        response.add_change('responsible_client',
                            IForwarding['responsible_client'].title,
                            self.context.responsible_client,
                            new_client)
        self.context.responsible_client = new_client

        # change responsible
        new_responsible = u'inbox:%s' % get_client_id()
        response.add_change('responsible',
                            IForwarding['responsible'].title,
                            self.context.responsible,
                            new_responsible)
        self.context.responsible = new_responsible

        modified(self.context)

    def assign_to_dossier(self, data):
        """Assigning to a dossier means creating a successor task (!).
        """
        # There is a change_successor_state_after_edit which resets
        # the tasks workflow state on modified event. We dont want it
        # to do that on this request - so we need to set a prevention
        # flag.
        self.request.set('X-CREATING-SUCCESSOR', True)

        dossier = data['target_dossier']
        forwarding = self.context

        # we need all task field values from the forwarding (which is a
        # kind of task) for creating the new task.
        fielddata = {}
        for fieldname in ITask.names():
            field = ITask.get(fieldname)
            value = field.get(forwarding)
            fielddata[fieldname] = value

        # lets create a new task - the successor task
        task = createContentInContainer(dossier, 'opengever.task.task',
                                        **fielddata)

        # copy all responses
        task_responses = IResponseContainer(task)
        for id, fresp in enumerate(IResponseContainer(forwarding)):
            tresp = Response('')
            for key in IPersistentResponse.names():
                attr = IPersistentResponse[key]
                if type(attr) == Attribute:
                    setattr(tresp, key,
                            deepcopy(getattr(fresp, key, None)))
            tresp._p_changed = True
            task_responses.add(tresp)

        # set the predecessor
        taskSTC = ISuccessorTaskController(task)
        forwardingSTC = ISuccessorTaskController(forwarding)
        taskSTC.set_predecessor(forwardingSTC.get_oguid())

        # set the workflow state
        state = 'task-state-new-successor'
        mtool = getToolByName(self.context, 'portal_membership')
        wtool = getToolByName(self.context, 'portal_workflow')
        current_user_id = mtool.getAuthenticatedMember().getId()
        wf_ids = wtool.getChainFor(task)
        if wf_ids:
            wf_id = wf_ids[0]
            comment = 'Created successor.'
            wtool.setStatusOf(wf_id, task, {'review_state': state,
                                            'action' : state,
                                            'actor': current_user_id,
                                            'time': DateTime(),
                                            'comments': comment,})

            wfs = {wf_id: wtool.getWorkflowById(wf_id)}
            wtool._recursiveUpdateRoleMappings(task, wfs)
            task.reindexObjectSecurity()

        # Remove the responsible. This solves a problem with the
        # responsible_client and responsible fields in combination with the
        # autocomplete widget. It makes anyway sence that the users has to
        # select a new responsible.
        task = ITask(task)
        task.responsible_client = None
        task.responsible = None
        task.reindexObject()

        # copy documents
        for doc in self.get_documents():
            parent = aq_parent(aq_inner(doc))
            clipboard = parent.manage_copyObjects([doc.getId()])
            task.manage_pasteObjects(clipboard)

        # redirect to edit view later
        redirector = IRedirector(self.request)
        redirector.redirect(task.absolute_url() + '/edit')
        return task


class CleanupForwardingSuccessor(CleanupSuccessor):
    """For forwardings, we need to modify the behavior a little bit.
    """

    grok.context(IForwarding)

    def set_workflow_state(self):
        """Do not change the workflow state, because the initial state is
        quite ok.
        """
        return


class ForwardingResponseAddFormView(SingleAddFormView):
    grok.context(IForwarding)
    grok.name('addresponse')

    form = ForwardingResponseAddForm
