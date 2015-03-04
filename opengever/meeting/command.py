from opengever.base.model import create_session
from opengever.base.oguid import Oguid
from opengever.base.request import dispatch_json_request
from opengever.base.transport import REQUEST_KEY
from opengever.base.transport import Transporter
from opengever.meeting import _
from opengever.meeting.model import proposalhistory
from opengever.meeting.model import SubmittedDocument
from plone import api
import json


class CreateSubmittedProposalCommand(object):

    def __init__(self, proposal):
        self.proposal = proposal
        self.submitted_proposal_path = None
        self.admin_unit_id = self.proposal.get_committee_admin_unit().id()

    def execute(self):
        model = self.proposal.load_model()
        jsondata = {'committee_oguid': model.committee.oguid.id,
                    'proposal_oguid': model.oguid.id}
        request_data = {REQUEST_KEY: json.dumps(jsondata)}
        response = dispatch_json_request(
            self.admin_unit_id, '@@create_submitted_proposal', data=request_data)

        self.submitted_proposal_path = response['path']
        create_session().add(proposalhistory.Submitted(proposal=model))


class NullUpdateSubmittedDocumentCommand(object):

    def __init__(self, document):
        self.document = document

    def execute(self):
        pass

    def show_message(self):
        portal = api.portal.get()
        api.portal.show_message(
            _(u'Document ${title} has already been submitted in that version',
              mapping=dict(title=self.document.title)),
            portal.REQUEST,
            type='warn')


class UpdateSubmittedDocumentCommand(object):

    def __init__(self, proposal, document, submitted_document):
        self.proposal = proposal
        self.document = document
        self.submitted_document = submitted_document

    def execute(self):
        Transporter().transport_to(
            self.document,
            self.submitted_document.submitted_admin_unit_id,
            self.submitted_document.submitted_physical_path,
            view='update-submitted-document')

        session = create_session()
        proposal_model = self.proposal.load_model()

        submitted_version = self.document.get_current_version()
        submitted_document = SubmittedDocument.query.get_by_source(
            self.proposal, self.document)
        submitted_document.submitted_version = submitted_version

        session.add(proposalhistory.DocumentUpdated(
            proposal=proposal_model,
            submitted_document=submitted_document,
            submitted_version=submitted_version,
            document_title=self.document.title))

    def show_message(self):
        portal = api.portal.get()
        api.portal.show_message(
            _(u'A new submitted version of document ${title} has been created',
              mapping=dict(title=self.document.title)),
            portal.REQUEST)


class CopyProposalDocumentCommand(object):
    """Copy documents attached to a proposal to the proposal's associated
    committee once a proposal is submitted.

    """
    def __init__(self, proposal, document, parent_action=None,
                 target_path=None, target_admin_unit_id=None):
        self.proposal = proposal
        self.document = document
        self._parent_action = parent_action
        self._target_path = target_path
        self._target_admin_unit_id = target_admin_unit_id

    @property
    def target_path(self):
        return self._target_path or self._parent_action.submitted_proposal_path

    @property
    def target_admin_unit_id(self):
        return self._target_admin_unit_id or self._parent_action.admin_unit_id

    def execute(self):
        reponse = self.copy_document(self.target_path, self.target_admin_unit_id)
        self.add_database_entry(reponse, self.target_admin_unit_id)

    def show_message(self):
        portal = api.portal.get()
        api.portal.show_message(
            _(u'Additional document ${title} has been submitted successfully',
              mapping=dict(title=self.document.title)),
            portal.REQUEST)

    def add_database_entry(self, reponse, target_admin_unit_id):
        session = create_session()
        proposal_model = self.proposal.load_model()
        oguid = Oguid.for_object(self.document)
        submitted_version = self.document.get_current_version()

        doc = SubmittedDocument(oguid=oguid,
                                proposal=proposal_model,
                                submitted_admin_unit_id=target_admin_unit_id,
                                submitted_int_id=reponse['intid'],
                                submitted_physical_path=reponse['path'],
                                submitted_version=submitted_version)
        session.add(doc)

        session.add(proposalhistory.DocumentSubmitted(
            proposal=proposal_model,
            submitted_document=doc,
            submitted_version=submitted_version,
            document_title=self.document.title))

    def copy_document(self, target_path, target_admin_unit_id):
        return OgCopyCommand(
            self.document, target_admin_unit_id, target_path).execute()


class OgCopyCommand(object):

    def __init__(self, source, target_admin_unit_id, target_path):
        self.source = source
        self.target_path = target_path
        self.target_admin_unit_id = target_admin_unit_id

    def execute(self):
        return Transporter().transport_to(
            self.source, self.target_admin_unit_id, self.target_path)
