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
from plone.app.testing import login
from time import time
from zope.component.hooks import getSite


class OpengeverContentFixture(object):

    def __call__(self):
        start = time()

        with self.freeze_at_hour(6):
            self.create_units()

        with self.freeze_at_hour(7):
            self.create_users()

        with self.freeze_at_hour(8):
            with self.login(self.administrator):
                self.create_repository_tree()

        with self.freeze_at_hour(9):
            with self.login(self.dossier_responsible):
                self.create_treaty_dossiers()

        end = time()
        print '(fixture setup in {}s) '.format(round(end-start, 3)),

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
            u'Nicole', u'Kohler', ['Administrator'])
        self.dossier_responsible = self.create_user(u'Robert', u'Ziegler')
        self.regular_user = self.create_user(u'K\xe4thi', u'B\xe4rfuss')

    @staticuid()
    def create_repository_tree(self):
        self.root = create(
            Builder('repository_root')
            .having(title_de=u'Ordnungssystem',
                    title_fr=u'Syst\xe8me de classement'))
        self.root.manage_setLocalRoles(self.org_unit.users_group_id,
                                       ('Reader', 'Contributor', 'Editor'))
        self.root.reindexObjectSecurity()

        self.repo0 = create(
            Builder('repository').within(self.root)
            .having(title_de=u'F\xfchrung',
                    title_fr=u'Direction'))

        self.repo00 = create(
            Builder('repository').within(self.repo0)
            .having(title_de=u'Vertr\xe4ge und Vereinbarungen',
                    title_fr=u'Contrats et accords'))

        self.repo1 = create(
            Builder('repository').within(self.root)
            .having(title_de=u'Bev\xf6lkerung und Sicherheit',
                    title_fr=u'Population et de la s\xe9curit\xe9'))

    @staticuid()
    def create_treaty_dossiers(self):
        dossier = create(
            Builder('dossier').within(self.repo00)
            .titled(u'Vertr\xe4ge mit der kantonalen Finanzverwaltung')
            .having(description=u'Alle aktuellen Vertr\xe4ge mit der'
                    u' kantonalen Finanzverwaltung sind hier abzulegen.'
                    u' Vertr\xe4ge vor 2016 geh\xf6ren ins Archiv.',
                    keywords=(u'Finanzverwaltung', u'Vertr\xe4ge'),
                    start=date(2016, 1, 1),
                    responsible='hugo.boss'))
        create(Builder('dossier').within(dossier).titled(u'2016'))

        create(
            Builder('dossier').within(self.repo00)
            .titled(u'Archiv Vertr\xe4ge')
            .having(description=u'Archiv der Vertr\xe4ge vor 2016.',
                    keywords=(u'Finanzverwaltung', u'Vertr\xe4ge'),
                    start=date(2000, 1, 1),
                    end=date(2015, 12, 31),
                    responsible='hugo.boss')
            .in_state('dossier-state-resolved')).absolute_url()

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

    def create_user(self, firstname, lastname, globalroles=()):
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

        return plone_user

    @contextmanager
    def login(self, user):
        old_manager = getSecurityManager()
        try:
            login(getSite(), user.getId())
            yield
        finally:
            setSecurityManager(old_manager)
