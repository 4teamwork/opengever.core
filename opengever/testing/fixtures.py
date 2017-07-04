from AccessControl.SecurityManagement import getSecurityManager
from AccessControl.SecurityManagement import setSecurityManager
from contextlib import contextmanager
from datetime import date
from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.builder import ticking_creator
from ftw.testing import freeze
from ftw.testing import staticuid
from opengever.base.command import CreateEmailCommand
from opengever.mail.tests import MAIL_DATA
from opengever.ogds.base.utils import ogds_service
from operator import methodcaller
from plone.app.testing import login
from plone.app.testing import SITE_OWNER_NAME
from time import time
from zope.component.hooks import getSite


class OpengeverContentFixture(object):

    def __call__(self):
        start = time()
        self._lookup_table = {
            'manager': ('user', SITE_OWNER_NAME)}

        with self.freeze_at_hour(6):
            self.create_units()

        with self.freeze_at_hour(7):
            self.create_users()

        with self.freeze_at_hour(8):
            with self.login(self.administrator):
                self.create_repository_tree()
                self.create_templates()
                self.create_committees()

        with self.freeze_at_hour(14):
            with self.login(self.dossier_responsible):
                self.create_treaty_dossiers()

        with self.freeze_at_hour(15):
            with self.login(self.dossier_responsible):
                self.create_emails()

        end = time()
        print '(fixture setup in {}s) '.format(round(end-start, 3)),

        return self._lookup_table

    def create_units(self):
        self.admin_unit = create(
            Builder('admin_unit')
            .having(title=u'Hauptmandant',
                    unit_id=u'plone',
                    public_url='http://nohost/plone')
            .as_current_admin_unit())

        self.org_unit = create(
            Builder('org_unit')
            .id('fa')
            .having(title=u'Finanzamt',
                    admin_unit=self.admin_unit)
            .with_default_groups()
            .as_current_org_unit())

    def create_users(self):
        self.administrator = self.create_user(
            'administrator', u'Nicole', u'Kohler', ['Administrator'])
        self.dossier_responsible = self.create_user(
            'dossier_responsible', u'Robert', u'Ziegler')
        self.regular_user = self.create_user(
            'regular_user', u'K\xe4thi', u'B\xe4rfuss')
        self.secretariat_user = self.create_user(
            'secretariat_user', u'J\xfcrgen', u'K\xf6nig')

    @staticuid()
    def create_repository_tree(self):
        self.root = self.register('repository_root', create(
            Builder('repository_root')
            .having(title_de=u'Ordnungssystem',
                    title_fr=u'Syst\xe8me de classement')))
        self.root.manage_setLocalRoles(self.org_unit.users_group_id,
                                       ('Reader', 'Contributor', 'Editor'))
        self.root.manage_setLocalRoles(self.secretariat_user.getId(),
                                       ('Reviewer', 'Publisher'))
        self.root.reindexObjectSecurity()

        self.repofolder0 = self.register('branch_repofolder', create(
            Builder('repository').within(self.root)
            .having(title_de=u'F\xfchrung',
                    title_fr=u'Direction',
                    description=u'Alles zum Thema F\xfchrung.')))

        self.repofolder00 = self.register('leaf_repofolder', create(
            Builder('repository').within(self.repofolder0)
            .having(title_de=u'Vertr\xe4ge und Vereinbarungen',
                    title_fr=u'Contrats et accords')))

        self.repofolder1 = self.register('empty_repofolder', create(
            Builder('repository').within(self.root)
            .having(title_de=u'Rechnungspr\xfcfungskommission',
                    title_fr=u'Commission de v\xe9rification')))

    @staticuid()
    def create_templates(self):
        templates = self.register('templates', create(
            Builder('templatefolder')
            .titled(u'Vorlagen')
            .having(id='vorlagen')))

        self.sablon_template = self.register('sablon_template', create(
            Builder('sablontemplate')
            .within(templates)
            .with_asset_file('sablon_template.docx')))

    @staticuid()
    def create_committees(self):
        self.committee_container = self.register('committee_container', create(
            Builder('committee_container')
            .titled(u'Sitzungen')
            .having(protocol_template=self.sablon_template,
                    excerpt_template=self.sablon_template)))

        self.register('committee', self.create_committee(
            title=u'Rechnungspr\xfcfungskommission',
            repository_folder=self.repofolder1,
            group_id='committee_rpk_group',
            members=[self.administrator]))

    @staticuid()
    def create_treaty_dossiers(self):
        self.dossier = self.register('dossier', create(
            Builder('dossier').within(self.repofolder00)
            .titled(u'Vertr\xe4ge mit der kantonalen Finanzverwaltung')
            .having(description=u'Alle aktuellen Vertr\xe4ge mit der'
                    u' kantonalen Finanzverwaltung sind hier abzulegen.'
                    u' Vertr\xe4ge vor 2016 geh\xf6ren ins Archiv.',
                    keywords=(u'Finanzverwaltung', u'Vertr\xe4ge'),
                    start=date(2016, 1, 1),
                    responsible='hugo.boss')))

        document = self.register('document', create(
            Builder('document').within(self.dossier)
            .titled(u'Vertr\xe4gsentwurf')
            .attach_file_containing('Word dummy content',
                                    u'vertrasentwurf.docx')))

        task = self.register('task', create(
            Builder('task').within(self.dossier)
            .titled(u'Vertragsentwurf \xdcberpr\xfcfen')
            .having(responsible_client=self.org_unit.id(),
                    responsible=self.regular_user.getId(),
                    issuer=self.dossier_responsible.getId(),
                    task_type='correction',
                    deadline=date(2016, 11, 1))
            .in_state('task-state-in-progress')
            .relate_to(document)))

        self.register('subtask', create(
            Builder('task').within(task)
            .titled(u'Rechtliche Grundlagen in Vertragsentwurf \xdcberpr\xfcfen')
            .having(responsible_client=self.org_unit.id(),
                    responsible=self.regular_user.getId(),
                    issuer=self.dossier_responsible.getId(),
                    task_type='correction',
                    deadline=date(2016, 11, 1))
            .in_state('task-state-resolved')
            .relate_to(document)))

        self.register('taskdocument', create(
            Builder('document').within(task)
            .titled(u'Feedback zum Vertragsentwurf')
            .attach_file_containing('Feedback text',
                                    u'vertr\xe4g sentwurf.docx')))

        subdossier = self.register('subdossier', create(
            Builder('dossier').within(self.dossier).titled(u'2016')))

        self.register('subdocument', create(
            Builder('document').within(subdossier)
            .titled(u'\xdcbersicht der Vertr\xe4ge von 2016')
            .attach_file_containing('Excel dummy content', u'tab\xe4lle.xlsx')))

        self.register('archive_dossier', create(
            Builder('dossier').within(self.repofolder00)
            .titled(u'Archiv Vertr\xe4ge')
            .having(description=u'Archiv der Vertr\xe4ge vor 2016.',
                    keywords=(u'Finanzverwaltung', u'Vertr\xe4ge'),
                    start=date(2000, 1, 1),
                    end=date(2015, 12, 31),
                    responsible='hugo.boss')
            .in_state('dossier-state-resolved')))

    @staticuid()
    def create_emails(self):
        self.mail_eml = self.register('mail_eml', create(
            Builder("mail")
            .with_message(MAIL_DATA)
            .within(self.dossier)))

        class MockMsg2MimeTransform(object):

            def transform(self, data):
                return 'mock-eml-body'

        command = CreateEmailCommand(self.dossier,
                                     'testm\xc3\xa4il.msg',
                                     'mock-msg-body',
                                     transform=MockMsg2MimeTransform())
        self.mail_msg = self.register('mail_msg', command.execute())

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
        with freeze(datetime(2016, 8, 31, hour, 1, 33)) as clock:
            with ticking_creator(clock, minutes=2):
                yield

    def register(self, attrname, obj):
        """Add an object to the lookup table so that it can be accessed from
        within the name under the attribute with name ``attrname``.
        Return the object for chaining convenience.
        """
        self._lookup_table[attrname] = ('object', '/'.join(obj.getPhysicalPath()))
        return obj

    def create_user(self, attrname, firstname, lastname, globalroles=()):
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
            .in_groups(self.org_unit.users_group_id))

        builder.update_properties()  # updates builder.userid
        email = '{}@gever.local'.format(builder.userid)
        plone_user = create(builder.with_email(email))

        create(Builder('ogds_user')
               .id(plone_user.getId())
               .having(firstname=firstname, lastname=lastname, email=email)
               .assign_to_org_units([self.org_unit]))

        self._lookup_table[attrname] = ('user', plone_user.getId())
        return plone_user

    def create_committee(self, title, repository_folder, group_id, members):
        # XXX I would have expected the commitee builder to do all of that.
        ogds_members = map(ogds_service().find_user,
                           map(methodcaller('getId'), members))

        create(Builder('ogds_group')
               .having(groupid=group_id,
                       users=ogds_members))
        create(Builder('group')
               .with_groupid(group_id)
               .with_members(*members))
        return create(
            Builder('committee')
            .titled(title)
            .within(self.committee_container)
            .having(repository_folder=repository_folder,
                    group_id=group_id))

    @contextmanager
    def login(self, user):
        old_manager = getSecurityManager()
        try:
            login(getSite(), user.getId())
            yield
        finally:
            setSecurityManager(old_manager)
