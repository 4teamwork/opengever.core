from datetime import date
from datetime import timedelta
from ftw.builder import Builder
from ftw.builder import builder_registry
from ftw.builder import create
from opengever.base.browser.helper import get_css_class
from opengever.base.model.favorite import Favorite
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
from opengever.globalindex.model.reminder_settings import ReminderSetting
from opengever.globalindex.model.task import Task
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
from opengever.meeting.model.submitteddocument import SubmittedDocument
from opengever.meeting.proposal import ISubmittedProposal
from opengever.ogds.base.interfaces import IAdminUnitConfiguration
from opengever.ogds.base.utils import get_ou_selector
from opengever.ogds.models.admin_unit import AdminUnit
from opengever.ogds.models.group import Group
from opengever.ogds.models.org_unit import OrgUnit
from opengever.ogds.models.team import Team
from opengever.ogds.models.user import User
from opengever.ogds.models.user_settings import UserSettings
from opengever.task.reminder import Reminder
from opengever.task.reminder import ReminderSameDay
from opengever.testing.builders.base import TEST_USER_ID
from opengever.testing.helpers import localized_datetime
from opengever.testing.model import TransparentModelLoader
from plone import api
from plone.locking.interfaces import ILockable
from plone.registry.interfaces import IRegistry
from plone.uuid.interfaces import IUUID
from zope.component import getUtility
import transaction


class SqlObjectBuilder(object):
    id_argument_name = None
    mapped_class = None

    def __init__(self, session):
        self.session = session
        self.db_session = self._get_db_session(session)
        self.arguments = {}

    def _get_db_session(self, session):
        return session.session

    def id(self, identifier):
        self.arguments[self.id_argument_name] = identifier
        return self

    def create(self, **kwargs):
        self.before_create()
        obj = self.create_object(**kwargs)
        self.add_object_to_session(obj)
        obj = self.after_create(obj)
        self.persist()
        return obj

    def before_create(self):
        pass

    def after_create(self, obj):
        return obj

    def persist(self):
        if self.session.auto_commit:
            transaction.commit()

        if getattr(self.session, 'auto_flush', False):
            self.db_session.flush()

    def add_object_to_session(self, obj):
        self.db_session.add(obj)

    def having(self, **kwargs):
        self.arguments.update(kwargs)
        return self

    def create_object(self):
        return self.mapped_class(**self.arguments)


class AdminUnitBuilder(SqlObjectBuilder):

    mapped_class = AdminUnit
    id_argument_name = 'unit_id'

    def __init__(self, session):
        super(AdminUnitBuilder, self).__init__(session)
        self._as_current_admin_unit = False
        self.arguments[self.id_argument_name] = u'foo'
        self.arguments['ip_address'] = '1.2.3.4'
        self.arguments['site_url'] = 'http://example.com'
        self.arguments['public_url'] = 'http://example.com/public'
        self.arguments['abbreviation'] = 'Client1'
        self.org_unit = None
        self._as_current_admin_unit = False

    def wrapping_org_unit(self, org_unit):
        self.org_unit = org_unit
        self.arguments.update(dict(
            unit_id=org_unit.id(),
            title=org_unit.label(),
        ))
        return self

    def as_current_admin_unit(self):
        self._as_current_admin_unit = True
        return self

    def assign_org_units(self, units):
        self.arguments['org_units'] = units
        return self

    def after_create(self, obj):
        if self.org_unit:
            self.org_unit.assign_to_admin_unit(obj)

        if self._as_current_admin_unit:
            registry = getUtility(IRegistry)
            proxy = registry.forInterface(IAdminUnitConfiguration)
            proxy.current_unit_id = self.arguments.get(self.id_argument_name)

        return obj


builder_registry.register('admin_unit', AdminUnitBuilder)


class OrgUnitBuilder(SqlObjectBuilder):

    mapped_class = OrgUnit
    id_argument_name = 'unit_id'

    def __init__(self, session):
        super(OrgUnitBuilder, self).__init__(session)
        self.arguments[self.id_argument_name] = u'rr'
        self._with_inbox_group = False
        self._with_users_group = False
        self._inbox_users = set()
        self._group_users = set()
        self._as_current_org_unit = False

    def before_create(self):
        self._assemble_groups()

    def after_create(self, obj):
        if self._as_current_org_unit:
            get_ou_selector().set_current_unit(obj.id())
        return obj

    def with_default_groups(self):
        self.with_inbox_group()
        self.with_users_group()
        return self

    def with_inbox_group(self):
        self._with_inbox_group = True
        return self

    def with_users_group(self):
        self._with_users_group = True
        return self

    def as_current_org_unit(self):
        self._as_current_org_unit = True
        return self

    def assign_users(self, users, to_users=True, to_inbox=True):
        if to_users:
            self.with_users_group()
            self._group_users.update(users)

        if to_inbox:
            self.with_inbox_group()
            self._inbox_users.update(users)
        return self

    def _assemble_groups(self):
        if self._with_users_group or self._with_inbox_group:
            unit_id = self.arguments.get(self.id_argument_name)

        if self._with_users_group:
            self.arguments.setdefault('users_group_id', "{0}_users".format(unit_id))
            users_group_title = '{0} Users Group'.format(unit_id)
            self._create_users_group(self.arguments['users_group_id'], users_group_title)

        if self._with_inbox_group:
            self.arguments.setdefault('inbox_group_id', "{0}_inbox_users".format(unit_id))
            users_inbox_title = '{0} Inbox Users Group'.format(unit_id)
            self._create_inbox_group(self.arguments['inbox_group_id'], users_inbox_title)

        # When the builder is used without creating the groups, e.g. in unit tests,
        # we simply set a group id (foo/bar) for which no group exists.
        self.arguments.setdefault('users_group_id', 'foo')
        self.arguments.setdefault('inbox_group_id', 'bar')

    def _create_users_group(self, users_group_id, users_group_title=None):
        create(Builder('group')
               .having(title=users_group_title)
               .with_groupid(users_group_id)
               .with_members(api.user.get(TEST_USER_ID)))
        users_group = create(Builder('ogds_group')
                             .having(groupid=users_group_id,
                                     title=users_group_title,
                                     users=list(self._group_users)))
        self.arguments['users_group'] = users_group

    def _create_inbox_group(self, users_inbox_id, users_inbox_title=None):
        create(Builder('group')
               .having(title=users_inbox_title)
               .with_groupid(users_inbox_id)
               .with_members(api.user.get(TEST_USER_ID)))
        inbox_group = create(Builder('ogds_group')
                             .having(groupid=users_inbox_id,
                                     title=users_inbox_title,
                                     users=list(self._inbox_users)))
        self.arguments['inbox_group'] = inbox_group


builder_registry.register('org_unit', OrgUnitBuilder)


class OGDSUserBuilder(SqlObjectBuilder):

    mapped_class = User
    id_argument_name = 'userid'
    _as_contact_adapter = False

    def __init__(self, session):
        super(OGDSUserBuilder, self).__init__(session)
        self.groups = []
        self.arguments['userid'] = 'test'
        self.arguments['email'] = 'test@example.org'
        self.arguments[self.id_argument_name] = TEST_USER_ID
        self.user_settings = {}

    def as_contact_adapter(self):
        self._as_contact_adapter = True
        return self

    def in_group(self, group):
        if group and group not in self.groups:
            self.groups.append(group)
        return self

    def assign_to_org_units(self, org_units):
        for org_unit in org_units:
            self.groups.append(org_unit.users_group)
        return self

    def create_object(self):
        obj = super(OGDSUserBuilder, self).create_object()
        if self.groups:
            obj.groups.extend(self.groups)
        if self._as_contact_adapter:
            obj = OgdsUserToContactAdapter(obj)
        return obj

    def after_create(self, obj):
        if self.user_settings:
            for key, value in self.user_settings.items():
                UserSettings.save_setting_for_user(obj.userid, key, value)
        return obj

    def add_object_to_session(self, obj):
        if self._as_contact_adapter:
            # unwrap the ogds user from its adapter
            obj = obj.ogds_user

        self.db_session.add(obj)

    def with_user_settings(self, **settings):
        self.user_settings = settings
        return self


builder_registry.register('ogds_user', OGDSUserBuilder)


class OGDSGroupBuilder(SqlObjectBuilder):

    mapped_class = Group
    id_argument_name = 'groupid'

    def __init__(self, session):
        super(OGDSGroupBuilder, self).__init__(session)
        self.arguments['groupid'] = 'testgroup'
        self.arguments['title'] = 'Test Group'


builder_registry.register('ogds_group', OGDSGroupBuilder)


class OGDSTeamBuilder(SqlObjectBuilder):

    mapped_class = Team
    id_argument_name = 'team_id'


builder_registry.register('ogds_team', OGDSTeamBuilder)


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
        self.arguments['workflow_state'] = 'pending'
        self.arguments['dossier_reference_number'] = 'FD 1.2.3 / 1'
        self.arguments['language'] = 'en'
        self.arguments['repository_folder_title'] = 'Just a Repo-Folder'
        self.arguments['issuer'] = TEST_USER_ID

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
                    submitted_version=document.get_current_version_id(
                        missing_as_zero=True),
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
        self.arguments['group_id'] = 'org-unit-1_users'


builder_registry.register('committee_model', CommitteeBuilder)


class MemberBuilder(SqlObjectBuilder):

    mapped_class = Member
    id_argument_name = 'member_id'

    def __init__(self, session):
        super(MemberBuilder, self).__init__(session)
        self.arguments['firstname'] = u'Peter'
        self.arguments['lastname'] = u'M\xfcller'


builder_registry.register('member', MemberBuilder)


class MemberShipBuilder(TransparentModelLoader, SqlObjectBuilder):

    mapped_class = Membership
    auto_loaded_models = ('committee', )

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


class MeetingBuilder(TransparentModelLoader, SqlObjectBuilder):

    mapped_class = Meeting
    auto_loaded_models = ('committee', )

    def __init__(self, session):
        super(MeetingBuilder, self).__init__(session)
        self._scheduled_proposals = []
        self.arguments['dossier_admin_unit_id'] = 'foo'
        self.arguments['dossier_int_id'] = 1234
        self.arguments['start'] = localized_datetime(2011, 12, 13, 9, 30)
        self.arguments['end'] = localized_datetime(2011, 12, 13, 11, 45)
        self.arguments['location'] = u'B\xe4rn'
        self.arguments['title'] = u'C\xf6mmunity meeting'

    def link_with(self, dossier):
        del self.arguments['dossier_admin_unit_id']
        del self.arguments['dossier_int_id']
        assert IMeetingDossier.providedBy(dossier)
        self.arguments['dossier_oguid'] = Oguid.for_object(dossier)
        return self

    def scheduled_proposals(self, proposals):
        for proposal in proposals:
            if ISubmittedProposal.providedBy(proposal):
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
        self.arguments['generated_version'] = document.get_current_version_id(
            missing_as_zero=True)
        return self


builder_registry.register('generated_protocol', GeneratedProtocolBuilder)


class GeneratedExcerptBuilder(GeneratedProtocolBuilder):

    mapped_class = GeneratedExcerpt


builder_registry.register('generated_excerpt', GeneratedExcerptBuilder)


class AgendaItemBuilder(TransparentModelLoader, SqlObjectBuilder):

    auto_loaded_models = ('proposal', )

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


class FavoriteBuilder(SqlObjectBuilder):

    mapped_class = Favorite
    id_argument_name = 'favorite_id'

    def for_object(self, obj):
        self.arguments['oguid'] = Oguid.for_object(obj)
        self.arguments['title'] = obj.title
        self.arguments['portal_type'] = obj.portal_type
        self.arguments['icon_class'] = get_css_class(obj)
        self.arguments['plone_uid'] = IUUID(obj)

        return self

    def for_user(self, user):
        self.arguments['userid'] = user.getId()
        return self


builder_registry.register('favorite', FavoriteBuilder)


class ReminderSettingsBuilder(SqlObjectBuilder):

    mapped_class = ReminderSetting
    id_argument_name = 'reminder_setting_id'

    def for_object(self, obj, option_type=ReminderSameDay.option_type, params=None):
        if params is None:
            params = {}
        reminder = Reminder.create(option_type, params)
        self.arguments['task_id'] = obj.get_sql_object().task_id
        self.arguments['option_type'] = reminder.option_type
        self.arguments['remind_day'] = reminder.calculate_trigger_date(obj.deadline)

        return self

    def for_actor(self, actor):
        self.arguments['actor_id'] = actor.getId()

        return self

    def remind_on(self, remind_day):
        self.arguments['remind_day'] = remind_day

        return self


builder_registry.register('reminder_setting_model', ReminderSettingsBuilder)
