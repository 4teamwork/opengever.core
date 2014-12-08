from datetime import date
from ftw.builder import builder_registry
from opengever.globalindex.model.task import Task
from opengever.meeting.model import Committee
from opengever.meeting.model import Member
from opengever.meeting.model import Membership
from opengever.meeting.model import Proposal as ProposalModel
from opengever.meeting.proposal import Proposal
from opengever.ogds.base.interfaces import IAdminUnitConfiguration
from opengever.ogds.base.utils import get_ou_selector
from opengever.ogds.models.tests.builders import AdminUnitBuilder
from opengever.ogds.models.tests.builders import OrgUnitBuilder
from opengever.ogds.models.tests.builders import SqlObjectBuilder
from opengever.ogds.models.tests.builders import UserBuilder
from plone.app.testing import TEST_USER_ID
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

builder_registry.register('committee', CommitteeBuilder)


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

builder_registry.register('membership', MemberShipBuilder)
