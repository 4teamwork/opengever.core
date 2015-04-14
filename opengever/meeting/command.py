from Acquisition import aq_inner
from Acquisition import aq_parent
from opengever.base.command import CreateDocumentCommand
from opengever.base.model import create_session
from opengever.base.oguid import Oguid
from opengever.base.request import dispatch_json_request
from opengever.base.transport import REQUEST_KEY
from opengever.base.transport import Transporter
from opengever.meeting import _
from opengever.meeting.model import GeneratedPreProtocol
from opengever.meeting.model import GeneratedProtocol
from opengever.meeting.model import proposalhistory
from opengever.meeting.model import SubmittedDocument
from opengever.meeting.protocol import ExcerptProtocolData
from opengever.meeting.protocol import PreProtocolData
from opengever.meeting.protocol import ProtocolData
from opengever.meeting.sablon import Sablon
from plone import api
import json


MIME_DOCX = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'


class PreProtocolOperations(object):

    def get_sablon_template(self, meeting):
        return meeting.get_pre_protocol_template()

    def get_meeting_data(self, meeting):
        return PreProtocolData(meeting)

    def create_database_entry(self, meeting, document):
        pre_protocol_document = GeneratedPreProtocol(
            oguid=Oguid.for_object(document),
            generated_version=document.get_current_version())
        meeting.pre_protocol_document = pre_protocol_document
        return pre_protocol_document

    def get_generated_message(self, meeting):
        return _(u'Pre-protocol for meeting ${title} has been generated '
                 'successfully',
                 mapping=dict(title=meeting.get_title()))

    def get_updated_message(self, meeting):
        return _(u'Pre-protocol for meeting ${title} has been updated '
                 'successfully',
                 mapping=dict(title=meeting.get_title()))

    def get_title(self, meeting):
        return meeting.get_pre_protocol_title()

    def get_filename(self, meeting):
        return meeting.get_pre_protocol_filename()


class ProtocolOperations(PreProtocolOperations):

    def get_sablon_template(self, meeting):
        return meeting.get_protocol_template()

    def get_meeting_data(self, meeting):
        return ProtocolData(meeting)

    def create_database_entry(self, meeting, document):
        protocol_document = GeneratedProtocol(
            oguid=Oguid.for_object(document),
            generated_version=document.get_current_version())
        meeting.protocol_document = protocol_document
        return protocol_document

    def get_generated_message(self, meeting):
        return _(u'Protocol for meeting ${title} has been generated '
                 'successfully',
                 mapping=dict(title=meeting.get_title()))

    def get_updated_message(self, meeting):
        return _(u'Protocol for meeting ${title} has been updated '
                 'successfully',
                 mapping=dict(title=meeting.get_title()))

    def get_title(self, meeting):
        return meeting.get_protocol_title()

    def get_filename(self, meeting):
        return meeting.get_protocol_filename()


class ExcerptOperations(PreProtocolOperations):

    def __init__(self, agenda_items):
        self.agenda_items = agenda_items

    def get_sablon_template(self, meeting):
        return meeting.get_excerpt_template()

    def get_meeting_data(self, meeting):
        return ExcerptProtocolData(meeting, self.agenda_items)

    def create_database_entry(self, meeting, document):
        excerpt = GeneratedExcerpt(
            oguid=Oguid.for_object(document),
            generated_version=document.get_current_version())

        for agenda_item in self.agenda_items:
            agenda_item.proposal.submitted_excerpt_document = excerpt

        return excerpt

    def get_generated_message(self, meeting):
        return _(u'Excerpt for meeting ${title} has been generated '
                 'successfully',
                 mapping=dict(title=meeting.get_title()))

    def get_updated_message(self, meeting):
        return _(u'Excerpt for meeting ${title} has been updated '
                 'successfully',
                 mapping=dict(title=meeting.get_title()))

    def get_title(self, meeting):
        return meeting.get_excerpt_title()

    def get_filename(self, meeting):
        return meeting.get_excerpt_filename()


class CreateGeneratedDocumentCommand(CreateDocumentCommand):

    def __init__(self, target_dossier, meeting, document_operations):
        """Data will be initialized lazily since it is only available after the
        document has been generated in `execute`.

        """
        self.meeting = meeting
        self.document_operations = document_operations

        super(CreateGeneratedDocumentCommand, self).__init__(
            target_dossier,
            self.document_operations.get_filename(self.meeting),
            data=None,
            title=self.document_operations.get_title(self.meeting),
            content_type=MIME_DOCX)

    def generate_file_data(self):
        template = self.document_operations.get_sablon_template(self.meeting)
        sablon = Sablon(template)
        sablon.process(self.document_operations.get_meeting_data(self.meeting).as_json())
        assert sablon.is_processed_successfully(), sablon.stderr
        return sablon.file_data

    def execute(self):
        self.data = self.generate_file_data()

        document = super(CreateGeneratedDocumentCommand, self).execute()
        self.add_database_entry(document)
        return document

    def add_database_entry(self, document):
        session = create_session()
        generated_document = self.document_operations.create_database_entry(
            self.meeting, document)
        if generated_document:
            session.add(generated_document)

    def show_message(self):
        portal = api.portal.get()
        api.portal.show_message(
            self.document_operations.get_generated_message(self.meeting),
            portal.REQUEST)


class ReplaceGeneratedDocumentCommand(CreateGeneratedDocumentCommand):

    def __init__(self, generated_document, document_operations):
        meeting = generated_document.meeting
        document = generated_document.resolve_document()
        dossier = aq_parent(aq_inner(document))
        super(ReplaceGeneratedDocumentCommand, self).__init__(
            dossier, meeting, document_operations)

        self.generated_document = generated_document

    def add_database_entry(self, document):
        self.generated_document.oguid = Oguid.for_object(document)
        self.generated_document.generated_version = document.get_current_version()


class UpdateGeneratedDocumentCommand(object):

    def __init__(self, generated_document, document_operations):
        self.generated_document = generated_document
        self.meeting = generated_document.meeting
        self.document_operations = document_operations

    def generate_file_data(self):
        template = self.document_operations.get_sablon_template(self.meeting)
        sablon = Sablon(template)
        sablon.process(
            self.document_operations.get_meeting_data(self.meeting).as_json())

        assert sablon.is_processed_successfully(), sablon.stderr
        return sablon.file_data

    def execute(self):
        document = Oguid.resolve_object(self.generated_document.oguid)
        document.file.data = self.generate_file_data()

        repository = api.portal.get_tool('portal_repository')
        comment = _(u'Updated with a newer generated version from meeting '
                    '${title}.',
                    mapping=dict(title=self.meeting.get_title()))
        repository.save(obj=document, comment=comment)

        new_version = document.get_current_version()
        self.generated_document.generated_version = new_version

        return document

    def show_message(self):
        portal = api.portal.get()
        api.portal.show_message(
            self.document_operations.get_updated_message(self.meeting),
            portal.REQUEST)


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


class GenerateExcerptsCommand(object):

    def __init__(self, meeting):
        self.meeting = meeting

    def execute(self):
        for agenda_item in self.meeting.agenda_items:
            if agenda_item.has_proposal():
                self.generate_excerpt(agenda_item)

    def generate_excerpt(self, agenda_item):
        proposal_obj = agenda_item.proposal.submitted_oguid.resolve_object()
        operations = ExcerptOperations([agenda_item])

        CreateGeneratedDocumentCommand(
            proposal_obj, self.meeting, operations).execute()


class DecideProposalsCommand(object):

    def __init__(self, meeting):
        self.meeting = meeting

    def execute(self):
        for agenda_item in self.meeting.agenda_items:
            if not agenda_item.has_proposal():
                continue

            self.decide_proposals(agenda_item.proposal)

    def decide_proposals(self, proposal):
        response = self.copy_document(proposal)
        self.add_database_entry(proposal, response)

    def add_database_entry(self, proposal, response):
        session = create_session()
        version = proposal.submitted_excerpt_document.generated_version

        excerpt = GeneratedExcerpt(
            admin_unit_id=proposal.admin_unit_id,
            int_id=response['intid'],
            generated_version=version)
        session.add(excerpt)

        proposal.excerpt_document = excerpt

    def copy_document(self, proposal):
        document = proposal.submitted_excerpt_document.oguid.resolve_object()
        return OgCopyCommand(
            document, proposal.admin_unit_id, proposal.physical_path).execute()


class CloseMeeting(object):

    def __init__(self, meeting):
        self.meeting = meeting

    def execute(self):
        GenerateExcerptsCommand(self.meeting).execute()
        DecideProposalsCommand(self.meeting).execute()
