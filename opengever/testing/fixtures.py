from AccessControl.SecurityManagement import getSecurityManager
from AccessControl.SecurityManagement import setSecurityManager
from contextlib import contextmanager
from contextlib import nested
from datetime import date
from datetime import datetime
from datetime import timedelta
from ftw.builder import Builder
from ftw.builder import create
from ftw.builder import ticking_creator
from ftw.bumblebee.tests.helpers import asset as bumblebee_asset
from ftw.testing import freeze
from ftw.testing import staticuid
from functools import wraps
from opengever.base.command import CreateEmailCommand
from opengever.base.model import create_session
from opengever.mail.tests import MAIL_DATA
from opengever.meeting.proposalhistory import BaseHistoryRecord
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
from zope.component.hooks import getSite
import logging
import pytz


class OpengeverContentFixture(object):
    """Provide a basic content fixture for integration tests."""

    def __init__(self):
        start = time()
        self._logger = logger = logging.getLogger('opengever.testing')
        self._lookup_table = {
            'manager': ('user', SITE_OWNER_NAME),
            }

        with self.freeze_at_hour(4):
            self.create_units()

        with self.freeze_at_hour(5):
            self.create_users()

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

        with self.freeze_at_hour(15):
            with self.login(self.dossier_responsible):
                self.create_emails()

        with self.freeze_at_hour(16):
            with self.login(self.committee_responsible):
                with self.features('meeting'):
                    self.create_meetings()

        with self.freeze_at_hour(17):
            self.create_private_root()

            with self.login(self.regular_user):
                self.create_private_folder()

        with self.freeze_at_hour(18):
            with self.login(self.workspace_owner):
                self.create_workspace()

        logger.info('(fixture setup in %ds) ', round(time() - start, 3))

    def __call__(self):
        return self._lookup_table

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

        self.org_unit = create(
            Builder('org_unit')
            .id('fa')
            .having(
                title=u'Finanzamt',
                admin_unit=self.admin_unit,
                )
            .with_default_groups()
            .as_current_org_unit()
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
            group=self.org_unit.inbox_group,
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
                org_unit=self.org_unit,
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
                org_unit=self.org_unit,
                )
            )

    @staticuid()
    def create_repository_tree(self):
        self.root = self.register('repository_root', create(
            Builder('repository_root')
            .having(
                title_de=u'Ordnungssystem',
                title_fr=u'Syst\xe8me de classement',
                )
            ))

        self.root.manage_setLocalRoles(
            self.org_unit.users_group_id,
            ['Reader', 'Contributor', 'Editor'],
            )

        self.root.manage_setLocalRoles(
            self.secretariat_user.getId(),
            ['Reviewer', 'Publisher'],
            )

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

        self.repofolder0.manage_setLocalRoles(
            self.dossier_manager.getId(),
            ['DossierManager'],
            )

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

        self.contactfolder.manage_setLocalRoles(
            self.org_unit.users_group_id,
            ['Reader'],
            )

        self.contactfolder.manage_setLocalRoles(
            self.org_unit.users_group_id,
            ['Reader', 'Contributor', 'Editor'],
            )

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

        self.templates.manage_setLocalRoles(self.org_unit.users_group_id, ['Reader'])
        self.templates.manage_setLocalRoles(self.administrator.getId(), ['Reader', 'Contributor', 'Editor'])
        self.templates.manage_setLocalRoles(self.dossier_responsible.getId(), ['Reader', 'Contributor', 'Editor'])
        self.templates.reindexObjectSecurity()

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

        with self.features('doc-properties', ):
            self.register('docprops_template', create(
                Builder('document')
                .titled(u'T\xc3\xb6mpl\xc3\xb6te Mit')
                .with_asset_file('with_custom_properties.docx')
                .with_modification_date(datetime(2010, 12, 28))
                .within(self.templates)
                ))

        with self.features('meeting', ):
            self.meeting_template = self.register('meeting_template', create(
                Builder('meetingtemplate')
                .titled(u'Meeting T\xc3\xb6mpl\xc3\xb6te')
                .within(self.templates)
                ))
            create(
                Builder('paragraphtemplate')
                .titled(u'Begr\xfcssung')
                .having(position=1)
                .within(self.meeting_template)
                )
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

        self.subdossiertemplate = self.register('subdossiertemplate', create(
            Builder('dossiertemplate')
            .titled(u'Anfragen')
            .within(self.dossiertemplate)
            ))

    @staticuid()
    def create_subtemplates(self):
        subtemplates = self.register('subtemplates', create(
            Builder('templatefolder')
            .titled(u'Vorlagen neu')
            .having(id='vorlagen-neu')
            .within(self.templates)
            ))
        subtemplates.manage_setLocalRoles(self.org_unit.users_group_id, ['Reader'])
        subtemplates.manage_setLocalRoles(self.administrator.getId(), ['Reader', 'Contributor', 'Editor'])
        subtemplates.manage_setLocalRoles(self.dossier_responsible.getId(), ['Reader', 'Contributor', 'Editor'])
        subtemplates.reindexObjectSecurity()

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
            .having(
                agendaitem_list_template=self.sablon_template,
                protocol_header_template=self.sablon_template,
                excerpt_header_template=self.sablon_template,
                excerpt_suffix_template=self.sablon_template,
                paragraph_template=self.sablon_template,
                )
            ))

        self.committee_container.manage_setLocalRoles(
            self.committee_responsible.getId(),
            ['MeetingUser'],
            )

        self.committee_container.manage_setLocalRoles(
            self.meeting_user.getId(),
            ['MeetingUser'],
            )

        self.committee_container.manage_setLocalRoles(
            self.administrator.getId(),
            ['CommitteeAdministrator'],
            )

        self.committee_container.reindexObjectSecurity()

        self.committee = self.register('committee', self.create_committee(
            title=u'Rechnungspr\xfcfungskommission',
            repository_folder=self.repofolder1,
            group_id='committee_rpk_group',
            group_title=u'Gruppe Rechnungspr\xfcfungskommission',
            responsibles=[
                self.administrator,
                self.committee_responsible,
                ]
            ))

        self.register_raw(
            'committee_id',
            self.committee.load_model().committee_id,
            )

        self.committee.manage_setLocalRoles(
            self.meeting_user.getId(),
            ['CommitteeMember'],
            )

        self.committee_president = self.create_committee_membership(
            self.committee,
            'committee_president',
            firstname=u'Heidrun',
            lastname=u'Sch\xf6ller',
            email='h.schoeller@web.de',
            date_from=datetime(2014, 1, 1),
            date_to=datetime(2016, 12, 31),
            )

        self.committee_secretary = create(
            Builder('ogds_user')
            .id('committee.secretary')
            .having(firstname=u'C\xf6mmittee', lastname='Secretary', email='committee.secretary@example.com')
            .assign_to_org_units([self.org_unit])
            )

        self.committee_participant_1 = self.create_committee_membership(
            self.committee,
            'committee_participant_1',
            firstname=u'Gerda',
            lastname=u'W\xf6lfl',
            email='g.woelfl@hotmail.com',
            date_from=datetime(2014, 1, 1),
            date_to=datetime(2016, 12, 31),
            )

        self.committee_participant_2 = self.create_committee_membership(
            self.committee,
            'committee_participant_2',
            firstname=u'Jens',
            lastname=u'Wendler',
            email='jens-wendler@gmail.com',
            date_from=datetime(2014, 1, 1),
            date_to=datetime(2016, 12, 31),
            )

        self.inactive_committee_participant = self.create_committee_membership(
            self.committee,
            'inactive_committee_participant',
            firstname=u'Pablo',
            lastname=u'Neruda',
            email='pablo-neruda@gmail.com',
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
                ),
            )

        self.register_raw(
            'empty_committee_id',
            self.empty_committee.load_model().committee_id,
            )

        self.empty_committee.manage_setLocalRoles(
            self.meeting_user.getId(),
            ['CommitteeMember'],
            )

        self.empty_committee.reindexObjectSecurity()

    @staticuid()
    def create_inbox(self):
        self.inbox = self.register('inbox', create(
            Builder('inbox')
            .titled(u'Eingangsk\xf6rbli')
            .having(
                id='eingangskorb',
                responsible_org_unit='fa',
                inbox_group=self.org_unit.inbox_group,
                )
            ))

        self.register('inbox_document', create(
            Builder('document')
            .within(self.inbox)
            .titled(u'Dokument im Eingangsk\xf6rbli')
            .with_asset_file('text.txt')
            ))

        self.inbox.manage_setLocalRoles(
            self.secretariat_user.getId(),
            ['Contributor', 'Editor', 'Reader'],
            )

        inbox_forwarding = self.register('inbox_forwarding', create(
            Builder('forwarding')
            .within(self.inbox)
            .titled(u'F\xf6rw\xe4rding')
            .having(
                responsible_client=self.org_unit.id(),
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

        self.private_folder.manage_setLocalRoles(
            self.regular_user.getId(),
            [
                'Publisher',
                'Contributor',
                'Reader',
                'Owner',
                'Reviewer',
                'Editor',
                ],
            )

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
                document_date=datetime(2010, 1, 3),
                document_author=TEST_USER_ID,
                document_type='contract',
                receipt_date=datetime(2010, 1, 3),
                delivery_date=datetime(2010, 1, 3),
                )
            .attach_file_containing(
                bumblebee_asset('example.docx').bytes(),
                u'vertragsentwurf.docx')
            ))

        self.task = self.register('task', create(
            Builder('task')
            .within(self.dossier)
            .titled(u'Vertragsentwurf \xdcberpr\xfcfen')
            .having(
                responsible_client=self.org_unit.id(),
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
            .titled(
                u'Rechtliche Grundlagen in Vertragsentwurf \xdcberpr\xfcfen',
                )
            .having(
                responsible_client=self.org_unit.id(),
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

        self.sequential_task = self.register('sequential_task', create(
            Builder('task')
            .within(self.dossier)
            .titled(u'Personaleintritt')
            .having(responsible_client=self.org_unit.id(),
                    responsible=self.regular_user.getId(),
                    issuer=self.regular_user.getId(),
                    task_type='direct-execution',
                    deadline=date(2016, 11, 1))
            .in_state('task-state-in-progress')
            .as_sequential_task()
        ))
        self.seq_subtask_1 = self.register('seq_subtask_1', create(
            Builder('task')
            .within(self.sequential_task)
            .titled(u'Mitarbeiter Dossier generieren')
            .having(responsible_client=self.org_unit.id(),
                    responsible=self.regular_user.getId(),
                    issuer=self.secretariat_user.getId(),
                    task_type='direct-execution',
                    deadline=date(2016, 11, 1))
            .in_state('task-state-open')
            .as_sequential_task()
        ))
        self.seq_subtask_2 = self.register('seq_subtask_2', create(
            Builder('task')
            .within(self.sequential_task)
            .titled(u'Arbeitsplatz vorbereiten')
            .having(responsible_client=self.org_unit.id(),
                    responsible=self.regular_user.getId(),
                    issuer=self.secretariat_user.getId(),
                    task_type='direct-execution',
                    deadline=date(2016, 11, 1))
            .in_state('task-state-planned')
            .as_sequential_task()
        ))
        self.seq_subtask_3 = self.register('seq_subtask_3', create(
            Builder('task')
            .within(self.sequential_task)
            .titled(u'Vorstellungsrunde bei anderen Mitarbeitern')
            .having(responsible_client=self.org_unit.id(),
                    responsible=self.regular_user.getId(),
                    issuer=self.dossier_responsible.getId(),
                    task_type='direct-execution',
                    deadline=date(2016, 11, 1))
            .in_state('task-state-planned')
            .as_sequential_task()
        ))

        subtasks = [self.seq_subtask_1, self.seq_subtask_2, self.seq_subtask_3]
        self.sequential_task.set_tasktemplate_order(subtasks)
        [task.sync() for task in subtasks]

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

            word_proposal = self.register('word_proposal', create(
                Builder('proposal')
                .within(self.dossier)
                .having(
                    title=u'\xc4nderungen am Personalreglement',
                    committee=self.committee.load_model(),
                    issuer=self.dossier_responsible.getId(),
                    )
                .relate_to(self.document)
                .with_proposal_file(assets.load('vertragsentwurf.docx'))
                .as_submitted()
                ))

            self.register_path(
                'submitted_word_proposal',
                word_proposal
                .load_model()
                .submitted_physical_path.encode('utf-8'),
                )

            self.register('draft_word_proposal', create(
                Builder('proposal')
                .within(self.dossier)
                .having(
                    title=u'\xdcberarbeitung der GAV',
                    committee=self.empty_committee.load_model(),
                    issuer=self.dossier_responsible.getId(),
                    )
                ))

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

        self.register('subdocument', create(
            Builder('document')
            .within(subdossier)
            .titled(u'\xdcbersicht der Vertr\xe4ge von 2016')
            .attach_file_containing(
                'Excel dummy content',
                u'tab\xe4lle.xlsx',
                )
            ))

    @staticuid()
    def create_expired_dossier(self):
        expired_dossier = self.register('expired_dossier', create(
            Builder('dossier')
            .within(self.repofolder00)
            .titled(u'Abgeschlossene Vertr\xe4ge')
            .having(
                description=u'Abgeschlossene Vertr\xe4ge vor 2000.',
                keywords=(u'Vertr\xe4ge'),
                start=date(1995, 1, 1),
                end=date(2000, 12, 31),
                responsible=self.dossier_responsible.getId(),
                )
            .in_state('dossier-state-resolved')
            ))

        expired_document = self.register('expired_document', create(
            Builder('document')
            .within(expired_dossier)
            .titled(u'\xdcbersicht der Vertr\xe4ge vor 2000')
            .attach_archival_file_containing('TEST', name=u'test.pdf')
            .with_dummy_content()
            ))

        self.register('expired_task', create(
            Builder('task')
            .within(expired_dossier)
            .titled(u'Vertr\xe4ge abschliessen')
            .having(
                responsible_client=self.org_unit.id(),
                responsible=self.regular_user.getId(),
                issuer=self.dossier_responsible.getId(),
                task_type='correction',
                deadline=date(2000, 12, 31),
                )
            .in_state('task-state-resolved')
            .relate_to(expired_document)
            ))

    @staticuid()
    def create_inactive_dossier(self):
        inactive_dossier = self.register('inactive_dossier', create(
            Builder('dossier')
            .within(self.repofolder00)
            .titled(u'Inaktive Vertr\xe4ge')
            .having(
                description=u'Inaktive Vertr\xe4ge von 2016.',
                keywords=(u'Vertr\xe4ge'),
                start=date(2016, 1, 1),
                end=date(2016, 12, 31),
                responsible=self.dossier_responsible.getId(),
                )
            .in_state('dossier-state-inactive')
            ))

        inactive_document = self.register('inactive_document', create(
            Builder('document')
            .within(inactive_dossier)
            .titled(u'\xdcbersicht der Inaktiven Vertr\xe4ge von 2016')
            .attach_file_containing('Excel dummy content', u'tab\xe4lle.xlsx')
            ))

        self.register('inactive_task', create(
            Builder('task')
            .within(inactive_dossier)
            .titled(u'Status \xdcberpr\xfcfen')
            .having(
                responsible_client=self.org_unit.id(),
                responsible=self.regular_user.getId(),
                issuer=self.dossier_responsible.getId(),
                task_type='direct-execution',
                deadline=date(2016, 11, 1),
                )
            .in_state('task-state-in-progress')
            .relate_to(inactive_document)
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
    def create_emails(self):
        self.mail_eml = self.register('mail_eml', create(
            Builder("mail")
            .with_message(MAIL_DATA)
            .within(self.dossier)
            ))

        self.register('mail', self.mail_eml)

        class MockMsg2MimeTransform(object):

            def transform(self, data):
                return 'mock-eml-body'

        command = CreateEmailCommand(
            self.dossier,
            'testm\xc3\xa4il.msg',
            'mock-msg-body',
            transform=MockMsg2MimeTransform(),
            )

        self.mail_msg = self.register('mail_msg', command.execute())

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

        meeting_task = self.register('meeting_task', create(
            Builder('task')
            .within(self.meeting_dossier)
            .titled(u'Programm \xdcberpr\xfcfen')
            .having(
                responsible=self.dossier_responsible.getId(),
                responsible_client=self.org_unit.id(),
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
                responsible_client=self.org_unit.id(),
                responsible=self.dossier_responsible.getId(),
                issuer=self.dossier_responsible.getId(),
                deadline=date(2016, 11, 1),
                )
            .in_state('task-state-resolved')
            .relate_to(self.meeting_document)
            ))

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
        for agenda_item in self.decided_meeting.agenda_items:
            agenda_item.close()
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
    def freeze_at_hour(self, hour):
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
            with ticking_creator(clock, minutes=2):
                with self.ticking_proposal_history(clock, seconds=1):
                    with time_based_intids():
                        yield

            assert datetime.now(pytz.UTC) < end, (
                'The context self.freeze_at_hour({}) creates too many objects '
                'with ftw.builder, leading to a time overlap with '
                'self.freeze_at_hour({}).').format(hour, hour + 1)

    @contextmanager
    def ticking_proposal_history(self, clock, **forward):
        """The proposal history entries must be unique.
        This context manager applies patches so that creating a proposal
        history record will move the freezed clock forward a bit.
        This context manager must not be nested.
        """
        marker_name = '_fixture_patched'

        if getattr(BaseHistoryRecord, marker_name, None):
            yield
            return

        original_init = BaseHistoryRecord.__init__

        @wraps(original_init)
        def patched_init(*args, **kwargs):
            result = original_init(*args, **kwargs)
            clock.forward(**forward)
            return result

        BaseHistoryRecord.__init__ = patched_init
        setattr(BaseHistoryRecord, marker_name, True)
        try:
            yield

        finally:
            BaseHistoryRecord.__init__ = original_init
            delattr(BaseHistoryRecord, marker_name)

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
        self._lookup_table[attrname] = ('object', path)

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
            .in_groups(self.org_unit.users_group_id)
            )

        builder.update_properties()  # updates builder.userid
        email = '{}@gever.local'.format(builder.userid)
        plone_user = create(builder.with_email(email))

        create(
            Builder('ogds_user')
            .id(plone_user.getId())
            .having(firstname=firstname, lastname=lastname, email=email)
            .assign_to_org_units([self.org_unit])
            .in_group(group)
            .having(**kwargs)
            )

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
        ):
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

        self.workspace_root.manage_setLocalRoles(
            self.workspace_owner.getId(),
            ['WorkspacesUser', 'WorkspacesCreator'],
            )

        self.workspace_root.manage_setLocalRoles(
            self.workspace_admin.getId(),
            ['WorkspacesUser', 'WorkspacesCreator'],
            )

        self.workspace_root.manage_setLocalRoles(
            self.workspace_member.getId(),
            ['WorkspacesUser'],
            )

        self.workspace_root.manage_setLocalRoles(
            self.workspace_guest.getId(),
            ['WorkspacesUser'],
            )

        self.workspace_root.reindexObjectSecurity()

    def create_workspace(self):
        self.workspace = self.register('workspace', create(
            Builder('workspace')
            .titled(u'A Workspace')
            .within(self.workspace_root)
            ))

        self.workspace.manage_setLocalRoles(
            self.workspace_admin.getId(),
            ['WorkspaceAdmin'],
            )

        self.workspace.manage_setLocalRoles(
            self.workspace_member.getId(),
            ['WorkspaceMember'],
            )

        self.workspace.manage_setLocalRoles(
            self.workspace_guest.getId(),
            ['WorkspaceGuest'],
            )
        self.workspace.reindexObjectSecurity()

        self.workspace_folder = self.register('workspace_folder', create(
            Builder('workspace folder')
            .having(
                title_de=u'WS F\xc3lder',
                title_fr=u'WS fichi\xe9r',
                )
            .within(self.workspace)
            ))

    @contextmanager
    def login(self, user):
        old_manager = getSecurityManager()

        try:
            login(getSite(), user.getId())
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
