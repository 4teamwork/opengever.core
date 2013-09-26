from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from five import grok
from opengever.inbox import _
from opengever.inbox.browser.schema import ISimpleResponseForm
from opengever.inbox.forwarding import IForwarding
from opengever.ogds.base.interfaces import IContactInformation
from opengever.ogds.base.interfaces import ITransporter
from opengever.ogds.base.transport import ORIGINAL_INTID_ANNOTATION_KEY
from opengever.ogds.base.transport import REQUEST_KEY
from opengever.ogds.base.utils import get_client_id
from opengever.ogds.base.utils import remote_json_request
from opengever.task import _ as task_mf
from opengever.task.browser.accept.utils import _get_yearfolder
from opengever.task.transporter import IResponseTransporter
from opengever.task.util import add_simple_response
from opengever.task.util import get_documents_of_task
from plone.z3cform import layout
from z3c.form import button
from z3c.form.field import Fields
from z3c.form.form import Form
from zope.annotation.interfaces import IAnnotations
from zope.component import getUtility
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent
import json


STATUS_SUCCESSFULL = 1
STATUS_ALLREADY_DONE = 2


class ForwardingRefuseForm(Form):

    fields = Fields(ISimpleResponseForm)
    ignoreContext = True
    label = _(u'label_refuse_forwarding', default=u'Refuse Forwarding')

    @button.buttonAndHandler(
        _(u'label_refuse', default='Refuse'), name='refuse')
    def handle_refuse(self, action):

        data, errors = self.extractData()
        if not errors:

            refusing_client = self.context.responsible_client
            self.change_workflow_sate()
            self.add_response(data.get('text'))
            copy_url = self.store_copy_in_remote_yearfolder(refusing_client)
            self.reset_responsible()
            notify(ObjectModifiedEvent(self.context))

        return self.request.RESPONSE.redirect(copy_url)

    @button.buttonAndHandler(task_mf(u'button_cancel', default=u'Cancel'))
    def handle_cancel(self, action):
        return self.request.RESPONSE.redirect('.')

    def reset_responsible(self):
        """Set responsible back to the issuer respectively current inbox."""

        self.context.responsible_client = get_client_id()
        self.context.responsible = u'inbox:%s' % (
            self.context.responsible_client)

    def add_response(self, response_text):
        add_simple_response(
            self.context,
            text=response_text,
            transition=u'forwarding-transition-refuse')

    def change_workflow_sate(self):
        wf_tool = getToolByName(self.context, 'portal_workflow')
        wf_tool.doActionFor(self.context, 'forwarding-transition-refuse')

    def store_copy_in_remote_yearfolder(self, refusing_client_id):
        transporter = getUtility(ITransporter)
        jsondata = json.dumps(transporter._extract_data(self.context))
        request_data = {REQUEST_KEY: jsondata, }

        response = remote_json_request(
            refusing_client_id, '@@store_refused_forwarding',
            data=request_data)

        if response.get('status') not in [
                STATUS_SUCCESSFULL, STATUS_ALLREADY_DONE]:
            raise Exception(
                'Storing the forwarding on remote yearfolder failed')

        remote_task = response.get('remote_task')
        if response.get('status') != STATUS_ALLREADY_DONE:
            # transport responses
            response_transporter = IResponseTransporter(self.context)
            response_transporter.send_responses(
                refusing_client_id, remote_task)

            # transport documents
            for document in get_documents_of_task(self.context):
                transporter.transport_to(
                    document, refusing_client_id, remote_task)

        return self.get_remote_task_url(refusing_client_id, remote_task)

    def get_remote_task_url(self, refusing_client_id, remote_task):
        info = getUtility(IContactInformation)
        return '%s/%s' % (
            info.get_client_by_id(refusing_client_id).public_url,
            remote_task)


class RefuseForwardingView(layout.FormWrapper, grok.View):
    """A view which reassign the forwarding to the inbox of the client
    which raised the forwarding, so that it can be reassigned
    afterwards to another client / person."""

    grok.context(IForwarding)
    grok.name('refuse-task')
    grok.require('zope2.View')

    form = ForwardingRefuseForm

    def __init__(self, *args, **kwargs):
        layout.FormWrapper.__init__(self, *args, **kwargs)
        grok.View.__init__(self, *args, **kwargs)

    __call__ = layout.FormWrapper.__call__


class StoreRefusedForwardingView(grok.View):
    grok.context(IPloneSiteRoot)
    grok.name('store_refused_forwarding')
    grok.require('zope2.View')

    yearfolder = None

    def render(self):
        self.request.response.setHeader("Content-type", "text/plain")

        response = {}
        if self.is_already_done():
            response['status'] = STATUS_ALLREADY_DONE
            forwarding = self.get_newest_closed_forwarding()
        else:
            response['status'] = STATUS_SUCCESSFULL
            forwarding = self.create_forwarding()
            self.update_workflow(forwarding)

        url_tool = getToolByName(self.context, 'portal_url')
        response['remote_task'] = '/'.join(
            url_tool.getRelativeContentPath(forwarding))
        return json.dumps(response)

    def get_yearfolder(self):
        if not self.yearfolder:
            catalog = getToolByName(self.context, 'portal_catalog')
            inbox = catalog(portal_type='opengever.inbox.inbox')[0].getObject()
            self.yearfolder = _get_yearfolder(inbox)

        return self.yearfolder

    def get_newest_closed_forwarding(self):
        """Returns the newest forwarding form the actual yearfolder.
        None if it's emtpy"""

        yearfolder = self.get_yearfolder()
        stored_forwardings = yearfolder.getFolderContents(
            {'sort_on': 'created', })

        if len(stored_forwardings):
            return stored_forwardings[0].getObject()
        return None

    def create_forwarding(self):
        """Create a copy of the given forwarding in the request to
        the actual yearfolder."""

        yearfolder = self.get_yearfolder()
        transporter = getUtility(ITransporter)
        return transporter.receive(yearfolder, self.request)

    def update_workflow(self, forwarding):
        wftool = getToolByName(self.context, 'portal_workflow')
        chain = wftool.getChainFor(forwarding)
        wftool.setStatusOf(chain[0], forwarding, {
            'review_state': 'forwarding-state-closed',
            'action': '',
            'actor': ''})

        notify(ObjectModifiedEvent(forwarding))

    def is_already_done(self):
        """When the sender (caller of this view) has a conflict error, this
        view is called on the receiver multiple times, even when the changes
        are already done the first time. We need to detect such requests and
        tell the sender that it has worked.
        """

        newest_forwarding = self.get_newest_closed_forwarding()
        if not newest_forwarding:
            return False
        return self.compare_forwarding_with_request_data(newest_forwarding)

    def compare_forwarding_with_request_data(self, forwarding):
        """Compare the given forwarding, with the data in the request.
        Returns True if the original_id is the same like in the request
        data otherwise False"""

        data = json.loads(self.request.get(REQUEST_KEY))
        orig_intid = IAnnotations(forwarding)[ORIGINAL_INTID_ANNOTATION_KEY]

        return data.get(u'unicode:intid-data') == orig_intid
