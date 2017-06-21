from opengever.base.command import CreateDocumentCommand
from opengever.base.interfaces import IDataCollector
from opengever.base.model import create_session
from opengever.base.oguid import Oguid
from opengever.base.request import dispatch_json_request
from opengever.base.request import dispatch_request
from opengever.base.transport import REQUEST_KEY
from opengever.base.transport import Transporter
from opengever.locking.lock import SYS_LOCK
from opengever.meeting import _
from opengever.meeting import is_word_meeting_implementation_enabled
from opengever.meeting.exceptions import ProtocolAlreadyGenerated
from opengever.meeting.interfaces import IHistory
from opengever.meeting.model.generateddocument import GeneratedExcerpt
from opengever.meeting.model.generateddocument import GeneratedProtocol
from opengever.meeting.model.proposalhistory import Submitted, DocumentUpdated, DocumentSubmitted
from opengever.meeting.model.submitteddocument import SubmittedDocument
from opengever.meeting.protocol import AgendaItemListProtocolData
from opengever.meeting.protocol import ExcerptProtocolData
from opengever.meeting.protocol import ProtocolData
from opengever.meeting.sablon import Sablon
from opengever.ogds.base.utils import decode_for_json
from plone import api
from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.locking.interfaces import ILockable
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.globalrequest import getRequest
from zope.i18n import translate
import base64
import json


MIME_DOCX = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'


class ProtocolOperations(object):

    def get_sablon_template(self, meeting):
        return meeting.get_protocol_template()

    def get_meeting_data(self, meeting):
        return ProtocolData(meeting)

    def create_database_entry(self, meeting, document):
        if meeting.protocol_document is not None:
            raise ProtocolAlreadyGenerated()
        protocol_document = GeneratedProtocol(
            oguid=Oguid.for_object(document),
            generated_version=document.get_current_version())
        meeting.protocol_document = protocol_document
        return protocol_document

    def get_generated_message(self, meeting):
        return _(u'Protocol for meeting ${title} has been generated '
                 'successfully.',
                 mapping=dict(title=meeting.get_title()))

    def get_updated_message(self, meeting):
        return _(u'Protocol for meeting ${title} has been updated '
                 'successfully.',
                 mapping=dict(title=meeting.get_title()))

    def get_title(self, meeting):
        return meeting.get_protocol_title()

    def get_filename(self, meeting):
        return meeting.get_protocol_filename()


class AgendaItemListOperations(object):

    def get_sablon_template(self, meeting):
        return meeting.get_agendaitem_list_template()

    def get_meeting_data(self, meeting):
        return AgendaItemListProtocolData(meeting)

    def get_title(self, meeting):
        return meeting.get_agendaitem_list_title()

    def get_filename(self, meeting):
        return meeting.get_agendaitem_list_filename()


class ExcerptOperations(object):

    def __init__(self, agenda_item):
        self.agenda_item = agenda_item
        self.proposal = agenda_item.proposal

    def get_sablon_template(self, meeting):
        return meeting.get_excerpt_template()

    def get_meeting_data(self, meeting):
        return ExcerptProtocolData(meeting, [self.agenda_item])

    def create_database_entry(self, meeting, document):
        excerpt = GeneratedExcerpt(
            oguid=Oguid.for_object(document),
            generated_version=document.get_current_version())

        self.proposal.submitted_excerpt_document = excerpt

        return excerpt

    def get_generated_message(self, meeting):
        return _(u'Excerpt for agenda item ${title} has been generated '
                 'successfully',
                 mapping=dict(title=meeting.get_title()))

    def get_updated_message(self, meeting):
        return _(u'Excerpt for agenda item ${title} has been updated '
                 'successfully',
                 mapping=dict(title=meeting.get_title()))

    def get_title(self, meeting):
        return u"{} - {}".format(
            self.proposal.resolve_submitted_proposal().title,
            meeting.get_title())

    def get_filename(self, meeting):
        normalizer = getUtility(IIDNormalizer)
        return u"{}-{}.docx".format(
            normalizer.normalize(
                self.proposal.resolve_submitted_proposal().title),
            normalizer.normalize(
                meeting.get_title()))


class ManualExcerptOperations(object):

    def __init__(self, agenda_items, title,
                 include_initial_position=True, include_legal_basis=True,
                 include_considerations=True, include_proposed_action=True,
                 include_discussion=True, include_decision=True,
                 include_publish_in=True, include_disclose_to=True,
                 include_copy_for_attention=True):
        self.agenda_items = agenda_items
        self.title = title
        self.include_initial_position = include_initial_position
        self.include_legal_basis = include_legal_basis
        self.include_considerations = include_considerations
        self.include_proposed_action = include_proposed_action
        self.include_discussion = include_discussion
        self.include_decision = include_decision
        self.include_publish_in = include_publish_in
        self.include_disclose_to = include_disclose_to
        self.include_copy_for_attention = include_copy_for_attention

    def get_sablon_template(self, meeting):
        return meeting.get_excerpt_template()

    def get_meeting_data(self, meeting):
        return ExcerptProtocolData(
            meeting, self.agenda_items,
            include_initial_position=self.include_initial_position,
            include_legal_basis=self.include_legal_basis,
            include_considerations=self.include_considerations,
            include_proposed_action=self.include_proposed_action,
            include_discussion=self.include_discussion,
            include_decision=self.include_decision,
            include_publish_in=self.include_publish_in,
            include_disclose_to=self.include_disclose_to,
            include_copy_for_attention=self.include_copy_for_attention)

    def create_database_entry(self, meeting, document):
        excerpt = GeneratedExcerpt(
            oguid=Oguid.for_object(document),
            generated_version=document.get_current_version())

        meeting.excerpt_documents.append(excerpt)
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
        return self.title

    def get_filename(self, meeting):
        normalizer = getUtility(IIDNormalizer)
        return u"{}.docx".format(normalizer.normalize(self.get_title(meeting)))


class CreateGeneratedDocumentCommand(CreateDocumentCommand):

    def __init__(self, context, meeting, document_operations,
                 lock_document_after_creation=False):
        """Data will be initialized lazily since it is only available after the
        document has been generated in `execute`.

        """
        self.meeting = meeting
        self.document_operations = document_operations
        self.lock_document_after_creation = lock_document_after_creation

        super(CreateGeneratedDocumentCommand, self).__init__(
            context, filename=None, data=None,
            title=self.document_operations.get_title(self.meeting))

    def generate_file_data(self):
        template = self.document_operations.get_sablon_template(self.meeting)
        sablon = Sablon(template)
        sablon.process(self.document_operations.get_meeting_data(self.meeting).as_json())
        assert sablon.is_processed_successfully(), sablon.stderr
        return sablon.file_data

    def execute(self):
        self.set_file(
            self.document_operations.get_filename(self.meeting),
            self.generate_file_data(),
            MIME_DOCX
            )

        document = super(CreateGeneratedDocumentCommand, self).execute()
        self.lock_document(document)
        self.add_database_entry(document)
        return document

    def lock_document(self, document):
        if not self.lock_document_after_creation:
            return

        ILockable(document).lock(SYS_LOCK)

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


class UpdateGeneratedDocumentCommand(object):

    def __init__(self, generated_document, meeting, document_operations):
        self.generated_document = generated_document
        self.meeting = meeting
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
        comment = translate(
            _(u'Updated with a newer generated version from meeting ${title}.',
              mapping=dict(title=self.meeting.get_title())),
            context=getRequest())
        repository.save(obj=document, comment=comment)

        new_version = document.get_current_version()
        self.generated_document.generated_version = new_version

        return document

    def show_message(self):
        portal = api.portal.get()
        api.portal.show_message(
            self.document_operations.get_updated_message(self.meeting),
            portal.REQUEST)


class UpdateExcerptInDossierCommand(object):
    """Update an excerpt that has already been stored in a dossier from an
    excerpt that is stored in a submitted proposal.

    """
    def __init__(self, proposal):
        self.proposal = proposal
        self.excerpt = proposal.excerpt_document
        self.submitted_excerpt = proposal.submitted_excerpt_document
        self.document = self.submitted_excerpt.resolve_document()

    def execute(self):
        #XXX handle errors when executing across admin units.
        Transporter().transport_to(
            self.document,
            self.excerpt.admin_unit_id,
            '',
            view='update-dossier-excerpt',
            oguid=self.excerpt.oguid.id)


class CreateSubmittedProposalCommand(object):

    def __init__(self, proposal):
        self.proposal = proposal
        self.submitted_proposal_path = None
        self.admin_unit_id = self.proposal.get_committee_admin_unit().id()

    def execute(self):
        model = self.proposal.load_model()
        jsondata = {'committee_oguid': model.committee.oguid.id,
                    'proposal_oguid': model.oguid.id}

        # XXX use Transporter or API?
        collector = getMultiAdapter((self.proposal,), IDataCollector,
                                    name='field-data')
        jsondata['field-data'] = collector.extract()

        if is_word_meeting_implementation_enabled():
            blob = self.proposal.get_proposal_document().file
            jsondata['file'] = {
                'filename': blob.filename,
                'contentType': blob.contentType,
                'data': base64.encodestring(blob.data)}

        request_data = {REQUEST_KEY: json.dumps(decode_for_json(jsondata))}
        response = dispatch_json_request(
            self.admin_unit_id, '@@create_submitted_proposal', data=request_data)

        self.submitted_proposal_path = response['path']
        IHistory(self.proposal).append_record('submitted')


class RejectProposalCommand(object):

    def __init__(self, submitted_proposal):
        self.submitted_proposal = submitted_proposal

    def execute(self):
        model = self.submitted_proposal.load_model()
        response = dispatch_request(
            model.admin_unit_id,
            '@@reject-proposal',
            path=model.physical_path)

        response_body = response.read()
        if response_body != 'OK':
            raise ValueError(
                'Unexpected response {!r} when rejecting proposal.'.format(
                    response))


class NullUpdateSubmittedDocumentCommand(object):

    def __init__(self, document):
        self.document = document

    def execute(self):
        pass

    def show_message(self):
        portal = api.portal.get()
        api.portal.show_message(
            _(u'Document ${title} has already been submitted in that version.',
              mapping=dict(title=self.document.title)),
            portal.REQUEST,
            type='warning')


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

        session.add(DocumentUpdated(
            proposal=proposal_model,
            submitted_document=submitted_document,
            submitted_version=submitted_version,
            document_title=self.document.title))

    def show_message(self):
        portal = api.portal.get()
        api.portal.show_message(
            _(u'A new submitted version of document ${title} has been created.',
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
        reponse = self.copy_document(
            self.target_path, self.target_admin_unit_id)
        self.add_database_entry(reponse, self.target_admin_unit_id)

    def show_message(self):
        portal = api.portal.get()
        api.portal.show_message(
            _(u'Additional document ${title} has been submitted successfully.',
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

        session.add(DocumentSubmitted(
            proposal=proposal_model,
            submitted_document=doc,
            submitted_version=submitted_version,
            document_title=self.document.title))

    def copy_document(self, target_path, target_admin_unit_id):
        return SubmitDocumentCommand(
            self.document, target_admin_unit_id, target_path).execute()


class OgCopyCommand(object):

    def __init__(self, source, target_admin_unit_id, target_path):
        self.source = source
        self.target_path = target_path
        self.target_admin_unit_id = target_admin_unit_id

    def execute(self):
        return Transporter().transport_to(
            self.source, self.target_admin_unit_id, self.target_path)


class SubmitDocumentCommand(OgCopyCommand):

    def execute(self):
        return Transporter().transport_to(
            self.source, self.target_admin_unit_id, self.target_path,
            view='recieve-submitted-document')


class CreateExcerptCommand(OgCopyCommand):

    def execute(self):
        return Transporter().transport_to(
            self.source, self.target_admin_unit_id, self.target_path,
            view='recieve-excerpt-document')
