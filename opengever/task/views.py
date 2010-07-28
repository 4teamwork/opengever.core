from five import grok
from opengever.octopus.tentacle.interfaces import IContactInformation
from opengever.octopus.tentacle.interfaces import ICortexCommunicator
from opengever.octopus.tentacle.interfaces import ITentacleConfig
from opengever.octopus.tentacle.interfaces import ITransporter
from zope.component import getUtility
from zope.interface import Interface
import os.path

class CopyRelatedDocumentsToInbox(grok.CodeView):
    grok.context(Interface)
    grok.name('copy-related-documents-to-inbox')

    def __call__(self, event):
        # fix context
        self.scripts = self.context
        self.event = event
        self.context = event.object
        # we need some utilities
        self.comm = getUtility(ICortexCommunicator)
        self.tc = getUtility(ITentacleConfig)
        self.contacts = getUtility(IContactInformation)
        self.transporter = getUtility(ITransporter)
        # check if we need to copy
        if not self.should_be_copied():
            return False
        self.copy_documents()
        return

    def render(self):
        # make grok happy
        pass

    def should_be_copied(self):
        home_client = self.comm.get_home_client(self.context)
        member = self.context.portal_membership.getAuthenticatedMember()
        # only copy if we are not on our home-client
        if self.tc.cid==home_client['cid']:
            return False
        # the task type category should be uni_val
        if self.context.task_type_category!=u'uni_val':
            return False
        # we should be able to write to our home-client inbox. that means the current
        # user should be in the main group (which must have privileges)
        home_inbox_group = self.comm.get_client_inbox_group(home_client['cid'])
        if home_inbox_group not in member.getGroups():
            return False
        # the responsible should be a inbox principal
        if not self.contacts.is_inbox_principal(self.context.responsible):
            return False
        return True

    def copy_documents(self):
        home_client = self.comm.get_home_client(self.context)
        target_cid = home_client['cid']
        container_path = os.path.join(self.comm.get_client_site_path(target_cid),
                                      'eingangskorb')
        for doc in self.get_documents():
            self.transporter.transport_to(doc, target_cid, container_path)

    def get_documents(self):
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

