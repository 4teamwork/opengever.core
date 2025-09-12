# -*- coding: utf-8 -*-
from Acquisition import aq_parent
from opengever.base.exceptions import InvalidOguidIntIdPart
from opengever.exportng.utils import Attribute
from opengever.exportng.utils import userid_to_email
from opengever.meeting.model import AgendaItem
from opengever.meeting.model import Committee
from opengever.meeting.model import Meeting
from opengever.meeting.model import Membership
from opengever.meeting.model import Proposal
from opengever.ogds.models.group import Group
from opengever.ogds.models.user import User
from sqlalchemy.sql.expression import false
import logging

logger = logging.getLogger('opengever.exportng')


class OGDSItemSerializer(object):

    mapping = {}

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

    def __init__(self, engine, metadata):
        self.engine = engine
        self.metadata = metadata

    def get_sql_items(self):
        table = self.metadata.tables[self.table]
        stmt = table.select().where(table.c._deleted == false())
        with self.engine.connect() as conn:
            return conn.execute(stmt).fetchall()

    def get_ogds_items(self):
        distinct_attr = getattr(self.model, self.key)
        return self.model.query.distinct(distinct_attr).all()

    def truncate(self):
        with self.engine.begin() as conn:
            conn.execution_options(autocommit=True).execute(
                "TRUNCATE TABLE {}".format(self.table))

    def sync(self):
        self.truncate()
        inserts = []
        for item in self.get_ogds_items():
            serializer = self.serializer(item)
            inserts.append(serializer.data())

        table = self.metadata.tables[self.table]
        with self.engine.connect() as conn:
            conn.execute(table.insert(), inserts)
        logger.info('Added %s: %s', table, len(inserts))


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
        return []

    def objsecchange(self):
        members = self.item.get_active_members()
        return [member.email for member in members]

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

    def meeting_id(self):
        return 'meeting-{}'.format(self.item.meeting_id)

    def timezone(self):
        return 'Europe/Zurich'

    def dossier_uid(self):
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
            'held': 'IN_PROGRESS',
            'closed': 'COMPLETED',
            'cancelled': 'CLOSED',
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
    ]

    def agendaitem_id(self):
        return 'agendaitem-{}'.format(self.item.agenda_item_id)

    def meeting_id(self):
        return 'meeting-{}'.format(self.item.meeting.meeting_id)

    def title(self):
        return self.item.get_title()

    def proposal_uid(self):
        if self.item.has_proposal:
            return self.item.proposal.resolve_proposal().UID()

    def dossier_uid(self):
        if self.item.has_proposal:
            return aq_parent(self.item.proposal.resolve_proposal()).UID()

    def workflow_state(self):
        state_mapping = {
            'pending': 'OPEN',
            'decided': 'DONE',
        }
        return state_mapping.get(self.item.workflow_state)


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
        Attribute('creator', 'objcreatedby', 'varchar'),
        Attribute('issuer', 'pproposedby', 'varchar'),
        Attribute('dossier_uid', 'poriginaldossier', 'varchar'),
        Attribute('agendaitem_id', 'pagendaitem', 'varchar'),
    ]

    def __init__(self, item):
        super(ProposalSerializer, self).__init__(item)
        self.proposal = item.resolve_proposal()

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


class ProposalSyncer(OGDSSyncer):

    table = 'proposals'
    model = Proposal
    key = 'proposal_id'
    serializer = ProposalSerializer
