from datetime import date
from datetime import timedelta
from ftw.builder import Builder
from ftw.builder import builder_registry
from ftw.builder import create
from opengever.base.oguid import Oguid
from opengever.contact.models import Address
from opengever.contact.models import ArchivedAddress
from opengever.contact.models import ArchivedMailAddress
from opengever.contact.models import ArchivedOrganization
from opengever.contact.models import ArchivedPerson
from opengever.contact.models import ArchivedPhoneNumber
from opengever.contact.models import ArchivedURL
from opengever.contact.models import ContactParticipation
from opengever.contact.models import MailAddress
from opengever.contact.models import OgdsUserParticipation
from opengever.contact.models import Organization
from opengever.contact.models import OrgRole
from opengever.contact.models import OrgRoleParticipation
from opengever.contact.models import ParticipationRole
from opengever.contact.models import Person
from opengever.contact.models import PhoneNumber
from opengever.contact.models import URL
from opengever.contact.ogdsuser import OgdsUserToContactAdapter
from opengever.globalindex.model.task import Task
from opengever.locking.model import Lock
from opengever.meeting.committee import ICommittee
from opengever.meeting.interfaces import IMeetingDossier
from opengever.meeting.model import AgendaItem
from opengever.meeting.model import Committee
from opengever.meeting.model import Meeting
from opengever.meeting.model import Member
from opengever.meeting.model import Membership
from opengever.meeting.model import Period
from opengever.meeting.model import Proposal as ProposalModel
from opengever.meeting.model.generateddocument import GeneratedExcerpt
from opengever.meeting.model.generateddocument import GeneratedProtocol
from opengever.meeting.model.submitteddocument import SubmittedDocument
from opengever.meeting.proposal import IProposal
from opengever.meeting.proposal import Proposal
from opengever.ogds.base.interfaces import IAdminUnitConfiguration
from opengever.ogds.base.utils import get_ou_selector
from opengever.ogds.models.tests.builders import AdminUnitBuilder
from opengever.ogds.models.tests.builders import OrgUnitBuilder
from opengever.ogds.models.tests.builders import SqlObjectBuilder
from opengever.ogds.models.tests.builders import UserBuilder
from opengever.testing.builders.base import TEST_USER_ID
from opengever.testing.helpers import localized_datetime
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
    _as_contact_adapter = False

    def __init__(self, session):
        super(PloneOGDSUserBuilder, self).__init__(session)
        self.arguments[self.id_argument_name] = TEST_USER_ID

    def as_contact_adapter(self):
        self._as_contact_adapter = True
        return self

    def create_object(self):
        obj = super(PloneOGDSUserBuilder, self).create_object()
        if self._as_contact_adapter:
            obj = OgdsUserToContactAdapter(obj)
        return obj

    def add_object_to_session(self, obj):
        if self._as_contact_adapter:
            # unwrap the ogds user from its adapter
            obj = obj.ogds_user

        self.db_session.add(obj)

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
        self.arguments['workflow_state'] = Proposal.workflow.default_state.name
        self.arguments['dossier_reference_number'] = 'FD 1.2.3 / 1'
        self.arguments['language'] = 'en'
        self.arguments['repository_folder_title'] = 'Just a Repo-Folder'
        self.arguments['creator'] = TEST_USER_ID

    def id(self, identifier):
        """Proposals have a composite primary key, admin_unit_id and int_id.

        """
        raise NotImplementedError

    def with_submitted_documents(self, *documents):
        """Attach documents on the submitted side."""

        # XXX should receive an optional list of tuples to have different
        # submitted and source documents
        if not documents:
            return

        submitted = []
        for document in documents:
            oguid = Oguid.for_object(document)
            submitted.append(SubmittedDocument(
                    oguid=oguid,
                    submitted_oguid=oguid,
                    submitted_version=document.get_current_version(),
                ))
        self.arguments['submitted_documents'] = submitted
        return self

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
        self.arguments['firstname'] = u'Peter'
        self.arguments['lastname'] = u'M\xfcller'

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
        self.arguments['start'] = localized_datetime(2011, 12, 13, 9, 30)
        self.arguments['end'] = localized_datetime(2011, 12, 13, 11, 45)
        self.arguments['location'] = u'B\xe4rn'
        self.arguments['title'] = u'C\xf6mmunity meeting'

    def before_create(self):
        committee = self.arguments.get('committee')
        if not committee:
            return

        if ICommittee.providedBy(committee):
            self.arguments['committee'] = committee.load_model()

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


class PeriodBuilder(SqlObjectBuilder):

    mapped_class = Period
    id_argument_name = 'period_id'

    def __init__(self, session):
        super(PeriodBuilder, self).__init__(session)
        self.arguments['title'] = unicode(date.today().year)

builder_registry.register('period', PeriodBuilder)


class PersonBuilder(SqlObjectBuilder):

    mapped_class = Person
    id_argument_name = 'person_id'
    organizations = []

    def in_orgs(self, organizations):
        self.organizations = organizations
        return self

    def after_create(self, obj):
        obj = super(PersonBuilder, self).after_create(obj)
        for organization in self.organizations:
            if isinstance(organization, tuple):
                organization, function = organization
            else:
                function = None

            create(Builder('org_role')
                   .having(person=obj,
                           organization=organization,
                           function=function))

        return obj

builder_registry.register('person', PersonBuilder)


class ArchivedPersonBuilder(SqlObjectBuilder):

    mapped_class = ArchivedPerson
    id_argument_name = 'archived_person_id'

    def __init__(self, session):
        super(ArchivedPersonBuilder, self).__init__(session)
        self.arguments['actor_id'] = TEST_USER_ID

builder_registry.register('archived_person', ArchivedPersonBuilder)


class ContactAttributesBuilder(SqlObjectBuilder):
    """Base class for contacts attributes builders like the
    AddressBuilder, PhoneNumberBuilder or the MailAddressBuilder.
    """

    def for_contact(self, contact):
        self.arguments['contact'] = contact
        return self

    def labeled(self, label):
        self.arguments['label'] = label
        return self


class ArchivedContactAttributesBuilder(ContactAttributesBuilder):
    """Base class for archived contacts attributes."""

    def __init__(self, session):
        super(ArchivedContactAttributesBuilder, self).__init__(session)
        self.arguments['actor_id'] = TEST_USER_ID


class AddressBuilder(ContactAttributesBuilder):

    mapped_class = Address
    id_argument_name = 'address_id'

builder_registry.register('address', AddressBuilder)


class ArchivedAddressBuilder(ArchivedContactAttributesBuilder):

    mapped_class = ArchivedAddress
    id_argument_name = 'archived_address_id'

builder_registry.register('archived_address', ArchivedAddressBuilder)


class PhoneNumberBuilder(ContactAttributesBuilder):

    mapped_class = PhoneNumber
    id_argument_name = 'phone_number_id'

builder_registry.register('phonenumber', PhoneNumberBuilder)


class ArchivedPhoneNumberBuilder(ArchivedContactAttributesBuilder):

    mapped_class = ArchivedPhoneNumber
    id_argument_name = 'archived_phonenumber_id'

builder_registry.register('archived_phonenumber', ArchivedPhoneNumberBuilder)


class MailAddressBuilder(ContactAttributesBuilder):

    mapped_class = MailAddress
    id_argument_name = 'mailaddress_id'

builder_registry.register('mailaddress', MailAddressBuilder)


class ArchivedMailAddressBuilder(ArchivedContactAttributesBuilder):

    mapped_class = ArchivedMailAddress
    id_argument_name = 'archived_mail_address_id'

builder_registry.register('archived_mail_addresses', ArchivedMailAddressBuilder)


class URLBuilder(ContactAttributesBuilder):

    mapped_class = URL
    id_argument_name = 'url_id'

builder_registry.register('url', URLBuilder)


class ArchivedURLBuilder(ArchivedContactAttributesBuilder):

    mapped_class = ArchivedURL
    id_argument_name = 'archived_url_id'

builder_registry.register('archived_url', ArchivedURLBuilder)


class OrganizationBuilder(SqlObjectBuilder):

    mapped_class = Organization
    id_argument_name = 'organization_id'

    def named(self, name):
        self.arguments['name'] = name
        return self

builder_registry.register('organization', OrganizationBuilder)


class ArchivedOrganizationBuilder(SqlObjectBuilder):

    mapped_class = ArchivedOrganization
    id_argument_name = 'archived_organization_id'

    def __init__(self, session):
        super(ArchivedOrganizationBuilder, self).__init__(session)
        self.arguments['actor_id'] = TEST_USER_ID

builder_registry.register('archived_organization', ArchivedOrganizationBuilder)


class OrgRoleBuilder(SqlObjectBuilder):

    mapped_class = OrgRole
    id_argument_name = 'org_role_id'

builder_registry.register('org_role', OrgRoleBuilder)


class BaseParticipationBuilder(SqlObjectBuilder):

    id_argument_name = 'participation_id'
    roles = []

    def for_dossier(self, obj):
        self.arguments['dossier_oguid'] = Oguid.for_object(obj)
        return self

    def with_roles(self, roles):
        self.roles = roles
        return self

    def after_create(self, obj):
        if self.roles:
            obj.add_roles(self.roles)
        return obj


class ContactParticipationBuilder(BaseParticipationBuilder):

    mapped_class = ContactParticipation

    def for_contact(self, contact):
        self.arguments['contact'] = contact
        return self

builder_registry.register('contact_participation', ContactParticipationBuilder)


class OrgRoleParticipationBuilder(BaseParticipationBuilder):

    mapped_class = OrgRoleParticipation

    def for_org_role(self, org_role):
        self.arguments['org_role'] = org_role
        return self

builder_registry.register('org_role_participation', OrgRoleParticipationBuilder)


class OgdsUserParticipationBuilder(BaseParticipationBuilder):

    mapped_class = OgdsUserParticipation

    def for_ogds_user(self, adapted_ogds_user):
        self.arguments['ogds_user'] = adapted_ogds_user
        return self

builder_registry.register('ogds_user_participation', OgdsUserParticipationBuilder)


class ParticipationRoleBuilder(SqlObjectBuilder):

    mapped_class = ParticipationRole
    id_argument_name = 'participation_role_id'

builder_registry.register('participation_role', ParticipationRoleBuilder)
