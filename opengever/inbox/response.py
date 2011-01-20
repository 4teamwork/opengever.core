"""Provides a custom forwarding implementation used
for forwardings.
"""

from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage
from five import grok
from opengever.base.interfaces import IRedirector
from opengever.base.source import RepositoryPathSourceBinder
from opengever.inbox import _
from opengever.inbox.forwarding import IForwarding
from opengever.ogds.base.interfaces import IContactInformation
from opengever.ogds.base.interfaces import ITransporter
from opengever.ogds.base.utils import remote_request
from opengever.task.interfaces import ISuccessorTaskController
from opengever.task.response import IResponse, AddForm, SingleAddFormView
from z3c.form import field, button
from z3c.form.browser import radio
from z3c.form.interfaces import HIDDEN_MODE, DISPLAY_MODE
from z3c.relationfield.schema import RelationChoice, RelationList
from zope.component import getUtility
import os.path


class IForwardingResponse(IResponse):

    target_dossier = RelationList(
        title=_(u'label_target_dossier',
                default=u'Target dossier'),
        default=[],
        required=False,
        value_type=RelationChoice(
            title=u'Target dossier',
            source=RepositoryPathSourceBinder(
                object_provides='opengever.dossier.behaviors.dossier.' + \
                    'IDossierMarker',
                navigation_tree_query={
                    'object_provides':
                        ['opengever.repository.repositoryroot.IRepositoryRoot',
                         'opengever.repository.repositoryfolder.' + \
                             'IRepositoryFolderSchema',
                         'opengever.dossier.behaviors.dossier.IDossierMarker',]
                    })))



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
        else:
            self.widgets['target_dossier'].required = False

    @button.buttonAndHandler(_(u'save', default='Save'),
                             name='save', )
    def handleContinue(self, action):
        data, errors = self.extractData()
        response = super(ForwardingResponseAddForm, self).handleContinue(
            action.form, action)
        if not response:
            return

        wftool = getToolByName(self.context, 'portal_workflow')
        workflow = wftool.getWorkflowById(wftool.getChainFor(self.context)[0])
        transition_id = data['transition']
        if type(transition_id) in (list, tuple):
            transition_id = transition_id[0]
        transition = workflow.transitions[transition_id]
        new_state_id = transition.new_state_id

        # ACCEPT
        if transition_id == 'forwarding-transition-accept':
            self.create_successor_forwarding(data)

        if new_state_id == 'forwarding-state-closed':
            # When the forwarding is closed, we need to move it to the
            # folder for the current year (a kind of an archive). If there
            # is no folder, create it.

            # # search the inbox
            # inbox = self.context
            # while not IPloneSiteRoot.providedBy(inbox):
            #     if IInbox.providedBy(inbox):
            #         break
            #     else:
            #         inbox = aq_parent(aq_inner(inbox))

            # # get or create the year folder
            # year = datetime.now().strftime('%Y')
            # folder = inbox.get(year, None)
            # if not folder:
            #     folder = createContentInContainer(inbox, '')
            IStatusMessage(self.request).addStatusMessage(
                'YEAR FOLDERS NOT YET IMPLEMENTED', type='error')

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
        httpresponse = trans.transport_to(self.context, client.client_id,
                                          'eingangskorb')
        target_task_path = httpresponse.read()

        # connect tasks and change state of successor
        response = remote_request(
            client.client_id, '@@cleanup-successor-task',
            path=target_task_path,
            data={'oguid': successor_controller.get_oguid()})

        if response.read().strip() != 'ok':
            raise Exception('Cleaning up the successor task failed on the'
                            'remote client %s' % client.client_id)

        # copy documents
        for doc in self.get_documents():
            trans.transport_to(doc, client.client_id, target_task_path)

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
        """All documents which are either within the current task or defined
        as related items.
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




class ForwardingResponseAddFormView(SingleAddFormView):
    grok.context(IForwarding)
    grok.name('addresponse')

    form = ForwardingResponseAddForm
