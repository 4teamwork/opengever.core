# -*- coding: utf-8 -*-
from Acquisition import aq_parent
from DateTime import DateTime
from opengever.base.exceptions import InvalidOguidIntIdPart
from opengever.exportng.utils import Attribute
from opengever.exportng.utils import garbage_collect
from opengever.exportng.utils import timer
from opengever.exportng.utils import userid_to_email
from opengever.meeting.model import AgendaItem
from opengever.meeting.model import Committee
from opengever.meeting.model import Meeting
from opengever.meeting.model import Membership
from opengever.meeting.model import Proposal
from opengever.ogds.models.group import Group
from opengever.ogds.models.user import User
from plone.app.uuid.utils import uuidToObject
from sqlalchemy.sql.expression import false
from zope.component.hooks import getSite

import logging

logger = logging.getLogger('opengever.exportng')


class OGDSItemSerializer(object):

    mapping = []
    additional_mappings = {}

    def __init__(self, item):
        self.item = item

    def data(self):
        data = {}
        for attr in self.mapping:
            getter = getattr(self, attr.name, None)
            if getter is not None:
                value = getter()
            else:
                value = getattr(self.item, attr.name)
            data[attr.col_name] = value
        return data


class OGDSSyncer(object):

    filter = None

    def __init__(self, engine, metadata):
        self.engine = engine
        self.metadata = metadata
        self.site = getSite()

    def get_sql_items(self):
        table = self.metadata.tables[self.table]
        stmt = table.select().where(table.c._deleted == false())
        with self.engine.connect() as conn:
            return conn.execute(stmt).fetchall()

    def get_ogds_items(self):
        distinct_attr = getattr(self.model, self.key)
        query = self.model.query
        if self.filter is not None:
            query = query.filter(self.filter)
        return query.distinct(distinct_attr).all()

    def truncate(self):
        with self.engine.begin() as conn:
            conn.execution_options(autocommit=True).execute(
                "TRUNCATE TABLE {}".format(self.table))

    def sync(self):
        self.truncate()

        total_time = timer()
        lap_time = timer()
        counter = 0

        inserts = []
        additional_inserts = {}
        ogds_items = self.get_ogds_items()
        ogds_items_len = len(ogds_items)
        logger.info('Exporting %s %s...', ogds_items_len, self.table)
        for item in self.get_ogds_items():
            serializer = self.serializer(item)
            inserts.append(serializer.data())
            for tablename in self.serializer.additional_mappings.keys():
                additional_data = serializer.additional_data(tablename)
                if additional_data:
                    additional_inserts.setdefault(tablename, []).extend(
                        additional_data)

            counter += 1
            if counter % 100 == 0:
                logger.info(
                    '%d of %d items processed (%.2f %%), last batch in %s',
                    counter, ogds_items_len, 100 * float(counter) / ogds_items_len, next(lap_time),
                )
                garbage_collect(self.site)
        logger.info('Processed %d items in %s.', counter, next(total_time))

        table = self.metadata.tables[self.table]
        with self.engine.connect() as conn:
            conn.execute(table.insert(), inserts)
            logger.info('Added %s: %s', table, len(inserts))
            for tablename, ainserts in additional_inserts.items():
                atable = self.metadata.tables[tablename]
                conn.execute(atable.insert(), ainserts)
                logger.info('Added %s: %s', atable, len(ainserts))


class UserSerializer(OGDSItemSerializer):

    mapping = [
        Attribute('email', 'email', 'varchar'),
        Attribute('firstname', 'firstname', 'varchar'),
        Attribute('lastname', 'lastname', 'varchar'),
        Attribute('active', 'active', 'boolean'),
    ]


class UserSyncer(OGDSSyncer):

    table = 'users'
    model = User
    key = 'email'
    serializer = UserSerializer


class GroupSerializer(OGDSItemSerializer):

    mapping = [
        Attribute('groupname', 'groupname', 'varchar'),
        Attribute('title', 'title', 'varchar'),
        Attribute('active', 'active', 'boolean'),
    ]


class GroupSyncer(OGDSSyncer):

    table = 'groups'
    model = Group
    key = 'groupname'
    serializer = GroupSerializer


class CommitteeSerializer(OGDSItemSerializer):

    mapping = [
        Attribute('committee_uid', 'objexternalkey', 'varchar'),
        Attribute('title', 'objname', 'varchar'),
        Attribute('workflow_state', 'cdeactivated', 'boolean'),
        Attribute('committee_dossier_location', 'cmeetingdossierlocation', 'varchar'),
        Attribute('protocoltype', 'cprotocoltype', 'varchar'),
        Attribute('objsecsecurity', 'objsecsecurity', 'jsonb'),
        Attribute('objsecchange', 'objsecchange', 'jsonb'),
        Attribute('objsecread', 'objsecread', 'jsonb'),
    ]

    def committee_uid(self):
        return self.item.resolve_committee().UID()

    def workflow_state(self):
        return self.item.workflow_state != 'active'

    def committee_dossier_location(self):
        return self.item.resolve_committee().get_repository_folder().UID()

    def protocoltype(self):
        return 'WORD'

    def objsecsecurity(self):
        members = self.item.get_active_members()
        return [member.email for member in members]

    def objsecchange(self):
        return []

    def objsecread(self):
        return []


class CommitteeSyncer(OGDSSyncer):

    table = 'committees'
    model = Committee
    key = 'committee_id'
    serializer = CommitteeSerializer


class CommitteeMemberSerializer(OGDSItemSerializer):

    mapping = [
        Attribute('committee_uid', 'committee', 'varchar'),
        Attribute('member_id', 'participant', 'varchar'),
        Attribute('role', 'role', 'varchar'),
        # Attribute('date_from'),
        # Attribute('date_to'),
    ]

    def committee_uid(self):
        return self.item.committee.resolve_committee().UID()

    def member_id(self):
        return self.item.member.email


class CommitteeMemberSyncer(OGDSSyncer):

    table = 'committee_participants'
    model = Membership
    key = 'committee_id'
    serializer = CommitteeMemberSerializer

    def get_ogds_items(self):
        return self.model.query.all()


class MeetingSerializer(OGDSItemSerializer):

    # mlink (video call link)
    mapping = [
        Attribute('meeting_id', 'objexternalkey', 'varchar'),
        Attribute('title', 'objsubject', 'varchar'),
        Attribute('start', 'mbegin', 'datetime'),
        Attribute('end', 'mend', 'datetime'),
        Attribute('location', 'mlocation', 'varchar'),
        Attribute('committee_uid', 'mcommittee', 'varchar'),
        Attribute('dossier_uid', 'mdossier', 'varchar'),
        Attribute('timezone', 'mtimezone', 'varchar'),
        Attribute('workflow_state', 'mmeetingstate', 'varchar'),
        Attribute('objsecsecurity', 'objsecsecurity', 'jsonb'),
        Attribute('objsecchange', 'objsecchange', 'jsonb'),
        Attribute('objsecread', 'objsecread', 'jsonb'),
    ]

    def start(self):
        return DateTime(self.item.get_start()).asdatetime()

    def end(self):
        if self.item.end:
            return DateTime(self.item.get_end()).asdatetime()

    def meeting_id(self):
        return 'meeting-{}'.format(self.item.meeting_id)

    def timezone(self):
        return 'Europe/Zurich'

    def dossier_uid(self):
        if self.item.workflow_state == 'closed':
            try:
                dossier = self.item.dossier_oguid.resolve_object()
            except InvalidOguidIntIdPart:
                logger.warning('Could not resolve dossier for meeting.')
                return None
            return dossier.UID()

    def committee_uid(self):
        return self.item.committee.resolve_committee().UID()

    def workflow_state(self):
        state_mapping = {
            'pending': 'IN_PREPARATION',
            'held': 'COMPLETED',
            'closed': 'CLOSED',
        }
        return state_mapping.get(self.item.workflow_state)

    def objsecsecurity(self):
        return []

    def objsecchange(self):
        return []

    def objsecread(self):
        return []


class MeetingSyncer(OGDSSyncer):

    table = 'meetings'
    filter = Meeting.workflow_state != 'cancelled'
    model = Meeting
    key = 'meeting_id'
    serializer = MeetingSerializer


class MeetingParticipantsSerializer(OGDSItemSerializer):

    mapping = [
        Attribute('meeting_id', 'meeting', 'varchar'),
        Attribute('participant', 'participant', 'varchar'),
        Attribute('role', 'role', 'varchar'),
    ]

    def data(self):
        meeting_id = 'meeting-{}'.format(self.item.meeting_id)
        participants = []
        for participant in self.item.participants:
            role = None
            if participant == self.item.presidency:
                role = 'Vorsitz'
            elif participant == self.item.secretary:
                role = 'Protokollführung'
            participants.append({
                'meeting': meeting_id,
                'participant': participant.email,
                'role': role,
            })
        return participants


class MeetingParticipantsSyncer(OGDSSyncer):

    table = 'meeting_participants'
    model = Meeting
    key = 'meeting_id'
    serializer = MeetingParticipantsSerializer

    def sync(self):
        self.truncate()
        inserts = []
        for item in self.get_ogds_items():
            serializer = self.serializer(item)
            inserts += serializer.data()

        table = self.metadata.tables[self.table]
        with self.engine.connect() as conn:
            conn.execute(table.insert(), inserts)
        logger.info('Added %s: %s', table, len(inserts))


class AgendaItemSerializer(OGDSItemSerializer):

    mapping = [
        Attribute('agendaitem_id', 'objexternalkey', 'varchar'),
        Attribute('meeting_id', 'objprimaryrelated', 'varchar'),
        Attribute('title', 'objsubject', 'varchar'),
        Attribute('workflow_state', 'aistate', 'varchar'),
        Attribute('proposal_uid', 'aiproposal', 'varchar'),
        Attribute('dossier_uid', 'mdossier', 'varchar'),
        Attribute('sort_order', '_sort_key', 'integer'),
        Attribute('is_paragraph', '_is_subheading', 'boolean'),
    ]

    additional_mappings = {
        'agendaitem_links': {
            Attribute('id', 'id', 'integer'),
            Attribute('agendaitem_id', 'agendaitem', 'varchar'),
            Attribute('excerpt_uid', 'document', 'varchar'),
            Attribute('attributedefinitiontarget', 'attributedefinitiontarget', 'varchar'),
        },
    }

    def agendaitem_id(self):
        return 'agendaitem-{}'.format(self.item.agenda_item_id)

    def meeting_id(self):
        return 'meeting-{}'.format(self.item.meeting.meeting_id)

    def title(self):
        return self.item.get_title()

    def proposal_uid(self):
        if self.item.has_proposal:
            proposal = (
                self.item.proposal.resolve_submitted_proposal()
                or self.item.proposal.resolve_proposal()
            )
            return proposal.UID()

    def dossier_uid(self):
        if self.item.meeting.workflow_state == 'closed' and self.item.has_proposal:
            excerpt = self.item.proposal.resolve_submitted_excerpt_document()
            if excerpt:
                return aq_parent(excerpt).UID()

    def excerpt_uid(self):
        if self.item.meeting.workflow_state == 'closed' and self.item.has_proposal:
            excerpt = self.item.proposal.resolve_submitted_excerpt_document()
            if excerpt:
                return excerpt.UID()

    def workflow_state(self):
        state_mapping = {
            'pending': 'OPEN',
            'decided': 'DONE',
            'revision': 'DONE',
        }
        return state_mapping.get(self.item.workflow_state)

    def additional_data(self, name):
        excerpt_uid = self.excerpt_uid()
        if excerpt_uid:
            return [{
                'id': self.item.agenda_item_id,
                'agendaitem': self.agendaitem_id(),
                'document': self.excerpt_uid(),
                'attributedefinitiontarget': 'aiprotocolword',
            }]


class AgendaItemSyncer(OGDSSyncer):

    table = 'agendaitems'
    model = AgendaItem
    key = 'agenda_item_id'
    serializer = AgendaItemSerializer


class ProposalSerializer(OGDSItemSerializer):

    # objcreatedat, objmodifiedat?
    mapping = [
        Attribute('proposal_uid', 'objexternalkey', 'varchar'),
        Attribute('committee_uid', 'pcommittee', 'varchar'),
        Attribute('title', 'objname', 'varchar'),
        Attribute('workflow_state', 'pstate', 'varchar'),
        Attribute('issuer', 'objcreatedby', 'varchar'),
        Attribute('creator', 'pproposedby', 'varchar'),
        Attribute('dossier_uid', 'poriginaldossier', 'varchar'),
        Attribute('agendaitem_id', 'pagendaitem', 'varchar'),
    ]

    additional_mappings = {
        'proposal_links': {
            Attribute('id', 'id', 'integer'),
            Attribute('proposal_id', 'proposal', 'varchar'),
            Attribute('document', 'document', 'varchar'),
            Attribute('attributedefinitiontarget', 'attributedefinitiontarget', 'varchar'),
        },
    }

    def __init__(self, item):
        super(ProposalSerializer, self).__init__(item)
        self.proposal = item.resolve_submitted_proposal() or item.resolve_proposal()

    def proposal_uid(self):
        return self.proposal.UID()

    def committee_uid(self):
        return self.item.committee.resolve_committee().UID()

    def issuer(self):
        return userid_to_email(self.item.issuer)

    def dossier_uid(self):
        return self.proposal.get_containing_dossier().UID()

    def creator(self):
        return userid_to_email(self.proposal.Creator())

    def agendaitem_id(self):
        if self.item.agenda_item is not None:
            return "agendaitem-{}".format(self.item.agenda_item.agenda_item_id)

    def workflow_state(self):
        state_mapping = {
            'scheduled': 'REGISTERED',
            'pending': 'IN_PREPARATION',
            'submitted': 'SUBMITTED',
            'decided': 'DECIDED',
            'cancelled': 'DISCARDED',
        }
        return state_mapping.get(self.item.workflow_state)

    def document(self):
        if self.proposal._proposal_document_uuid:
            document = uuidToObject(self.proposal._proposal_document_uuid)
            if document:
                return document.UID()
        # return self.proposal.get_proposal_document().UID()

    def attachments(self):
        return [doc.UID() for doc in self.proposal.get_documents()]

    def additional_data(self, name):
        links = []
        document = self.document()
        if document:
            links.append({
                'proposal': self.proposal_uid(),
                'document': document,
                'attributedefinitiontarget': 'pproposaldocument',
            })
            links.append({
                'proposal': self.proposal_uid(),
                'document': document,
                'attributedefinitiontarget': 'poriginaldocument',
            })
        for attachment in self.attachments():
            links.append({
                'proposal': self.proposal_uid(),
                'document': attachment,
                'attributedefinitiontarget': 'pdocuments',
            })
        return links


class ProposalSyncer(OGDSSyncer):

    table = 'proposals'
    model = Proposal
    key = 'proposal_id'
    serializer = ProposalSerializer
