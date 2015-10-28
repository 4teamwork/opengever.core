from datetime import date
from datetime import timedelta
from ftw.builder import Builder
from ftw.builder import builder_registry
from ftw.builder import create
from opengever.base.oguid import Oguid
from opengever.globalindex.model.task import Task
from opengever.locking.interfaces import ISQLLockable
from opengever.locking.model import Lock
from opengever.meeting.interfaces import IMeetingDossier
from opengever.meeting.model import AgendaItem
from opengever.meeting.model import Committee
from opengever.meeting.model import Meeting
from opengever.meeting.model import Member
from opengever.meeting.model import Membership
from opengever.meeting.model import Proposal as ProposalModel
from opengever.meeting.model.generateddocument import GeneratedExcerpt
from opengever.meeting.model.generateddocument import GeneratedProtocol
from opengever.meeting.proposal import IProposal
from opengever.meeting.proposal import Proposal
from opengever.ogds.base.interfaces import IAdminUnitConfiguration
from opengever.ogds.base.utils import get_ou_selector
from opengever.ogds.models.tests.builders import AdminUnitBuilder
from opengever.ogds.models.tests.builders import OrgUnitBuilder
from opengever.ogds.models.tests.builders import SqlObjectBuilder
from opengever.ogds.models.tests.builders import UserBuilder
from opengever.testing.builders.base import TEST_USER_ID
from plone import api
from plone.locking.interfaces import ILockable
from plone.registry.interfaces import IRegistry
from zope.component import getUtility


class PloneAdminUnitBuilder(AdminUnitBuilder):
    """Add plone specific functionality to opengever.ogds.models
    AdminUnitBuilder.

    """
    def __init__(self, session):
        super(PloneAdminUnitBuilder, self).__init__(session)
        self._as_current_admin_unit = False

    def as_current_admin_unit(self):
        self._as_current_admin_unit = True
        return self

    def after_create(self, obj):
        obj = super(PloneAdminUnitBuilder, self).after_create(obj)

        if self._as_current_admin_unit:
            registry = getUtility(IRegistry)
            proxy = registry.forInterface(IAdminUnitConfiguration)
            proxy.current_unit_id = self.arguments.get(self.id_argument_name)
        return obj

builder_registry.register('admin_unit', PloneAdminUnitBuilder, force=True)


class PloneOrgUnitBuilder(OrgUnitBuilder):
    """Add plone specific functionality to opengever.ogds.models
    OrgUnitBuilder.

    """
    def __init__(self, session):
        super(PloneOrgUnitBuilder, self).__init__(session)
        self._as_current_org_unit = False

    def after_create(self, obj):
        if self._as_current_org_unit:
            get_ou_selector().set_current_unit(obj.id())
        return obj

    def as_current_org_unit(self):
        self._as_current_org_unit = True
        return self

    def _create_users_group(self, users_group_id):
        create(Builder('group')
               .with_groupid(users_group_id)
               .with_members(api.user.get(TEST_USER_ID)))
        super(PloneOrgUnitBuilder, self)._create_users_group(users_group_id)

    def _create_inbox_group(self, users_inbox_id):
        create(Builder('group')
               .with_groupid(users_inbox_id)
               .with_members(api.user.get(TEST_USER_ID)))
        super(PloneOrgUnitBuilder, self)._create_inbox_group(users_inbox_id)

builder_registry.register('org_unit', PloneOrgUnitBuilder, force=True)


class PloneOGDSUserBuilder(UserBuilder):
    """Add plone specific functionality to opengever.ogds.models
    UserBuilder.

    """
    def __init__(self, session):
        super(PloneOGDSUserBuilder, self).__init__(session)
        self.arguments[self.id_argument_name] = TEST_USER_ID

builder_registry.register('ogds_user', PloneOGDSUserBuilder, force=True)


class TaskBuilder(SqlObjectBuilder):

    mapped_class = Task
    id_argument_name = 'task_id'

    def __init__(self, session):
        super(TaskBuilder, self).__init__(session)
        self.arguments['sequence_number'] = 1
        self.arguments['admin_unit_id'] = 'qux'
        self.arguments['issuing_org_unit'] = 'foo'
        self.arguments['assigned_org_unit'] = 'bar'
        self.arguments['int_id'] = 12345
        self.arguments['review_state'] = 'task-state-open'

builder_registry.register('globalindex_task', TaskBuilder)


class ProposalModelBuilder(SqlObjectBuilder):

    mapped_class = ProposalModel

    def __init__(self, session):
        super(ProposalModelBuilder, self).__init__(session)
        self.arguments['admin_unit_id'] = 'foo'
        self.arguments['int_id'] = 1234
        self.arguments['physical_path'] = '/bar'
        self.arguments['title'] = 'Bar'
        self.arguments['workflow_state'] = Proposal.workflow.default_state.name
        self.arguments['dossier_reference_number'] = 'FD 1.2.3 / 1'

    def id(self, identifier):
        """Proposals have a composite primary key, admin_unit_id and int_id.

        """
        raise NotImplementedError

builder_registry.register('proposal_model', ProposalModelBuilder)


class CommitteeBuilder(SqlObjectBuilder):

    mapped_class = Committee
    id_argument_name = 'committee_id'

    def __init__(self, session):
        super(CommitteeBuilder, self).__init__(session)
        self.arguments['title'] = 'Bar'
        self.arguments['admin_unit_id'] = 'foo'
        self.arguments['int_id'] = 1234
        self.arguments['physical_path'] = '/foo'
        self.arguments['group_id'] = 'client1_users'

builder_registry.register('committee_model', CommitteeBuilder)


class MemberBuilder(SqlObjectBuilder):

    mapped_class = Member
    id_argument_name = 'member_id'

    def __init__(self, session):
        super(MemberBuilder, self).__init__(session)
        self.arguments['firstname'] = 'Peter'
        self.arguments['lastname'] = 'Meier'

builder_registry.register('member', MemberBuilder)


class MemberShipBuilder(SqlObjectBuilder):

    mapped_class = Membership

    def __init__(self, session):
        super(MemberShipBuilder, self).__init__(session)
        self.arguments['date_from'] = date(2010, 1, 1)
        self.arguments['date_to'] = date(2014, 1, 1)

    def id(self, identifier):
        raise NotImplementedError

    def as_active(self, delta_before=1, delta_after=1):
        past_date = date.today() - timedelta(days=delta_before)
        future_date = date.today() + timedelta(days=delta_after)
        self.arguments['date_from'] = past_date
        self.arguments['date_to'] = future_date
        return self

builder_registry.register('membership', MemberShipBuilder)


class MeetingBuilder(SqlObjectBuilder):

    mapped_class = Meeting

    def __init__(self, session):
        super(MeetingBuilder, self).__init__(session)
        self._scheduled_proposals = []
        self.arguments['dossier_admin_unit_id'] = 'foo'
        self.arguments['dossier_int_id'] = 1234

    def link_with(self, dossier):
        del self.arguments['dossier_admin_unit_id']
        del self.arguments['dossier_int_id']
        assert IMeetingDossier.providedBy(dossier)
        self.arguments['dossier_oguid'] = Oguid.for_object(dossier)
        return self

    def scheduled_proposals(self, proposals):
        for proposal in proposals:
            if IProposal.providedBy(proposal):
                self._scheduled_proposals.append(proposal.load_model())
            else:
                self._scheduled_proposals.append(proposal)

        return self

    def after_create(self, obj):
        obj = super(MeetingBuilder, self).after_create(obj)

        for proposal in self._scheduled_proposals:
            obj.schedule_proposal(proposal)

        return obj

builder_registry.register('meeting', MeetingBuilder)


class GeneratedProtocolBuilder(SqlObjectBuilder):

    mapped_class = GeneratedProtocol

    def for_document(self, document):
        self.arguments['oguid'] = Oguid.for_object(document)
        self.arguments['generated_version'] = document.get_current_version()
        return self

builder_registry.register('generated_protocol', GeneratedProtocolBuilder)


class GeneratedExcerptBuilder(GeneratedProtocolBuilder):

    mapped_class = GeneratedExcerpt

builder_registry.register('generated_excerpt', GeneratedExcerptBuilder)


class AgendaItemBuilder(SqlObjectBuilder):

    def after_create(self, obj):
        obj.meeting.reorder_agenda_items()
        return obj

    mapped_class = AgendaItem

builder_registry.register('agenda_item', AgendaItemBuilder)


class LockBuilder(SqlObjectBuilder):

    mapped_class = Lock

    def __init__(self, session):
        super(LockBuilder, self).__init__(session)
        self.arguments['creator'] = TEST_USER_ID
        self.arguments['lock_type'] = u'plone.locking.stealable'

    def of_obj(self, sqlobj):
        lockable = ILockable(sqlobj)
        self.arguments['object_type'] = lockable.object_type
        self.arguments['object_id'] = lockable.object_id
        return self

builder_registry.register('lock', LockBuilder)
