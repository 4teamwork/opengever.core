from Products.statusmessages.interfaces import IStatusMessage
from five import grok
from opengever.base.interfaces import IRedirector
from opengever.ogds.base.interfaces import IContactInformation
from opengever.ogds.base.interfaces import ITransporter
from opengever.ogds.base.utils import remote_request, get_client_id
from opengever.task import _
from opengever.task.interfaces import ISuccessorTaskController
from opengever.task.task import ITask
from opengever.task.transporter import IResponseTransporter
from opengever.task.util import add_simple_response
from plone.directives import form
from plone.formwidget.autocomplete import AutocompleteFieldWidget
from plone.z3cform import layout
from z3c.form.button import buttonAndHandler
from z3c.form.field import Fields
from z3c.form.form import Form
from z3c.form.interfaces import HIDDEN_MODE
from zope import schema
from zope.app.intid.interfaces import IIntIds
from zope.component import getUtility
import os.path


class ISuccessorTaskSchema(form.Schema):
    """Schema interface for choosing one of the assigned clients when creating
    a successor task.
    """

    form.mode(client=HIDDEN_MODE)
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
    label = _(u'title_create_successor_task', default=u'Create successor task')
    ignoreContext = True

    @buttonAndHandler(_(u'button_continue', default=u'Continue'))
    def handle_continue(self, action):
        data, errors = self.extractData()
        if not errors:
            trans = getUtility(ITransporter)
            successor_controller = ISuccessorTaskController(self.context)
            info = getUtility(IContactInformation)

            # transport task
            result = trans.transport_to(self.context, data['client'],
                                          data['dossier'])
            target_task_path = result['path']

            # connect tasks and change state of successor
            response = remote_request(
                data['client'], '@@cleanup-successor-task',
                path=target_task_path,
                data={'oguid': successor_controller.get_oguid()})

            if response.read().strip() != 'ok':
                raise Exception('Cleaning up the successor task failed on the'
                                'remote client %s' % data['client'])

            # copy documents. we need to create a intids mapping
            # (intid on our client : intid on remote client) for
            # being able in the response transporter to change fix
            # the intids of relation values.
            intids_mapping = {}
            intids = getUtility(IIntIds)
            for doc in self.get_documents():
                result = trans.transport_to(doc, data['client'],
                                            target_task_path)
                intids_mapping[intids.queryId(doc)] = result['intid']

            # copy responses
            response_transporter = IResponseTransporter(self.context)
            response_transporter.send_responses(
                data['client'], target_task_path, intids_mapping)

            # create a response indicating that a successor was created
            successor_oguid = successor_controller.get_oguid_by_path(
                target_task_path, data['client'])
            add_simple_response(self.context, successor_oguid=successor_oguid)

            # redirect to target in new window
            client = info.get_client_by_id(data['client'])
            target_url = os.path.join(client.public_url, target_task_path,
                                      '@@edit')

            if get_client_id() != data['client']:
                # foreign client (open in popup) and with a jq-expose
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
            contentFilter={'portal_type': ['opengever.document.document',
                                           'ftw.mail.mail']})
        for doc in brains:
            yield doc.getObject()
        # find referenced documents
        relatedItems = getattr(self.context, 'relatedItems', None)
        if relatedItems:
            for rel in self.context.relatedItems:
                yield rel.to_object

    def updateWidgets(self):
        super(SuccessorTaskForm, self).updateWidgets()
        self.widgets['client'].mode = HIDDEN_MODE
        self.widgets['client'].value = self.context.responsible_client
        self.request['form.widgets.client'] = self.widgets['client'].value


class CreateSuccessorTask(layout.FormWrapper, grok.View):
    grok.context(ITask)
    grok.name('create-successor-task')
    grok.require('zope2.View')
    form = SuccessorTaskForm

    def __init__(self, *args, **kwargs):
        layout.FormWrapper.__init__(self, *args, **kwargs)
        grok.View.__init__(self, *args, **kwargs)


class CleanupSuccessor(grok.View):
    """Do cleanup tasks after creating a successor:
    - add a global reference to the predecessor
    - move the successor task in a special initial state
    """

    grok.context(ITask)
    grok.name('cleanup-successor-task')

    grok.require('zope2.View')

    def render(self):
        # WARNING: Be aware that this request may be called multiple times for
        # doing the same if the sender-client has a conflict error (which is
        # solved be redoing the request)!
        self.set_predecessor()
        return 'ok'

    def set_predecessor(self):
        oguid = self.request.get('oguid', None)
        if not oguid:
            raise ValueError('No valid oguid found in request.')

        scontroller = ISuccessorTaskController(self.context)
        scontroller.set_predecessor(oguid)
