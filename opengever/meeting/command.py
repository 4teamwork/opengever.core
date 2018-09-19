from DateTime import DateTime
from opengever.base import advancedjson
from opengever.base.command import CreateDocumentCommand
from opengever.base.interfaces import IDataCollector
from opengever.base.model import create_session
from opengever.base.oguid import Oguid
from opengever.base.request import dispatch_json_request
from opengever.base.request import dispatch_request
from opengever.base.transport import REQUEST_KEY
from opengever.base.transport import Transporter
from opengever.document.versioner import Versioner
from opengever.meeting import _
from opengever.meeting.activity.activities import ProposalDocumentSubmittedActivity
from opengever.meeting.activity.activities import ProposalDocumentUpdatedActivity
from opengever.meeting.exceptions import AgendaItemListAlreadyGenerated
from opengever.meeting.exceptions import AgendaItemListMissingTemplate
from opengever.meeting.exceptions import MissingProtocolHeaderTemplate
from opengever.meeting.exceptions import ProtocolAlreadyGenerated
from opengever.meeting.interfaces import IHistory
from opengever.meeting.mergetool import DocxMergeTool
from opengever.meeting.model.generateddocument import GeneratedAgendaItemList
from opengever.meeting.model.generateddocument import GeneratedProtocol
from opengever.meeting.model.submitteddocument import SubmittedDocument
from opengever.meeting.protocol import AgendaItemListProtocolData
from opengever.meeting.protocol import ExcerptProtocolData
from opengever.meeting.protocol import ProtocolData
from opengever.meeting.sablon import Sablon
from opengever.ogds.base.utils import decode_for_json
from plone import api
from plone.memoize import instance
from zope.component import getMultiAdapter
from zope.globalrequest import getRequest
from zope.i18n import translate
import base64
import json


MIME_DOCX = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'


class MergeDocxExcerptCommand(CreateDocumentCommand):
    """Create or update a merged excerpt word file.

    If an excerpt header is available it is considered the master document.
    If not, the agenda item`s file is considered the master document.
    """
    def __init__(self, context, agenda_item, filename, title):
        self.agenda_item = agenda_item
        self.excerpt_protocol_data = ExcerptProtocolData(
            self.agenda_item.meeting,
            [self.agenda_item])
        self.filename = filename
        super(MergeDocxExcerptCommand, self).__init__(
            context=context,
            filename=filename,
            data=None,
            title=title)

    def generate_file_data(self):
        header_template = self.agenda_item.get_excerpt_header_template()
        suffix_template = self.agenda_item.get_excerpt_suffix_template()
        agenda_item_document = self.agenda_item.resolve_document()

        has_header_template = header_template is not None

        if has_header_template and suffix_template is None:
            return agenda_item_document.file.data

        if has_header_template:
            sablon = self.get_sablon(template=header_template)
            master_data = sablon.file_data
        else:
            master_data = agenda_item_document.file.data

        with DocxMergeTool(master_data,
                           remove_property_fields=False) as merge_tool:
            if has_header_template:
                merge_tool.add(agenda_item_document.file.data)

            if suffix_template is not None:
                sablon = self.get_sablon(template=suffix_template)
                merge_tool.add(sablon.file_data)

            return merge_tool()

    def get_sablon(self, template):
        return Sablon(template).process(self.excerpt_protocol_data.as_json())

    def execute(self):
        self.set_file(
            self.filename,
            self.generate_file_data(),
            MIME_DOCX,
        )
        return super(MergeDocxExcerptCommand, self).execute()


class ProtocolOperations(object):
    """Protocol generation workflow."""

    def get_meeting_data(self, meeting):
        return ProtocolData(meeting)

    def create_database_entry(self, meeting, document):
        if meeting.protocol_document is not None:
            raise ProtocolAlreadyGenerated()
        version = document.get_current_version_id(missing_as_zero=True)
        protocol_document = GeneratedProtocol(
            oguid=Oguid.for_object(document), generated_version=version)
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

    def get_not_updated_message(self, meeting):
        return _(u'Protocol for meeting ${title} has not been updated. '
                 'The protocol has been modified manually and these modifications '
                 'will be lost if you regenerate the protocol.',
                 mapping=dict(title=meeting.get_title()))

    def get_title(self, meeting):
        return meeting.get_protocol_title()

    def get_filename(self, meeting):
        return meeting.get_protocol_filename()


class AgendaItemListOperations(object):
    """Agenda item list generation workflow."""

    def get_sablon_template(self, meeting):
        template = meeting.get_agendaitem_list_template()

        if template:
            return template

        raise AgendaItemListMissingTemplate

    def get_meeting_data(self, meeting):
        return AgendaItemListProtocolData(meeting)

    def get_title(self, meeting):
        return meeting.get_agendaitem_list_title()

    def get_filename(self, meeting):
        return meeting.get_agendaitem_list_filename()

    def create_database_entry(self, meeting, document):
        if meeting.agendaitem_list_document is not None:
            raise AgendaItemListAlreadyGenerated()

        version = document.get_current_version_id(missing_as_zero=True)
        agendaitem_list_document = GeneratedAgendaItemList(
            oguid=Oguid.for_object(document), generated_version=version)

        meeting.agendaitem_list_document = agendaitem_list_document

        return agendaitem_list_document

    def get_generated_message(self, meeting):
        return _(u'Agenda item list for meeting ${title} has been generated '
                 'successfully.',
                 mapping=dict(title=meeting.get_title()))

    def get_updated_message(self, meeting):
        return _(u'Agenda item list for meeting ${title} has been updated '
                 'successfully.',
                 mapping=dict(title=meeting.get_title()))


class CreateGeneratedDocumentCommand(CreateDocumentCommand):
    """Document generation workflow."""

    def __init__(self, context, meeting, document_operations):
        """Data will be initialized lazily since it is only available after the
        document has been generated in `execute`.

        """
        self.meeting = meeting
        self.document_operations = document_operations

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
        self.add_database_entry(document)
        return document

    def add_database_entry(self, document):
        session = create_session()
        generated_document = self.document_operations.create_database_entry(
            self.meeting, document)
        if generated_document:
            session.add(generated_document)

    def show_message(self):
        api.portal.show_message(
            self.document_operations.get_generated_message(self.meeting),
            self.context.REQUEST)


class MergeDocxProtocolCommand(CreateGeneratedDocumentCommand):
    """Create or update a merged protocol word file.

    Create a master file based on a sablon template (the master contains
    the first page with participants and agenda item list.)

    Then append all partial protocols for each agenda item in sequential order.
    """

    def __init__(self, context, meeting, document_operations):
        super(MergeDocxProtocolCommand, self).__init__(
            context, meeting, document_operations)

        self.has_protocol = meeting.protocol_document is not None
        self.protocol_updated = False

    def execute(self, overwrite=False):
        if self.has_protocol:
            return self.update_protocol_document(overwrite)

        return super(MergeDocxProtocolCommand, self).execute()

    def show_message(self):
        if not self.has_protocol:
            return super(MergeDocxProtocolCommand, self).show_message()

        if self.protocol_updated:
            api.portal.show_message(
                self.document_operations.get_updated_message(self.meeting),
                self.context.REQUEST)
        else:
            api.portal.show_message(
                self.document_operations.get_not_updated_message(self.meeting),
                self.context.REQUEST)

    def update_protocol_document(self, overwrite=False):
        if self.meeting.was_protocol_manually_edited() and not overwrite:
            return

        document = self.meeting.protocol_document.resolve_document()
        document.update_file(self.generate_file_data())

        comment = translate(
            _(u'Updated with a newer generated version from meeting ${title}.',
              mapping=dict(title=self.meeting.get_title())),
            context=getRequest())

        Versioner(document).create_version(comment)
        new_version = document.get_current_version_id()
        self.meeting.protocol_document.generated_version = new_version
        document.setModificationDate(DateTime())
        document.reindexObject(idxs=['modified'])
        self.protocol_updated = True
        return document

    def generate_file_data(self):
        master = self.get_header_sablon()
        with DocxMergeTool(master.file_data) as merge_tool:
            for agenda_item in self.meeting.agenda_items:
                if agenda_item.is_paragraph:
                    sablon = self.get_sablon_for_paragraph(agenda_item)
                    if sablon is not None:
                        merge_tool.add(sablon.file_data)

                elif agenda_item.has_document:
                    sablon = self.get_agenda_item_header_sablon(agenda_item)
                    if sablon is not None:
                        merge_tool.add(sablon.file_data)

                    document = agenda_item.resolve_document()
                    merge_tool.add(document.file.data)

                    sablon = self.get_agenda_item_suffix_sablon(agenda_item)
                    if sablon is not None:
                        merge_tool.add(sablon.file_data)

            if self.meeting.get_protocol_suffix_template():
                sablon = self.get_suffix_sablon()
                merge_tool.add(sablon.file_data)

            return merge_tool()

    def get_header_sablon(self):
        template = self.meeting.get_protocol_header_template()
        if template is None:
            raise MissingProtocolHeaderTemplate()
        return Sablon(template).process(
            self.document_operations.get_meeting_data(self.meeting).as_json())

    def get_suffix_sablon(self):
        return Sablon(self.meeting.get_protocol_suffix_template()).process(
            self.document_operations.get_meeting_data(self.meeting).as_json())

    def get_agenda_item_header_sablon(self, agenda_item):
        template = self.meeting.get_agenda_item_header_template()
        if template is None:
            return
        return Sablon(template).process(
            ProtocolData(self.meeting, [agenda_item]).as_json())

    def get_agenda_item_suffix_sablon(self, agenda_item):
        template = self.meeting.get_agenda_item_suffix_template()
        if template is None:
            return
        return Sablon(template).process(
            ProtocolData(self.meeting, [agenda_item]).as_json())

    def get_sablon_for_paragraph(self, agenda_item):
        template = self._get_paragraph_template()
        if template is None:
            return

        return Sablon(self._get_paragraph_template()).process(
            ProtocolData(self.meeting, [agenda_item]).as_json())

    @instance.memoize
    def _get_paragraph_template(self):
        committee = self.meeting.committee.resolve_committee()
        return committee.get_paragraph_template()


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
        document.update_file(self.generate_file_data())

        comment = translate(
            _(u'Updated with a newer generated version from meeting ${title}.',
              mapping=dict(title=self.meeting.get_title())),
            context=getRequest())

        Versioner(document).create_version(comment)
        new_version = document.get_current_version_id()
        self.generated_document.generated_version = new_version
        document.setModificationDate(DateTime())
        document.reindexObject(idxs=['modified'])

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
        # XXX handle errors when executing across admin units.
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

    def execute(self, text=None):
        model = self.proposal.load_model()
        jsondata = {'committee_oguid': model.committee.oguid.id,
                    'proposal_oguid': model.oguid.id}

        # XXX use Transporter or API?
        collector = getMultiAdapter((self.proposal,), IDataCollector,
                                    name='field-data')
        jsondata['field-data'] = collector.extract()

        document = self.proposal.get_proposal_document()
        jsondata['title'] = document.title_or_id()

        blob = document.file
        jsondata['file'] = {
            'filename': blob.filename,
            'contentType': blob.contentType,
            'data': base64.encodestring(blob.data)}

        record = IHistory(self.proposal).append_record(u'submitted', text=text)
        history_data = advancedjson.dumps({'uuid': record.uuid, 'text': text})

        request_data = {
            REQUEST_KEY: json.dumps(decode_for_json(jsondata)),
            'history_data': history_data,
        }

        response = dispatch_json_request(self.admin_unit_id, '@@create_submitted_proposal', data=request_data)
        self.submitted_proposal_path = response['path']


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
                    response_body))


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
        submitted_version = self.document.get_current_version_id()

        record = IHistory(self.proposal).append_record(
            u'document_updated',
            document_title=self.document.title,
            submitted_version=submitted_version,
        )
        history_data = advancedjson.dumps({
            'submitted_version': submitted_version,
            'uuid': record.uuid,
            })

        ProposalDocumentUpdatedActivity(
            self.proposal, self.proposal.REQUEST,
            self.document.title, submitted_version).record()

        Transporter().transport_to(
            self.document,
            self.submitted_document.submitted_admin_unit_id,
            self.submitted_document.submitted_physical_path,
            view='update-submitted-document',
            history_data=history_data)

        submitted_document = SubmittedDocument.query.get_by_source(
            self.proposal, self.document)
        submitted_document.submitted_version = submitted_version

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
                 target_path=None, target_admin_unit_id=None,
                 record_activity=True):
        self.proposal = proposal
        self.document = document
        self._parent_action = parent_action
        self._target_path = target_path
        self._target_admin_unit_id = target_admin_unit_id
        self.record_activity = record_activity

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
        submitted_version = self.document.get_current_version_id(
            missing_as_zero=True)

        doc = SubmittedDocument(oguid=oguid,
                                proposal=proposal_model,
                                submitted_admin_unit_id=target_admin_unit_id,
                                submitted_int_id=reponse['intid'],
                                submitted_physical_path=reponse['path'],
                                submitted_version=submitted_version)
        session.add(doc)

    def copy_document(self, target_path, target_admin_unit_id):
        submitted_version = self.document.get_current_version_id(
            missing_as_zero=True)

        record = IHistory(self.proposal).append_record(
            u'document_submitted',
            document_title=self.document.title,
            submitted_version=submitted_version,
        )

        if self.record_activity:
            ProposalDocumentSubmittedActivity(
                self.proposal, self.proposal.REQUEST, self.document.title).record()

        history_data = advancedjson.dumps({
            'submitted_version': submitted_version,
            'uuid': record.uuid,
            })

        activity = advancedjson.dumps({
            'record_activity': self.record_activity,
            })

        return SubmitDocumentCommand(
            self.document, target_admin_unit_id, target_path,
            history_data=history_data,
            activity=activity).execute()


class OgCopyCommand(object):

    def __init__(self, source, target_admin_unit_id, target_path, **kwargs):
        self.source = source
        self.target_path = target_path
        self.target_admin_unit_id = target_admin_unit_id
        self.kwargs = kwargs

    def execute(self):
        return Transporter().transport_to(
            self.source, self.target_admin_unit_id, self.target_path,
            **self.kwargs)


class SubmitDocumentCommand(OgCopyCommand):

    def execute(self):
        return Transporter().transport_to(
            self.source, self.target_admin_unit_id, self.target_path,
            view='recieve-submitted-document', **self.kwargs)


class CreateExcerptCommand(OgCopyCommand):

    def execute(self):
        return Transporter().transport_to(
            self.source, self.target_admin_unit_id, self.target_path,
            view='recieve-excerpt-document', **self.kwargs)
