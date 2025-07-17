# -*- coding: utf-8 -*-
from Acquisition import aq_parent
from collections import namedtuple
from opengever.exportng.utils import userid_to_email
from opengever.meeting.model import AgendaItem
from opengever.meeting.model import Committee
from opengever.meeting.model import Meeting
from opengever.meeting.model import Proposal
from opengever.ogds.models.group import Group
from opengever.ogds.models.user import User
from sqlalchemy.sql.expression import false
import logging

logger = logging.getLogger('opengever.exportng')

Attribute = namedtuple(
    'Attribute',
    ['name', 'col_name', 'col_type', 'getter'],
)
Attribute.__new__.__defaults__ = (None,)


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

    def get_values(self, item):
        data = {}
        for attr in self.mapping:
            if attr.getter is not None:
                value = attr.getter(item, attr.name)
            else:
                value = getattr(item, attr.name)
            data[attr.col_name] = value
        return data

    def truncate(self):
        with self.engine.begin() as conn:
            conn.execution_options(autocommit=True).execute(
                "TRUNCATE TABLE {}".format(self.table))

    def sync(self):
        self.truncate()
        inserts = []
        for item in self.get_ogds_items():
            inserts.append(self.get_values(item))

        table = self.metadata.tables[self.table]
        with self.engine.connect() as conn:
            conn.execute(table.insert(), inserts)
        logger.info('Added %s: %s', table, len(inserts))


class UserSyncer(OGDSSyncer):

    table = 'users'
    model = User
    key = 'email'

    mapping = [
        Attribute('email', 'email', 'varchar'),
        Attribute('firstname', 'firstname', 'varchar'),
        Attribute('lastname', 'lastname', 'varchar'),
        Attribute('active', 'active', 'boolean'),
    ]


class GroupSyncer(OGDSSyncer):

    table = 'groups'
    model = Group
    key = 'groupname'

    mapping = [
        Attribute('groupname', 'groupname', 'varchar'),
        Attribute('title', 'title', 'varchar'),
        Attribute('active', 'active', 'boolean'),
    ]


def get_committee_uid(item, attr):
    return item.resolve_committee().UID()


def get_committee_dossier_location(item, attr):
    return item.resolve_committee().get_repository_folder().UID()


def get_protocoltype(item, attr):
    return 'WORD'


def get_committee_state(item, attr):
    return item.workflow_state == 'active'


class CommitteeSyncer(OGDSSyncer):

    table = 'committees'
    model = Committee
    key = 'committee_id'

    mapping = [
        Attribute('committee_id', 'objexternalkey', 'varchar', get_committee_uid),
        Attribute('title', 'objname', 'varchar'),
        Attribute('workflow_state', 'cdeactivated', 'boolean', get_committee_state),
        Attribute('committee_id', 'cmeetingdossierlocation', 'varchar', get_committee_dossier_location),
        Attribute('committee_id', 'cprotocoltype', 'varchar', get_protocoltype),
    ]


def get_timezone(item, attr):
    return 'Europe/Zurich'


def get_dossier_uid(item, attr):
    oguid = getattr(item, attr)
    return oguid.resolve_object().UID()


def get_meeting_committee_uid(item, attr):
    committee = getattr(item, attr)
    return committee.resolve_committee().UID()


def get_meeting_id(item, attr):
    return '{}-{}-{}-{}'.format(
        item.dossier_admin_unit_id,
        item.dossier_int_id,
        item.committee_id,
        item.meeting_id,
    )


def get_meeting_state(item, attr):
    state_mapping = {
        'pending': 'IN_PREPARATION',
        'held': 'IN_PROGRESS',
        'closed': 'COMPLETED',
        'cancelled': 'CLOSED',
    }
    return state_mapping.get(item.workflow_state)


class MeetingSyncer(OGDSSyncer):

    table = 'meetings'
    model = Meeting
    key = 'meeting_id'

# mlink (video call link)
    mapping = [
        Attribute('meeting_id', 'objexternalkey', 'varchar', get_meeting_id),
        Attribute('title', 'objsubject', 'varchar'),
        Attribute('start', 'mbegin', 'datetime'),
        Attribute('end', 'mend', 'datetime'),
        Attribute('location', 'mlocation', 'varchar'),
        Attribute('committee', 'mcommittee', 'varchar', get_meeting_committee_uid),
        Attribute('dossier_oguid', 'mdossier', 'varchar', get_dossier_uid),
        Attribute('start', 'mtimezone', 'varchar', get_timezone),
        Attribute('workflow_state', 'mmeetingstate', 'varchar', get_meeting_state),
    ]


class MeetingParticipantsSyncer(OGDSSyncer):

    table = 'meeting_participants'
    model = Meeting
    key = 'meeting_id'

    mapping = [
        Attribute('meeting_id', 'meeting', 'varchar', get_meeting_id),
        Attribute('participant', 'participant', 'varchar'),
        Attribute('role', 'role', 'varchar'),
    ]

    def get_values(self, item):
        meeting_id = get_meeting_id(item, 'meeting_id')
        participants = []
        for participant in item.participants:
            role = None
            if participant == item.presidency:
                role = 'Vorsitz'
            elif participant == item.secretary:
                role = 'Protokollführung'
            participants.append({
                'meeting': meeting_id,
                'participant': participant.email,
                'role': role,
            })
        return participants

    def sync(self):
        self.truncate()
        inserts = []
        for item in self.get_ogds_items():
            inserts += self.get_values(item)

        table = self.metadata.tables[self.table]
        with self.engine.connect() as conn:
            conn.execute(table.insert(), inserts)
        logger.info('Added %s: %s', table, len(inserts))


def get_agendaitem_id(item, attr):
    return '{}-{}'.format(
        get_meeting_id(item.meeting, 'meeting_id'), item.agenda_item_id)


def get_agendaitem_meeting_id(item, attr):
    return get_meeting_id(item.meeting, 'meeting_id')


def get_agendaitem_proposal_id(item, attr):
    if item.has_proposal:
        return item.proposal.resolve_proposal().UID()


def get_agendaitem_dossier(item, attr):
    if item.has_proposal:
        return aq_parent(item.proposal.resolve_proposal()).UID()


class AgendaItemSyncer(OGDSSyncer):

    table = 'agendaitems'
    model = AgendaItem
    key = 'agenda_item_id'

    mapping = [
        Attribute('agenda_item_id', 'objexternalkey', 'varchar', get_agendaitem_id),
        Attribute('meeting_id', 'objprimaryrelated', 'varchar', get_agendaitem_meeting_id),
        Attribute('title', 'objsubject', 'varchar'),
        Attribute('workflow_state', 'aistate', 'varchar'),
        Attribute('proposal_id', 'aiproposal', 'varchar', get_agendaitem_proposal_id),
        Attribute('proposal_id', 'mdossier', 'varchar', get_agendaitem_dossier),
    ]


def get_proposal_uid(item, attr):
    return item.resolve_proposal().UID()


def get_proposal_committee_uid(item, attr):
    return item.committee.resolve_committee().UID()


def get_proposal_dossier_uid(item, attr):
    return item.resolve_proposal().get_containing_dossier().UID()


def get_proposal_issuer(item, attr):
    return userid_to_email(item.issuer)


def get_proposal_creator(item, attr):
    return userid_to_email(item.resolve_proposal().Creator())


def get_proposal_agenda_item(item, attr):
    if item.agenda_item is not None:
        return get_agendaitem_id(item.agenda_item, attr)
    else:
        return None


def get_proposal_state(item, attr):
    state_mapping = {
        'scheduled': 'REGISTERED',
        'pending': 'IN_PREPARATION',
        'submitted': 'SUBMITTED',
        'decided': 'DECIDED',
        'cancelled': 'DISCARDED',
    }
    return state_mapping.get(item.workflow_state)


class ProposalSyncer(OGDSSyncer):

    table = 'proposals'
    model = Proposal
    key = 'proposal_id'

# objcreatedat, objmodifiedat?
    mapping = [
        Attribute('proposal_id', 'objexternalkey', 'varchar', get_proposal_uid),
        Attribute('committee', 'pcommittee', 'varchar', get_proposal_committee_uid),
        Attribute('title', 'objname', 'varchar'),
        Attribute('workflow_state', 'pstate', 'varchar', get_proposal_state),
        Attribute('Creator', 'objcreatedby', 'varchar', get_proposal_creator),
        Attribute('issuer', 'pproposedby', 'varchar', get_proposal_issuer),
        Attribute('dossier', 'poriginaldossier', 'varchar', get_proposal_dossier_uid),
        Attribute('agendaitem', 'pagendaitem', 'varchar', get_proposal_agenda_item),
    ]


# class SubmittedDocumentSyncer(OGDSSyncer):

#     table = 'submitteddocuments'
#     model = SubmittedDocument
#     key = 'document_id'

#     mapping = [
#         Attribute('document_id', 'objexternalkey', 'varchar', get_proposal_uid),
#         Attribute('UID', 'objexternalkey', 'varchar', None),
#         Attribute('parent', 'objprimaryrelated', 'varchar', parent_uid),
#         Attribute('created', 'objcreatedat', 'datetime', as_datetime),
#         Attribute('modified', 'objmodifiedat', 'datetime', as_datetime),
#         Attribute('title', 'objname', 'varchar', get_title),
#         Attribute('Creator', 'objcreatedby', 'varchar', get_creator),

#     ]

