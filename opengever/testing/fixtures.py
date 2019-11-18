from AccessControl.SecurityManagement import getSecurityManager
from AccessControl.SecurityManagement import setSecurityManager
from contextlib import contextmanager
from contextlib import nested
from datetime import date
from DateTime import DateTime
from datetime import datetime
from datetime import timedelta
from ftw.builder import Builder
from ftw.builder import create
from ftw.builder import ticking_creator
from ftw.bumblebee.interfaces import IBumblebeeUserSaltStore
from ftw.bumblebee.tests.helpers import asset as bumblebee_asset
from ftw.testing import freeze
from ftw.testing import staticuid
from ftw.tokenauth.pas.storage import CredentialStorage
from opengever.base.behaviors.lifecycle import ARCHIVAL_VALUE_UNWORTHY
from opengever.base.behaviors.lifecycle import ARCHIVAL_VALUE_WORTHY
from opengever.base.command import CreateEmailCommand
from opengever.base.model import create_session
from opengever.base.role_assignments import InvitationRoleAssignment
from opengever.base.role_assignments import RoleAssignmentManager
from opengever.base.role_assignments import SharingRoleAssignment
from opengever.mail.tests import MAIL_DATA
from opengever.officeconnector.helpers import get_auth_plugin
from opengever.ogds.base.utils import ogds_service
from opengever.testing import assets
from opengever.testing.helpers import time_based_intids
from opengever.testing.integration_test_case import FEATURE_FLAGS
from operator import methodcaller
from plone import api
from plone.app.testing import login
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import TEST_USER_ID
from time import time
from zope.annotation.interfaces import IAnnotations
from zope.component.hooks import getSite
import json
import logging
import pytz


JWT_SECRET = 'topsecret'


class OpengeverContentFixture(object):
    """Provide a basic content fixture for integration tests."""

    def __init__(self):
        start = time()
        self._logger = logger = logging.getLogger('opengever.testing')
        self._lookup_table = {
            'manager': ('user', SITE_OWNER_NAME),
        }
        self._registered_paths = set()
        self.configure_jwt_plugin()
        self.create_fixture_content()
        logger.info('(fixture setup in %ds) ', round(time() - start, 3))

    def configure_jwt_plugin(self):
        # Set up a static secret for the Zope acl_users JWT plugin
        # XXX - the __call__ based _lookup_table cannot be used within __init__
        with self.login(api.user.get(SITE_OWNER_NAME)):
            jwt_plugin = get_auth_plugin(api.portal.get().getPhysicalRoot())
            jwt_plugin.use_keyring = False
            jwt_plugin._secret = JWT_SECRET

        # Set up a static secret for the Plone acl_users JWT plugin
        jwt_plugin = get_auth_plugin(api.portal.get())
        jwt_plugin.use_keyring = False
        jwt_plugin._secret = JWT_SECRET

    def create_fixture_content(self):
        with self.freeze_at_hour(4):
            self.create_units()

        # Create users. Here we can use a 1minute step between creation of two
        # objects as every second one is a ogds user with no creation date.
        with self.freeze_at_hour(5, tick_length=1):
            self.create_users()
            self.load_service_keys()

        with self.freeze_at_hour(6):
            self.create_teams()
            self.create_contacts()

        with self.freeze_at_hour(7):
            with self.login(self.administrator):
                self.create_repository_tree()

        with self.freeze_at_hour(8):
            with self.login(self.administrator):
                self.create_templates()

        with self.freeze_at_hour(9):
            with self.login(self.administrator):
                self.create_special_templates()
                self.create_subtemplates()

                with self.features('meeting'):
                    self.create_committees()

        with self.freeze_at_hour(10):
            with self.login(self.administrator):
                self.create_inbox()
                self.create_workspace_root()

        with self.freeze_at_hour(14):
            with self.login(self.dossier_responsible):
                self.create_treaty_dossiers()
                self.create_expired_dossier()
                self.create_inactive_dossier()
                self.create_empty_dossier()
                self.create_resolvable_dossier()

        with self.freeze_at_hour(15):
            with self.login(self.dossier_responsible):
                self.create_emails()

            with self.login(self.committee_responsible):
                with self.features('meeting'):
                    self.create_meetings()

        with self.freeze_at_hour(16):
            with self.login(self.dossier_responsible):
                self.create_tasks()

        with self.freeze_at_hour(17):
            self.create_private_root()

            with self.login(self.regular_user):
                self.create_private_folder()

        with self.freeze_at_hour(18):
            with self.login(self.workspace_owner):
                self.create_workspace()
                self.create_todos()

            with self.login(self.dossier_responsible):
                self.create_shadow_document()
                self.create_protected_dossiers()

        with self.freeze_at_hour(19):
            with self.login(self.dossier_responsible):
                self.create_offered_dossiers()
            with self.login(self.records_manager):
                self.create_disposition()
                self.create_disposition_with_sip()

    def __call__(self):
        return self._lookup_table

    def set_roles(self, obj, principal, roles):
        RoleAssignmentManager(obj).add_or_update_assignment(
            SharingRoleAssignment(principal, roles))

    def create_units(self):
        self.admin_unit = create(
            Builder('admin_unit')
            .having(
                title=u'Hauptmandant',
                unit_id=u'plone',
                public_url='http://nohost/plone',
                )
            .as_current_admin_unit()
            )

        self.org_unit_fd = create(
            Builder('org_unit')
            .id('fa')
            .having(
                title=u'Finanz\xe4mt',
                admin_unit=self.admin_unit,
                )
            .with_default_groups()
            .as_current_org_unit()
            )

        self.org_unit_rk = create(
            Builder('org_unit')
            .id('rk')
            .having(
                title=u'Ratskanzl\xc3\xa4i',
                admin_unit=self.admin_unit,
                )
            .with_default_groups()
        )

    def create_users(self):
        self.administrator = self.create_user(
            'administrator',
            u'Nicole',
            u'Kohler',
            ['Administrator', 'APIUser'],
            )

        self.member_admin = self.create_user(
            'member_admin',
            u'David',
            u'Meier',
            ['MemberAreaAdministrator', 'APIUser'],
            )

        self.dossier_responsible = self.create_user(
            'dossier_responsible',
            u'Robert',
            u'Ziegler',
            )

        self.regular_user = self.create_user(
            'regular_user',
            u'K\xe4thi',
            u'B\xe4rfuss',
            address1='Kappelenweg 13',
            address2='Postfach 1234',
            city='Vorkappelen',
            country='Schweiz',
            department='Staatskanzlei',
            department_abbr='SK',
            description='nix',
            directorate='Staatsarchiv',
            directorate_abbr='Arch',
            email2='bar@example.com',
            email='foo@example.com',
            phone_fax='012 34 56 77',
            phone_mobile='012 34 56 76',
            phone_office='012 34 56 78',
            salutation='Prof. Dr.',
            url='http://www.example.com',
            zip_code='1234',
            )

        self.meeting_user = self.create_user(
            'meeting_user',
            u'Herbert',
            u'J\xe4ger',
            )

        self.secretariat_user = self.create_user(
            'secretariat_user',
            u'J\xfcrgen',
            u'K\xf6nig',
            group=self.org_unit_fd.inbox_group,
            )

        self.committee_responsible = self.create_user(
            'committee_responsible',
            u'Fr\xe4nzi',
            u'M\xfcller',
            )

        self.dossier_manager = self.create_user(
            'dossier_manager',
            u'F\xe4ivel',
            u'Fr\xfchling',
            )

        self.records_manager = self.create_user(
            'records_manager',
            u'Ramon',
            u'Flucht',
            ['Records Manager'],
            )

        self.workspace_owner = self.create_user(
            'workspace_owner',
            u'G\xfcnther',
            u'Fr\xf6hlich',
            )

        self.workspace_admin = self.create_user(
            'workspace_admin',
            u'Fridolin',
            u'Hugentobler',
            )

        self.workspace_member = self.create_user(
            'workspace_member',
            u'B\xe9atrice',
            u'Schr\xf6dinger',
            )

        self.workspace_guest = self.create_user(
            'workspace_guest',
            u'Hans',
            u'Peter',
            )

        self.archivist = self.create_user(
            'archivist',
            u'J\xfcrgen',
            u'Fischer',
            ['Archivist']
            )

        self.service_user = self.create_user(
            'service_user',
            u'Service',
            u'User',
            [
                'Member',
                'ServiceKeyUser',
                'Impersonator',
                'Administrator',
            ])

        self.webaction_manager = self.create_user(
            'webaction_manager',
            u'WebAction',
            u'Manager',
            ['WebActionManager'],
            )

        # This user is intended to be used in situations where you need a user
        # which has only the 'Reader' role on some context and one has to build
        # the granting of that themselves
        firstname = u'L\xfccklicher'
        lastname = u'L\xe4ser'

        builder = (
            Builder('user')
            .named(firstname, lastname)
            .with_roles(['Member'])
            )

        builder.update_properties()  # updates builder.userid
        email = '{}@gever.local'.format(builder.userid)
        plone_user = create(builder.with_email(email))

        create(
            Builder('ogds_user')
            .id(plone_user.getId())
            .having(firstname=firstname, lastname=lastname, email=email)
            )

        self._lookup_table['reader_user'] = ('user', plone_user.getId())

        # This user is intended to be used in situations where you need a user
        # which has only the 'Contributor' role on some context, as granted by
        # accepting a task
        firstname = u'James'
        lastname = u'B\xf6nd'

        builder = (Builder('user').named(firstname, lastname).with_roles([]))
        builder.update_properties()  # updates builder.userid
        email = '{}@gever.local'.format(builder.userid)
        plone_user = create(builder.with_email(email))

        create(
            Builder('ogds_user')
            .id(plone_user.getId())
            .having(firstname=firstname, lastname=lastname, email=email)
            .assign_to_org_units([self.org_unit_rk])
        )

        self._lookup_table['foreign_contributor'] = ('user', plone_user.getId())

    def load_service_keys(self):
        for filename in ['service_user_generic.public.json']:
            public_key = json.loads(assets.load(filename))
            public_key['issued'] = DateTime(public_key['issued']).asdatetime()
            plugin = getSite().acl_users.token_auth
            CredentialStorage(plugin).add_service_key(public_key)

    def create_teams(self):
        users = [
            ogds_service().find_user(user.getId())
            for user in [self.regular_user, self.dossier_responsible]
            ]

        group_a = create(
            Builder('ogds_group')
            .having(groupid='projekt_a', title=u'Projekt A', users=users)
            )

        self.projekt_a = create(
            Builder('ogds_team')
            .having(
                title=u'Projekt \xdcberbaung Dorfmatte',
                group=group_a,
                org_unit=self.org_unit_fd,
                )
            )

        users = [
            ogds_service().find_user(user.getId())
            for user in [self.committee_responsible, self.meeting_user]
            ]

        group_b = create(
            Builder('ogds_group')
            .having(
                groupid='projekt_b',
                title=u'Projekt B',
                users=users,
                )
            )

        self.projekt_b = create(
            Builder('ogds_team')
            .having(
                title=u'Sekretariat Abteilung XY',
                group=group_b,
                org_unit=self.org_unit_fd,
                )
            )

        group_empty = create(
            Builder('ogds_group')
            .having(
                groupid=u'projekt_laeaer',
                title=u'Projekt L\xc3\xa4\xc3\xa4r',
                users=[],
            )
        )

        create(
            Builder('ogds_team')
            .having(
                title=u'Sekretariat Abteilung Null',
                group=group_empty,
                org_unit=self.org_unit_fd,
            )
        )

    @staticuid()
    def create_repository_tree(self):
        self.root = self.register('repository_root', create(
            Builder('repository_root')
            .with_tree_portlet()
            .having(
                title_de=u'Ordnungssystem',
                title_fr=u'Syst\xe8me de classement',
                )
            ))

        self.set_roles(
            self.root, self.org_unit_fd.users_group_id,
            ['Reader', 'Contributor', 'Editor'])
        self.set_roles(
            self.root, self.secretariat_user.getId(),
            ['Reviewer', 'Publisher'])

        self.root.reindexObjectSecurity()

        self.repofolder0 = self.register('branch_repofolder', create(
            Builder('repository')
            .within(self.root)
            .having(
                title_de=u'F\xfchrung',
                title_fr=u'Direction',
                description=u'Alles zum Thema F\xfchrung.',
                )
            ))

        self.set_roles(
            self.repofolder0, self.dossier_manager.getId(),
            ['DossierManager'])

        self.repofolder0.reindexObjectSecurity()

        self.repofolder00 = self.register('leaf_repofolder', create(
            Builder('repository')
            .within(self.repofolder0)
            .having(
                title_de=u'Vertr\xe4ge und Vereinbarungen',
                title_fr=u'Contrats et accords',
                )
            ))

        self.repofolder1 = self.register('empty_repofolder', create(
            Builder('repository')
            .within(self.root)
            .having(
                title_de=u'Rechnungspr\xfcfungskommission',
                title_fr=u'Commission de v\xe9rification',
                )
            ))

        self.register('inactive_repofolder', create(
            Builder('repository')
            .within(self.root)
            .having(
                title_de=u'Spinn\xe4nnetzregistrar',
                title_fr=u"Toile d'araign\xe9e",
                )
            .in_state('repositoryfolder-state-inactive')
            ))

    @staticuid()
    def create_contacts(self):
        self.contactfolder = self.register('contactfolder', create(
            Builder('contactfolder')
            .having(
                id='kontakte',
                title_de=u'Kontakte',
                title_en=u'Contacts',
                )
            ))

        self.set_roles(
            self.contactfolder, self.org_unit_fd.users_group_id,
            ['Reader'])

        self.set_roles(
            self.contactfolder, self.org_unit_fd.users_group_id,
            ['Reader', 'Contributor', 'Editor'])

        self.contactfolder.reindexObjectSecurity()

        self.hanspeter_duerr = self.register('hanspeter_duerr', create(
            Builder('contact')
            .within(self.contactfolder)
            .having(
                firstname=u'Hanspeter',
                lastname='D\xc3\xbcrr'.decode('utf-8'),
                )
            ))

        self.franz_meier = self.register('franz_meier', create(
            Builder('contact')
            .within(self.contactfolder)
            .having(
                firstname=u'Franz',
                lastname=u'Meier',
                email=u'meier.f@example.com',
                )
            ))

        self.josef_buehler = create(
            Builder('person')
            .having(firstname=u'Josef', lastname=u'B\xfchler'),
            )

        self.meier_ag = create(Builder('organization').named(u'Meier AG'))

        create_session().flush()

    @staticuid()
    def create_templates(self):
        self.templates = self.register('templates', create(
            Builder('templatefolder')
            .titled(u'Vorlagen')
            .having(id='vorlagen')
            ))

        self.set_roles(
            self.templates, self.org_unit_fd.users_group_id, ['Reader'])
        self.set_roles(
            self.templates, self.administrator.getId(),
            ['Reader', 'Contributor', 'Editor'])
        self.set_roles(
            self.templates, self.dossier_responsible.getId(),
            ['Reader', 'Contributor', 'Editor'])

        self.register('asset_template', create(
            Builder('document')
            .titled(u'T\xc3\xb6mpl\xc3\xb6te Ohne')
            .with_asset_file('without_custom_properties.docx')
            .within(self.templates)
            ))

        self.register('normal_template', create(
            Builder('document')
            .titled(u'T\xc3\xb6mpl\xc3\xb6te Normal')
            .with_dummy_content()
            .within(self.templates)
            ))

        self.register('empty_template', create(
            Builder('document')
            .titled(u'T\xc3\xb6mpl\xc3\xb6te Leer')
            .within(self.templates)
            ))

        with self.features('doc-properties'):
            self.register('docprops_template', create(
                Builder('document')
                .titled(u'T\xc3\xb6mpl\xc3\xb6te Mit')
                .with_asset_file('with_custom_properties.docx')
                .with_modification_date(datetime(2010, 12, 28))
                .within(self.templates)
                ))

        with self.features('meeting'):
            self.meeting_template = self.register('meeting_template', create(
                Builder('meetingtemplate')
                .titled(u'Meeting T\xc3\xb6mpl\xc3\xb6te')
                .within(self.templates)
                ))
            self.register('paragraph_template', create(
                Builder('paragraphtemplate')
                .titled(u'Begr\xfcssung')
                .having(position=1)
                .within(self.meeting_template)
                ))
            create(
                Builder('paragraphtemplate')
                .titled(u'Gesch\xf0fte')
                .having(position=2)
                .within(self.meeting_template)
                )
            create(
                Builder('paragraphtemplate')
                .titled(u'Schlusswort')
                .having(position=3)
                .within(self.meeting_template)
                )

    @staticuid()
    def create_special_templates(self):
        self.sablon_template = self.register('sablon_template', create(
            Builder('sablontemplate')
            .within(self.templates)
            .with_asset_file('sablon_template.docx')
            ))

        with self.features('meeting'):
            self.proposal_template = self.register('proposal_template', create(
                Builder('proposaltemplate')
                .titled(u'Geb\xfchren')
                .with_asset_file(u'vertragsentwurf.docx')
                .within(self.templates)
                ))

            self.register('ad_hoc_agenda_item_template', create(
                Builder('proposaltemplate')
                .titled(u'Freitext Traktandum')
                .with_asset_file(u'freitext_traktandum.docx')
                .within(self.templates)
                ))

            self.register('recurring_agenda_item_template', create(
                Builder('proposaltemplate')
                .titled(u'Wiederkehrendes Traktandum')
                .with_asset_file(u'wiederkehrendes_traktandum.docx')
                .within(self.templates)
                ))

        self.tasktemplatefolder = self.register('tasktemplatefolder', create(
            Builder('tasktemplatefolder')
            .titled(u'Verfahren Neuanstellung')
            .in_state('tasktemplatefolder-state-activ')
            .having(sequence_type='parallel')
            .within(self.templates)
        ))

        self.tasktemplate = self.register('tasktemplate', create(
            Builder('tasktemplate')
            .titled(u'Arbeitsplatz einrichten.')
            .having(**{
                'issuer': 'responsible',
                'responsible_client': 'fa',
                'responsible': 'robert.ziegler',
                'deadline': 10,
                })
            .within(self.tasktemplatefolder)
            ))

        self.dossiertemplate = self.register('dossiertemplate', create(
            Builder('dossiertemplate')
            .titled(u'Bauvorhaben klein')
            .having(**{
                'description': u'Lorem ipsum',
                'keywords': (u'secret', u'special'),
                'comments': 'this is very special',
                'filing_prefix': 'department',
                })
            .within(self.templates)
            ))

        # The title of this one should be alphabetically after
        # subdossiertemplatedocument for testing sorting!
        self.register('dossiertemplatedocument', create(
            Builder('document')
            .within(self.dossiertemplate)
            .titled(u'Werkst\xe4tte')
            .having(preserved_as_paper=True)
        ))

        self.subdossiertemplate = self.register('subdossiertemplate', create(
            Builder('dossiertemplate')
            .titled(u'Anfragen')
            .within(self.dossiertemplate)
            ))

        self.register('subdossiertemplatedocument', create(
            Builder('document')
            .within(self.subdossiertemplate)
            .titled(u'Baumsch\xfctze')
            .having(preserved_as_paper=True)
        ))

    @staticuid()
    def create_subtemplates(self):
        subtemplates = self.register('subtemplates', create(
            Builder('templatefolder')
            .titled(u'Vorlagen neu')
            .having(id='vorlagen-neu')
            .within(self.templates)
            ))

        self.set_roles(subtemplates, self.org_unit_fd.users_group_id, ['Reader'])
        self.set_roles(subtemplates, self.administrator.getId(),
                       ['Reader', 'Contributor', 'Editor'])
        self.set_roles(subtemplates, self.dossier_responsible.getId(),
                       ['Reader', 'Contributor', 'Editor'])

        self.register('subtemplate', create(
            Builder('document')
            .titled(u'T\xc3\xb6mpl\xc3\xb6te Sub')
            .with_dummy_content()
            .with_modification_date(datetime(2020, 2, 29))
            .within(subtemplates)
            ))

    @staticuid()
    def create_committees(self):
        self.committee_container = self.register('committee_container', create(
            Builder('committee_container')
            .titled(u'Sitzungen')
            ))

        self.set_roles(
            self.committee_container, self.committee_responsible.getId(),
            ['MeetingUser'])
        self.set_roles(
            self.committee_container, self.meeting_user.getId(),
            ['MeetingUser'])
        self.set_roles(
            self.committee_container, self.administrator.getId(),
            ['CommitteeAdministrator'])
        self.committee_container.reindexObjectSecurity()

        self.committee = self.register('committee', self.create_committee(
            title=u'Rechnungspr\xfcfungskommission',
            repository_folder=self.repofolder1,
            group_id='committee_rpk_group',
            group_title=u'Gruppe Rechnungspr\xfcfungskommission',
            responsibles=[
                self.administrator,
                self.committee_responsible,
                ],
            templates={
                'agendaitem_list_template': self.sablon_template,
                'protocol_header_template': self.sablon_template,
                'excerpt_header_template': self.sablon_template,
                'excerpt_suffix_template': self.sablon_template,
                'paragraph_template': self.sablon_template,
            }
            ))

        self.register_raw(
            'committee_id',
            self.committee.load_model().committee_id,
            )

        self.set_roles(
            self.committee, self.meeting_user.getId(), ['CommitteeMember'])

        self.committee_president = self.create_committee_membership(
            self.committee,
            'committee_president',
            firstname=u'Heidrun',
            lastname=u'Sch\xf6ller',
            email='h.schoeller@example.org',
            date_from=datetime(2014, 1, 1),
            date_to=datetime(2016, 12, 31),
            )

        self.committee_secretary = create(
            Builder('ogds_user')
            .id('committee.secretary')
            .having(firstname=u'C\xf6mmittee', lastname='Secretary', email='committee.secretary@example.com')
            .assign_to_org_units([self.org_unit_fd])
            )

        self.committee_participant_1 = self.create_committee_membership(
            self.committee,
            'committee_participant_1',
            firstname=u'Gerda',
            lastname=u'W\xf6lfl',
            email='g.woelfl@example.com',
            date_from=datetime(2014, 1, 1),
            date_to=datetime(2016, 12, 31),
            )

        self.committee_participant_2 = self.create_committee_membership(
            self.committee,
            'committee_participant_2',
            firstname=u'Jens',
            lastname=u'Wendler',
            email='jens-wendler@example.com',
            date_from=datetime(2014, 1, 1),
            date_to=datetime(2016, 12, 31),
            )

        self.inactive_committee_participant = self.create_committee_membership(
            self.committee,
            'inactive_committee_participant',
            firstname=u'Pablo',
            lastname=u'Neruda',
            email='pablo-neruda@example.com',
            date_from=datetime(2010, 1, 1),
            date_to=datetime(2014, 12, 31),
            )

        self.empty_committee = self.register(
            'empty_committee',
            self.create_committee(
                title=u'Kommission f\xfcr Verkehr',
                repository_folder=self.repofolder1,
                group_id='committee_ver_group',
                group_title=u'Gruppe Kommission f\xfcr Verkehr',
                responsibles=[
                    self.administrator,
                    self.committee_responsible,
                    ],
                templates={
                    'agendaitem_list_template': self.sablon_template,
                    'protocol_header_template': self.sablon_template,
                    'excerpt_header_template': self.sablon_template,
                    'excerpt_suffix_template': self.sablon_template,
                    'paragraph_template': self.sablon_template,
                }
                ),
            )

        self.register_raw(
            'empty_committee_id',
            self.empty_committee.load_model().committee_id,
            )

        self.set_roles(
            self.empty_committee, self.meeting_user.getId(),
            ['CommitteeMember'])

        self.empty_committee.reindexObjectSecurity()

    @staticuid()
    def create_inbox(self):
        self.inbox = self.register('inbox', create(
            Builder('inbox')
            .titled(u'Eingangsk\xf6rbli')
            .having(
                id='eingangskorb',
                responsible_org_unit='fa',
                inbox_group=self.org_unit_fd.inbox_group,
                )
            ))

        # Enable inbox_policy placeful workflow
        inbox_policy_id = 'opengever_inbox_policy'
        self.inbox.manage_addProduct[
            'CMFPlacefulWorkflow'].manage_addWorkflowPolicyConfig()
        pwf_tool = api.portal.get_tool('portal_placeful_workflow')
        policy_config = pwf_tool.getWorkflowPolicyConfig(self.inbox)
        policy_config.setPolicyIn(inbox_policy_id, update_security=False)
        policy_config.setPolicyBelow(inbox_policy_id, update_security=False)

        self.register('inbox_document', create(
            Builder('document')
            .within(self.inbox)
            .titled(u'Dokument im Eingangsk\xf6rbli')
            .with_asset_file('text.txt')
            ))

        self.set_roles(self.inbox, self.secretariat_user.getId(),
                       ['Contributor', 'Editor', 'Reader'])

        inbox_forwarding = self.register('inbox_forwarding', create(
            Builder('forwarding')
            .within(self.inbox)
            .titled(u'F\xf6rw\xe4rding')
            .having(
                responsible_client=self.org_unit_fd.id(),
                responsible=self.regular_user.getId(),
                issuer=self.dossier_responsible.getId(),
                )
            ))

        self.register('inbox_forwarding_document', create(
            Builder('document')
            .within(inbox_forwarding)
            .titled(u'Dokument im Eingangsk\xf6rbliweiterleitung')
            .with_asset_file('text.txt')
            ))

        self.inbox.reindexObjectSecurity()

    @staticuid()
    def create_private_root(self):
        self.private_root = self.register('private_root', create(
            Builder('private_root')
            .titled(u'Private')
        ))

        # The id of the private_root needs to match the MEMBERSFOLDER_ID
        # and setting the id is not possible when using dexterity builder,
        # we use the id ad title and rename it after creation.
        self.private_root.title_de = 'Meine Ablage'

        # Enable opengever.private placeful workflow policy
        private_policy_id = 'opengever_private_policy'
        self.private_root.manage_addProduct[
            'CMFPlacefulWorkflow'].manage_addWorkflowPolicyConfig()
        pwf_tool = api.portal.get_tool('portal_placeful_workflow')
        policy_config = pwf_tool.getWorkflowPolicyConfig(self.private_root)
        policy_config.setPolicyIn(private_policy_id, update_security=False)
        policy_config.setPolicyBelow(private_policy_id, update_security=False)

    @staticuid()
    def create_private_folder(self):
        self.private_folder = self.register('private_folder', create(
            Builder('private_folder')
            .having(id=self.regular_user.getId())
            .within(self.private_root)
            ))

        self.private_dossier = self.register('private_dossier', create(
            Builder('private_dossier')
            .having(title=u'Mein Dossier 1')
            .within(self.private_folder)
            ))

        create(
            Builder('private_dossier')
            .having(title=u'Mein Dossier 2')
            .within(self.private_folder)
            )

        self.register('private_document', create(
            Builder('document')
            .within(self.private_dossier)
            .with_asset_file('vertragsentwurf.docx')
            ))

        self.register('private_mail', create(
            Builder('mail')
            .within(self.private_dossier)
        ))

        self.set_roles(
            self.private_folder, self.regular_user.getId(),
            ['Publisher',
             'Contributor',
             'Reader',
             'Owner',
             'Reviewer',
             'Editor'])

        self.private_folder.reindexObjectSecurity()

    @staticuid()
    def create_treaty_dossiers(self):
        self.dossier = self.register('dossier', create(
            Builder('dossier')
            .within(self.repofolder00)
            .titled(u'Vertr\xe4ge mit der kantonalen Finanzverwaltung')
            .having(
                description=u'Alle aktuellen Vertr\xe4ge mit der kantonalen '
                u'Finanzverwaltung sind hier abzulegen. Vertr\xe4ge vor 2016 '
                u'geh\xf6ren ins Archiv.',
                keywords=(
                    u'Finanzverwaltung',
                    u'Vertr\xe4ge',
                    ),
                start=date(2016, 1, 1),
                responsible=self.dossier_responsible.getId(),
                external_reference=u'qpr-900-9001-\xf7',
                )
            ))

        create(
            Builder('contact_participation')
            .for_contact(self.meier_ag)
            .for_dossier(self.dossier)
            .with_roles(['final-drawing'])
            )

        create(
            Builder('contact_participation')
            .for_contact(self.josef_buehler)
            .for_dossier(self.dossier)
            .with_roles(['final-drawing', 'participation'])
            )

        self.document = self.register('document', create(
            Builder('document')
            .within(self.dossier)
            .titled(u'Vertr\xe4gsentwurf')
            .having(
                delivery_date=datetime(2010, 1, 3),
                description=u'Wichtige Vertr\xe4ge',
                document_author=TEST_USER_ID,
                document_date=datetime(2010, 1, 3),
                document_type='contract',
                receipt_date=datetime(2010, 1, 3),
                keywords=(u'Wichtig', ),
                )
            .attach_file_containing(
                bumblebee_asset('example.docx').bytes(),
                u'vertragsentwurf.docx')
            ))

        with self.features('meeting'):
            proposal = self.register('proposal', create(
                Builder('proposal')
                .within(self.dossier)
                .having(
                    title=u'Vertr\xe4ge',
                    committee=self.committee.load_model(),
                    issuer=self.dossier_responsible.getId(),
                    description=u'F\xfcr weitere Bearbeitung bewilligen',
                    )
                .relate_to(self.document)
                .as_submitted()
                ))

            self.register_path(
                'submitted_proposal',
                proposal.load_model().submitted_physical_path.encode('utf-8'),
                )

            self.register('proposaldocument', create(
                Builder('document')
                .within(proposal)
                .titled(u'Kommentar zum Vertragsentwurf')
                .attach_file_containing(
                    'Komentar text',
                    u'vertr\xe4g sentwurf.docx',
                    )
                ))

            self.register('draft_proposal', create(
                Builder('proposal')
                .within(self.dossier)
                .having(
                    title=u'Antrag f\xfcr Kreiselbau',
                    committee=self.empty_committee.load_model(),
                    issuer=self.dossier_responsible.getId(),
                    )
                ))

            self.decided_proposal = create(
                Builder('proposal')
                .within(self.dossier)
                .having(
                    title=u'Initialvertrag f\xfcr Bearbeitung',
                    committee=self.committee.load_model(),
                    issuer=self.dossier_responsible.getId(),
                    )
                .as_submitted()
                )

            self.register_path(
                'decided_proposal',
                self.decided_proposal
                .load_model()
                .submitted_physical_path.encode('utf-8'),
                )

        subdossier = self.register('subdossier', create(
            Builder('dossier')
            .within(self.dossier)
            .titled(u'2016')
            .having(
                keywords=(u'Subkeyword', u'Subkeyw\xf6rd'),
                )
            ))

        self.register('subdossier2', create(
            Builder('dossier')
            .within(self.dossier)
            .titled(u'2015')
            ))

        subdocument = self.register('subdocument', create(
            Builder('document')
            .within(subdossier)
            .titled(u'\xdcbersicht der Vertr\xe4ge von 2016')
            .attach_file_containing(
                'Excel dummy content',
                u'tab\xe4lle.xlsx',
            )
            .relate_to([self.document])
            .having(keywords=(u'Wichtig', u'Subkeyword', ))
        ))

        subsubdossier = self.register('subsubdossier', create(
            Builder('dossier')
            .within(subdossier)
            .titled(u'Subsubdossier')
            .having(
                keywords=(u'Subsubkeyword', u'Subsubkeyw\xf6rd'),
            )
        ))

        self.register('subsubdocument', create(
            Builder('document')
            .within(subsubdossier)
            .titled(u'\xdcbersicht der Vertr\xe4ge von 2014')
            .attach_file_containing(
                'Excel dummy content',
                u'tab\xe4lle neu.xlsx',
            )
            .relate_to([self.document, subdocument])
        ))

        self.register('empty_document', create(
            Builder('document')
            .within(subdossier)
            .titled(u'L\xe4\xe4r')
            .having(preserved_as_paper=True,
                    keywords=(u'Subkeyword', ))
        ))

        self.register('removed_document', create(
            Builder('document')
            .within(self.dossier)
            .titled(u'W\xe4g')
            .removed()
        ))

    @staticuid()
    def create_tasks(self):
        self.task = self.register('task', create(
            Builder('task')
            .within(self.dossier)
            .titled(u'Vertragsentwurf \xdcberpr\xfcfen')
            .having(
                responsible_client=self.org_unit_fd.id(),
                responsible=self.regular_user.getId(),
                issuer=self.dossier_responsible.getId(),
                task_type='correction',
                deadline=date(2016, 11, 1),
            )
            .in_state('task-state-in-progress')
            .relate_to(self.document)
        ))

        self.register('subtask', create(
            Builder('task')
            .within(self.task)
            .titled(u'Rechtliche Grundlagen in Vertragsentwurf \xdcberpr\xfcfen')
            .having(
                responsible_client=self.org_unit_fd.id(),
                responsible=self.regular_user.getId(),
                issuer=self.dossier_responsible.getId(),
                task_type='correction',
                deadline=date(2016, 11, 1),
            )
            .in_state('task-state-resolved')
            .relate_to(self.document)
        ))

        self.register('taskdocument', create(
            Builder('document')
            .within(self.task)
            .titled(u'Feedback zum Vertragsentwurf')
            .attach_file_containing(
                'Feedback text',
                u'vertr\xe4g sentwurf.docx',
            )
        ))

        sequential_task = self.register('sequential_task', create(
            Builder('task')
            .within(self.dossier)
            .titled(u'Personaleintritt')
            .having(
                responsible_client=self.org_unit_fd.id(),
                responsible=self.regular_user.getId(),
                issuer=self.regular_user.getId(),
                task_type='direct-execution',
                deadline=date(2016, 11, 1),
            )
            .in_state('task-state-in-progress')
            .as_sequential_task()
        ))

        seq_subtask_1 = self.register('seq_subtask_1', create(
            Builder('task')
            .within(sequential_task)
            .titled(u'Mitarbeiter Dossier generieren')
            .having(
                responsible_client=self.org_unit_fd.id(),
                responsible=self.regular_user.getId(),
                issuer=self.secretariat_user.getId(),
                task_type='direct-execution',
                deadline=date(2016, 11, 1),
            )
            .in_state('task-state-open')
            .as_sequential_task()
        ))

        seq_subtask_2 = self.register('seq_subtask_2', create(
            Builder('task')
            .within(sequential_task)
            .titled(u'Arbeitsplatz vorbereiten')
            .having(
                responsible_client=self.org_unit_fd.id(),
                responsible=self.regular_user.getId(),
                issuer=self.secretariat_user.getId(),
                task_type='direct-execution',
                deadline=date(2016, 11, 1),
            )
            .in_state('task-state-planned')
            .as_sequential_task()
        ))

        seq_subtask_3 = self.register('seq_subtask_3', create(
            Builder('task')
            .within(sequential_task)
            .titled(u'Vorstellungsrunde bei anderen Mitarbeitern')
            .having(
                responsible_client=self.org_unit_fd.id(),
                responsible=self.regular_user.getId(),
                issuer=self.dossier_responsible.getId(),
                task_type='direct-execution',
                deadline=date(2016, 11, 1),
            )
            .in_state('task-state-planned')
            .as_sequential_task()
        ))

        subtasks = [seq_subtask_1, seq_subtask_2, seq_subtask_3]
        sequential_task.set_tasktemplate_order(subtasks)
        for task in subtasks:
            task.sync()

        self.register('expired_task', create(
            Builder('task')
            .within(self.expired_dossier)
            .titled(u'Vertr\xe4ge abschliessen')
            .having(
                responsible_client=self.org_unit_fd.id(),
                responsible=self.regular_user.getId(),
                issuer=self.dossier_responsible.getId(),
                task_type='correction',
                deadline=date(2000, 12, 31),
            )
            .in_state('task-state-resolved')
            .relate_to(self.expired_document)
        ))

        self.register('inactive_task', create(
            Builder('task')
            .within(self.inactive_dossier)
            .titled(u'Status \xdcberpr\xfcfen')
            .having(
                responsible_client=self.org_unit_fd.id(),
                responsible=self.regular_user.getId(),
                issuer=self.dossier_responsible.getId(),
                task_type='direct-execution',
                deadline=date(2016, 11, 1),
            )
            .in_state('task-state-in-progress')
            .relate_to(self.inactive_document)
        ))

        with self.features('meeting', ):
            meeting_task = self.register('meeting_task', create(
                Builder('task')
                .within(self.meeting_dossier)
                .titled(u'Programm \xdcberpr\xfcfen')
                .having(
                    responsible=self.dossier_responsible.getId(),
                    responsible_client=self.org_unit_fd.id(),
                    issuer=self.dossier_responsible.getId(),
                    task_type='correction',
                    deadline=date(2016, 11, 1),
                )
                .in_state('task-state-in-progress')
                .relate_to(self.meeting_document)
            ))

            self.register('meeting_subtask', create(
                Builder('task')
                .within(meeting_task)
                .titled(u'H\xf6rsaal reservieren')
                .having(
                    responsible_client=self.org_unit_fd.id(),
                    responsible=self.dossier_responsible.getId(),
                    issuer=self.dossier_responsible.getId(),
                    deadline=date(2016, 11, 1),
                )
                .in_state('task-state-resolved')
                .relate_to(self.meeting_document)
            ))

        self.register('info_task', create(
            Builder('task')
            .titled(u'Vertragsentw\xfcrfe 2018')
            .within(self.dossier)
            .having(
                task_type=u'information',
                responsible_client=self.org_unit_fd.id(),
                responsible=self.regular_user.getId(),
            )
            .relate_to(self.document)
        ))

        self.register('private_task', create(
            Builder('task')
            .titled(u'Diskr\xe4te Dinge')
            .within(self.dossier)
            .having(
                deadline=date(2020, 1, 1),
                is_private=True,
                issuer=self.dossier_responsible.getId(),
                responsible_client=self.org_unit_fd.id(),
                responsible=self.regular_user.getId(),
                task_type=u'direct-execution',
                text=u'L\xf6rem ipsum dolor sit amet, consectetur'
            )
            .relate_to(self.document)
            .in_state('task-state-in-progress')
        ))

        self.register('inbox_task', create(
            Builder('task')
            .titled(u're: Diskr\xe4te Dinge')
            .within(self.dossier)
            .having(
                deadline=date(2020, 1, 1),
                is_private=True,
                issuer=self.dossier_responsible.getId(),
                responsible_client=self.org_unit_fd.id(),
                responsible='inbox:fa',
                task_type=u'direct-execution',
                text=u'L\xf6rem ipsum dolor sit amet, consectetur'
            )
            .relate_to(self.document)
            .in_state('task-state-in-progress')
        ))

    @staticuid()
    def create_expired_dossier(self):
        self.expired_dossier = self.register('expired_dossier', create(
            Builder('dossier')
            .within(self.repofolder00)
            .titled(u'Abgeschlossene Vertr\xe4ge')
            .having(
                description=u'Abgeschlossene Vertr\xe4ge vor 2000.',
                keywords=(u'Vertr\xe4ge', ),
                start=date(1995, 1, 1),
                end=date(2000, 12, 31),
                responsible=self.dossier_responsible.getId(),
                )
            .in_state('dossier-state-resolved')
            ))

        self.expired_document = self.register('expired_document', create(
            Builder('document')
            .within(self.expired_dossier)
            .titled(u'\xdcbersicht der Vertr\xe4ge vor 2000')
            .attach_archival_file_containing('TEST', name=u'test.pdf')
            .with_dummy_content()
            ))

    @staticuid()
    def create_inactive_dossier(self):
        self.inactive_dossier = self.register('inactive_dossier', create(
            Builder('dossier')
            .within(self.repofolder00)
            .titled(u'Inaktive Vertr\xe4ge')
            .having(
                description=u'Inaktive Vertr\xe4ge von 2016.',
                keywords=(u'Vertr\xe4ge', ),
                start=date(2016, 1, 1),
                end=date(2016, 12, 31),
                responsible=self.dossier_responsible.getId(),
                )
            .in_state('dossier-state-inactive')
            ))

        self.inactive_document = self.register('inactive_document', create(
            Builder('document')
            .within(self.inactive_dossier)
            .titled(u'\xdcbersicht der Inaktiven Vertr\xe4ge von 2016')
            .attach_file_containing('Excel dummy content', u'tab\xe4lle.xlsx')
            ))

    @staticuid()
    def create_offered_dossiers(self):
        self.offered_dossier_to_archive = self.register('offered_dossier_to_archive', create(
            Builder('dossier')
            .within(self.repofolder00)
            .titled(u'Hannah Baufrau')
            .having(
                description=u'Anstellung Hannah Baufrau.',
                keywords=(u'Wichtig', ),
                start=date(2000, 1, 1),
                end=date(2000, 1, 31),
                responsible=self.dossier_responsible.getId(),
                archival_value=ARCHIVAL_VALUE_WORTHY,
                )
            .in_state('dossier-state-resolved')
            ))

        self.offered_dossier_for_sip = self.register('offered_dossier_for_sip', create(
            Builder('dossier')
            .within(self.repofolder00)
            .titled(u'Dossier for SIP')
            .having(
                start=date(1997, 1, 1),
                end=date(1997, 1, 31),
                responsible=self.dossier_responsible.getId(),
                archival_value=ARCHIVAL_VALUE_WORTHY,
                )
            .in_state('dossier-state-resolved')
            ))

        self.offered_dossier_to_destroy = self.register('offered_dossier_to_destroy', create(
            Builder('dossier')
            .within(self.repofolder00)
            .titled(u'Hans Baumann')
            .having(
                description=u'Bewerbung Hans Baumann.',
                start=date(2000, 1, 1),
                end=date(2000, 1, 15),
                responsible=self.dossier_responsible.getId(),
                archival_value=ARCHIVAL_VALUE_UNWORTHY,
                )
            .in_state('dossier-state-inactive')
            ))

    @staticuid()
    def create_disposition(self):
        self.disposition = self.register('disposition', create(
            Builder('disposition')
            .titled(u'Angebot 31.8.2016')
            .having(dossiers=[self.offered_dossier_to_archive,
                              self.offered_dossier_to_destroy])
            .within(self.repofolder00)))

    @staticuid()
    def create_disposition_with_sip(self):
        self.disposition_with_sip = self.register('disposition_with_sip', create(
            Builder('disposition')
            .titled(u'Angebot 30.12.1997')
            .having(dossiers=[self.offered_dossier_for_sip])
            .in_state('disposition-state-appraised')
            .within(self.repofolder00)))

        api.content.transition(self.disposition_with_sip,
                               transition='disposition-transition-dispose')

    @staticuid()
    def create_shadow_document(self):
        with self.features('oneoffixx'):
            shadow_document = self.register('shadow_document', create(
                Builder('document')
                .within(self.dossier)
                .titled(u'Sch\xe4ttengarten')
                .as_shadow_document(),
                ))
            shadow_document_annotations = IAnnotations(shadow_document)
            shadow_document_annotations['template-id'] = '2574d08d-95ea-4639-beab-3103fe4c3bc7'
            shadow_document_annotations['languages'] = [2055]
            shadow_document_annotations['content_type'] = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'  # noqa

    @staticuid()
    def create_resolvable_dossier(self):
        self.resolvable_dossier = self.register('resolvable_dossier', create(
            Builder('dossier')
            .within(self.repofolder00)
            .titled(u'A resolvable main dossier')
            .having(
                start=date(2016, 1, 1),
                responsible=self.dossier_responsible.getId(),
            )
        ))

        self.resolvable_subdossier = self.register('resolvable_subdossier', create(
            Builder('dossier')
            .within(self.resolvable_dossier)
            .titled(u'Resolvable Subdossier')
            .having(
                start=date(2016, 1, 1),
                responsible=self.dossier_responsible.getId(),
            )
        ))

        self.resolvable_document = self.register('resolvable_document', create(
            Builder('document')
            .within(self.resolvable_subdossier)
            .titled(u'Umbau B\xe4rengraben')
            .having(
                document_date=datetime(2010, 1, 3),
            )
            .attach_file_containing(
                bumblebee_asset('example.docx').bytes(),
                u'vertragsentwurf.docx')
        ))

    @staticuid()
    def create_empty_dossier(self):
        self.register('empty_dossier', create(
            Builder('dossier')
            .within(self.repofolder00)
            .titled(u'An empty dossier')
            .having(
                start=date(2016, 1, 1),
                responsible=self.dossier_responsible.getId(),
                )
            ))

    @staticuid()
    def create_protected_dossiers(self):
        protected_dossier = self.register('protected_dossier', create(
            Builder('dossier')
            .within(self.repofolder00)
            .titled(u'Luftsch\xfctze')
            .having(
                description=u'Lichtbogen-L\xf6schkammern usw.',
                responsible=self.dossier_responsible.getId(),
                start=date(2016, 1, 1),
                )
            ))
        protected_dossier.__ac_local_roles_block__ = True
        protected_dossier.reindexObjectSecurity()
        protected_dossier.reindexObject(idxs=['blocked_local_roles'])

        self.register('protected_document', create(
            Builder('document')
            .within(protected_dossier)
            .titled(u'T\xfcrmli')
            .having(
                document_date=datetime(2010, 1, 3),
                document_author=TEST_USER_ID,
                )
            .attach_file_containing(
                bumblebee_asset('example.docx').bytes(),
                u'bauplan.docx')
            ))

        protected_dossier_with_task = self.register('protected_dossier_with_task', create(
            Builder('dossier')
            .within(self.repofolder00)
            .titled(u'Zu allem \xdcbel')
            .having(
                description=u'Schl\xe4cht',
                responsible=self.dossier_responsible.getId(),
                start=date(2016, 1, 1),
                )
            ))
        protected_dossier_with_task.__ac_local_roles_block__ = True
        protected_dossier_with_task.reindexObjectSecurity()
        protected_dossier_with_task.reindexObject(idxs=['blocked_local_roles'])

        protected_document_with_task = self.register('protected_document_with_task', create(
            Builder('document')
            .within(protected_dossier_with_task)
            .titled(u'Das kleinere \xdcbel')
            .having(
                document_date=datetime(2010, 1, 3),
                document_author=TEST_USER_ID,
                )
            .attach_file_containing(
                bumblebee_asset('example.docx').bytes(),
                u'kunststuck.docx')
            ))

        self.register('task_in_protected_dossier', create(
            Builder('task')
            .within(protected_dossier_with_task)
            .titled(u'Ein notwendiges \xdcbel')
            .having(
                responsible_client=self.org_unit_fd.id(),
                responsible=self.regular_user.getId(),
                issuer=self.dossier_responsible.getId(),
                task_type='correction',
                deadline=date(2016, 11, 1),
                )
            .in_state('task-state-in-progress')
            .relate_to(protected_document_with_task)
            ))

    @staticuid()
    def create_emails(self):
        self.register('mail_eml', create(
            Builder("mail")
            .with_message(MAIL_DATA)
            .within(self.dossier)
            ))

        class MockMsg2MimeTransform(object):

            def transform(self, data):
                return 'mock-eml-body'

        command = CreateEmailCommand(
            self.dossier,
            'testm\xc3\xa4il.msg',
            'mock-msg-body',
            transform=MockMsg2MimeTransform(),
            )

        self.register('mail_msg', command.execute())

    @staticuid()
    def create_meetings(self):
        self.meeting_dossier = self.register('meeting_dossier', create(
            Builder('meeting_dossier')
            .within(self.repofolder00)
            .titled(u'Sitzungsdossier 9/2017')
            .having(
                start=date(2016, 9, 12),
                keywords=(u'Finanzverwaltung', u'Vertr\xe4ge'),
                responsible=self.committee_responsible.getId(),
                )
            ))

        create(
            Builder('contact_participation')
            .for_contact(self.meier_ag)
            .for_dossier(self.meeting_dossier)
            .with_roles(['final-drawing'])
            )

        create(
            Builder('contact_participation')
            .for_contact(self.josef_buehler)
            .for_dossier(self.meeting_dossier)
            .with_roles(['final-drawing', 'participation'])
            )

        self.meeting_document = self.register('meeting_document', create(
            Builder('document')
            .within(self.meeting_dossier)
            .titled(u'Programm')
            .having(
                document_date=datetime(2016, 12, 1),
                document_author=TEST_USER_ID,
                )
            .with_asset_file('text.txt')
            ))

        self.meeting = create(
            Builder('meeting')
            .having(
                title=u'9. Sitzung der Rechnungspr\xfcfungskommission',
                committee=self.committee.load_model(),
                location=u'B\xfcren an der Aare',
                start=datetime(2016, 9, 12, 15, 30, tzinfo=pytz.UTC),
                end=datetime(2016, 9, 12, 17, 0, tzinfo=pytz.UTC),
                presidency=self.committee_president,
                secretary=self.committee_secretary,
                participants=[
                    self.committee_participant_1,
                    self.committee_participant_2,
                    ],
                )
            .link_with(self.meeting_dossier)
            )

        create_session().flush()  # trigger id generation, part of path

        self.register_path(
            'meeting',
            self.meeting.physical_path.encode('utf-8'),
            )

        decided_meeting_dossier = self.register(
            'decided_meeting_dossier', create(
                Builder('meeting_dossier')
                .within(self.repofolder00)
                .titled(u'Sitzungsdossier 8/2017')
                .having(
                    start=date(2016, 8, 17),
                    responsible=self.committee_responsible.getId(),
                    )
                ))

        self.decided_meeting = create(
            Builder('meeting')
            .having(
                title=u'8. Sitzung der Rechnungspr\xfcfungskommission',
                committee=self.committee.load_model(),
                location=u'B\xfcren an der Aare',
                start=datetime(2016, 7, 17, 15, 30, tzinfo=pytz.UTC),
                end=datetime(2016, 7, 17, 16, 30, tzinfo=pytz.UTC),
                presidency=self.committee_president,
                secretary=self.committee_secretary,
                participants=[
                    self.committee_participant_1,
                    self.committee_participant_2,
                    ],
                )
            .link_with(decided_meeting_dossier)
            )

        create_session().flush()  # trigger id generation, part of path

        self.register_path(
            'decided_meeting',
            self.decided_meeting.physical_path.encode('utf-8'),
            )

        self.decided_meeting.schedule_proposal(
            self.decided_proposal.load_model(),
            )
        create_session().flush()  # trigger workflow state default
        for agenda_item in self.decided_meeting.agenda_items:
            agenda_item.close()
            if agenda_item.has_proposal:
                excerpt = agenda_item.generate_excerpt(agenda_item.get_title())
                agenda_item.return_excerpt(excerpt)

        self.decided_meeting.close()

        closed_meeting_dossier = self.register(
            'closed_meeting_dossier', create(
                Builder('meeting_dossier')
                .within(self.repofolder00)
                .titled(u'Sitzungsdossier 7/2017')
                .having(
                    start=date(2016, 7, 17),
                    responsible=self.committee_responsible.getId(),
                    relatedDossier=[self.dossier, self.meeting_dossier],
                    )
                ))

        self.closed_meeting = create(
            Builder('meeting')
            .having(
                title=u'7. Sitzung der Rechnungspr\xfcfungskommission',
                committee=self.committee.load_model(),
                location=u'B\xfcren an der Aare',
                start=datetime(2015, 7, 17, 15, 30, tzinfo=pytz.UTC),
                end=datetime(2015, 7, 17, 16, 30, tzinfo=pytz.UTC),
                presidency=self.committee_president,
                secretary=self.committee_secretary,
                participants=[
                    self.committee_participant_1,
                    self.committee_participant_2,
                    ],
                )
            .link_with(closed_meeting_dossier)
            )

        create_session().flush()  # trigger id generation, part of path

        self.cancelled_meeting_dossier = self.register(
            'cancelled_meeting_dossier', create(
                Builder('meeting_dossier')
                .within(self.repofolder00)
                .titled(u'Sitzungsdossier 10/2016')
                .having(
                    start=date(2016, 10, 17),
                    responsible=self.committee_responsible.getId(),
                    )
                ))

        self.cancelled_meeting = create(
            Builder('meeting')
            .having(
                title=u'Stornierte Sitzung der Rechnungspr\xfcfungskommission',
                committee=self.committee.load_model(),
                workflow_state='cancelled',
                location=u'B\xfcren an der Aare',
                start=datetime(2016, 10, 17, 13, 30, tzinfo=pytz.UTC),
                end=datetime(2016, 10, 17, 14, 30, tzinfo=pytz.UTC),
                presidency=self.committee_president,
                secretary=self.committee_secretary,
                participants=[
                    self.committee_participant_1,
                    self.committee_participant_2,
                    ],
                )
            .link_with(self.cancelled_meeting_dossier)
            )

        create_session().flush()  # trigger id generation, part of path

        self.register_path(
            'cancelled_meeting',
            self.cancelled_meeting.physical_path.encode('utf-8'),
            )

    @contextmanager
    def freeze_at_hour(self, hour, tick_length=2):
        """Freeze the time when creating content with builders, so that
        we can rely on consistent creation times.
        Since we can sort consistently when all objects have the exact same
        creation times we need to move the clock forward whenever things are
        created, using ftw.builder's ticking creator in combination with a
        frozen clock.

        In order to be able to insert new objects in the fixture without
        mixing up all timestamps, we group the builders and let each group
        start at a given hour, moving the clock two minutes for each builder.
        We move it two minutes because the catalog rounds times sometimes to
        minute precision and we want to be more precise.
        """
        start = datetime(2016, 8, 31, hour, 1, 33, tzinfo=pytz.UTC)
        end = start + timedelta(hours=1)
        with freeze(start) as clock:
            with ticking_creator(clock, minutes=tick_length):
                with time_based_intids():
                    yield

            assert datetime.now(pytz.UTC) < end, (
                'The context self.freeze_at_hour({}) creates too many objects '
                'with ftw.builder, leading to a time overlap with '
                'self.freeze_at_hour({}).').format(hour, hour + 1)

    def register(self, attrname, obj):
        """Add an object to the lookup table so that it can be accessed from
        within the name under the attribute with name ``attrname``.
        Return the object for chaining convenience.
        """
        self.register_path(attrname, '/'.join(obj.getPhysicalPath()))
        return obj

    def register_path(self, attrname, path):
        """Add an object to the lookup table by path.
        """
        portal_path = '/'.join(api.portal.get().getPhysicalPath())
        if path.startswith(portal_path):
            path = path[len(portal_path):].lstrip('/')
        if path in self._registered_paths:
            raise ValueError('Trying to double register {}!'.format(path))
        self._lookup_table[attrname] = ('object', path)
        self._registered_paths.add(path)

    def register_url(self, attrname, url):
        """Add an object to the lookup table by url.

        The url can be generated based on the `public_url` of the
        `AdminUnit` used for testing.

        It can also be generated by calling `absolute_url` on a plone content
        type.
        """
        if url.startswith(self.admin_unit.public_url):
            url = url[len(self.admin_unit.public_url):]

        elif url.startswith(api.portal.get().absolute_url()):
            url = url[len(api.portal.get().absolute_url()):]

        url = url.lstrip('/')  # sanitize

        self.register_path(attrname, url)

    def register_raw(self, attrname, value):
        """Register a raw value in the lookup table for later lookup.
        The value must be JSON compatible.
        """
        self._lookup_table[attrname] = ('raw', value)

    def create_user(
            self,
            attrname,
            firstname,
            lastname,
            globalroles=(),
            group=None,
            **kwargs
        ):
        """Create an OGDS user and a Plone user.
        The user is member of the current org unit user group.
        The ``attrname`` is the attribute name used to access this user
        from within tests.
        """
        globalroles = ['Member'] + list(globalroles)
        builder = (
            Builder('user')
            .named(firstname, lastname)
            .with_roles(*globalroles)
            .in_groups(self.org_unit_fd.users_group_id)
            )

        builder.update_properties()  # updates builder.userid
        email = '{}@gever.local'.format(builder.userid)
        plone_user = create(builder.with_email(email))

        create(
            Builder('ogds_user')
            .id(plone_user.getId())
            .having(firstname=firstname, lastname=lastname, email=email)
            .assign_to_org_units([self.org_unit_fd])
            .in_group(group)
            .having(**kwargs)
            )

        # Use a static bumblebee user salt so that access tokens are predictable
        # when the time is frozen.
        store = IBumblebeeUserSaltStore(api.portal.get())
        store._get_storage()[plone_user.getId()] = 'static-salt-for-{}'.format(plone_user.getId())

        self._lookup_table[attrname] = ('user', plone_user.getId())
        return plone_user

    def create_committee_membership(
            self,
            committee,
            member_id_register_name,
            firstname,
            lastname,
            email,
            date_from,
            date_to,
        ):
        member = create(
            Builder('member')
            .having(firstname=firstname, lastname=lastname, email=email)
            )

        create(
            Builder('membership')
            .having(
                committee=committee,
                member=member,
                date_from=date_from,
                date_to=date_to,
                )
            )

        create_session().flush()  # trigger id generation, part of path

        self.register_url(
            member_id_register_name,
            member.get_url(self.committee_container).encode('utf-8'),
            )

        return member

    def create_committee(
            self,
            title,
            repository_folder,
            group_id,
            group_title,
            responsibles,
            templates=None,
        ):
        if templates is None:
            templates = {}
        # XXX I would have expected the commitee builder to do all of that.
        ogds_members = map(
            ogds_service().find_user,
            map(methodcaller('getId'), responsibles),
            )

        create(
            Builder('ogds_group')
            .having(
                groupid=group_id,
                users=ogds_members,
                )
            )

        create(
            Builder('group')
            .with_groupid(group_id)
            .having(title=group_title)
            .with_members(*responsibles)
            )

        committee = create(
            Builder('committee')
            .titled(title)
            .within(self.committee_container)
            .with_default_period()
            .having(
                ad_hoc_template=self.proposal_template,
                repository_folder=repository_folder,
                group_id=group_id,
                **templates
                )
            )

        return committee

    def create_workspace_root(self):
        self.workspace_root = self.register('workspace_root', create(
            Builder('workspace_root')
            .having(
                id=u'workspaces',
                title_de=u'Teamr\xe4ume',
                title_fr=u'Espace partag\xe9',
                )
            ))

        self.set_roles(
            self.workspace_root, self.workspace_owner.getId(),
            ['WorkspacesUser', 'WorkspacesCreator'])
        self.set_roles(
            self.workspace_root, self.workspace_admin.getId(),
            ['WorkspacesUser', 'WorkspacesCreator'])
        self.set_roles(
            self.workspace_root, self.workspace_member.getId(),
            ['WorkspacesUser'])
        self.set_roles(
            self.workspace_root, self.workspace_guest.getId(),
            ['WorkspacesUser'])
        self.workspace_root.reindexObjectSecurity()

    def create_workspace(self):
        self.workspace = self.register('workspace', create(
            Builder('workspace')
            .titled(u'A Workspace')
            .having(description=u'A Workspace description')
            .within(self.workspace_root)
            ))

        RoleAssignmentManager(self.workspace).reset([
            InvitationRoleAssignment(
                self.workspace_admin.id, ['WorkspaceAdmin'], self.workspace),
            InvitationRoleAssignment(
                self.workspace_member.id, ['WorkspaceMember'], self.workspace),
            InvitationRoleAssignment(
                self.workspace_guest.id, ['WorkspaceGuest'], self.workspace)
        ])

        self.workspace_folder = self.register('workspace_folder', create(
            Builder('workspace folder')
            .titled(u'WS F\xc3lder')
            .having(description=u'A Workspace folder description')
            .within(self.workspace)
            ))

    def create_todos(self):
        self.todolist_general = self.register('todolist_general', create(
            Builder('todolist')
            .titled(u'Allgemeine Informationen')
            .within(self.workspace)
        ))

        self.todolist_introduction = self.register(
            'todolist_introduction', create(
                Builder('todolist')
                .titled(u'Projekteinf\xfchrung')
                .within(self.workspace)
            ))

        self.todo = self.register('todo', create(
            Builder('todo')
            .titled(u'Fix user login')
            .having(
                text=u"Authentication is no longer possible.",
                deadline=date(2016, 9, 1),
                completed=False)
            .within(self.workspace)
            ))

        self.assigned_todo = self.register('assigned_todo', create(
            Builder('todo')
            .titled(u'Go live')
            .having(
                deadline=date(2016, 12, 1),
                responsible=self.workspace_member.getId(),
                completed=False)
            .within(self.todolist_introduction)
            ))

        self.completed_todo = self.register('completed_todo', create(
            Builder('todo')
            .titled(u'Cleanup installation')
            .having(
                text=u"Do some cleanups",
                deadline=date(2016, 9, 2),
                responsible=self.workspace_member.getId(),
                completed=True)
            .within(self.todolist_introduction)
        ))

    @contextmanager
    def login(self, user):
        old_manager = getSecurityManager()

        try:
            try:
                login(getSite(), user.getId())
            # XXX - Allow (early) lookups from the Zope acl_users as well
            except ValueError:
                login(getSite().getPhysicalRoot(), user.getId())
            yield

        finally:
            setSecurityManager(old_manager)

    @contextmanager
    def feature(self, feature):
        if feature not in FEATURE_FLAGS:
            raise ValueError('Invalid {!r}'.format(feature))

        before = api.portal.get_registry_record(FEATURE_FLAGS[feature])
        api.portal.set_registry_record(FEATURE_FLAGS[feature], True)

        try:
            yield

        finally:
            api.portal.set_registry_record(FEATURE_FLAGS[feature], before)

    def features(self, *features):
        return nested(*map(self.feature, features))
