from ftw.builder import Builder
from ftw.builder import create
from opengever.dossier.behaviors.dossier import IDossier
from opengever.dossier.behaviors.participation import IParticipationAware
from opengever.testing import FunctionalTestCase
from opengever.testing.helpers import obj2brain
from opengever.usermigration.dossier import DossierMigrator
from opengever.usermigration.exceptions import UserMigrationException
from plone import api


class TestDossierMigratorForResponsible(FunctionalTestCase):

    def setUp(self):
        super(TestDossierMigratorForResponsible, self).setUp()
        self.portal = self.layer['portal']
        self.catalog = api.portal.get_tool('portal_catalog')

        self.old_user = create(Builder('ogds_user').id('old.user'))
        self.new_user = create(Builder('ogds_user').id('new.user'))

        self.dossier = create(Builder('dossier')
                              .titled(u'Testdossier')
                              .having(responsible='old.user'))

    def test_dossier_responsible_gets_migrated(self):
        migrator = DossierMigrator(
            self.portal, {'old.user': 'new.user'}, 'move')
        migrator.migrate()
        self.assertEquals('new.user', IDossier(self.dossier).responsible)

    def test_dossier_responsible_index_gets_updated(self):
        migrator = DossierMigrator(
            self.portal, {'old.user': 'new.user'}, 'move')
        migrator.migrate()

        # Index should be up to date
        brains = self.catalog(responsible='new.user')
        self.assertEquals(1, len(brains))

        # Metadata should be up to date
        self.assertEquals('new.user', obj2brain(self.dossier).responsible)

    def test_raises_if_strict_and_user_doesnt_exist(self):
        migrator = DossierMigrator(
            self.portal, {'old.user': 'doesnt.exist'}, 'move')

        with self.assertRaises(UserMigrationException):
            migrator.migrate()

    def test_doesnt_raise_if_not_strict_and_user_doesnt_exist(self):
        migrator = DossierMigrator(
            self.portal, {'old.user': 'doesnt.exist'}, 'move', strict=False)

        migrator.migrate()
        self.assertEquals('doesnt.exist', IDossier(self.dossier).responsible)

    def test_returns_proper_results_for_moving_responsibles(self):
        migrator = DossierMigrator(
            self.portal, {'old.user': 'new.user'}, 'move')
        results = migrator.migrate()

        self.assertEquals(
            [('/plone/dossier-1', 'old.user', 'new.user')],
            results['responsibles']['moved']
        )


class TestDossierMigratorForParticipants(FunctionalTestCase):

    def setUp(self):
        super(TestDossierMigratorForParticipants, self).setUp()
        self.portal = self.layer['portal']

        create(Builder('ogds_user').id('old.participant'))
        create(Builder('ogds_user').id('new.participant'))

        self.dossier = create(Builder('dossier')
                              .titled(u'Testdossier'))

        self.phandler = IParticipationAware(self.dossier)
        p = self.phandler.create_participation('old.participant', ['regard'])
        self.phandler.append_participiation(p)

    def test_dossier_participation_gets_migrated(self):

        migrator = DossierMigrator(
            self.portal, {'old.participant': 'new.participant'}, 'move')
        migrator.migrate()

        self.assertEquals('new.participant',
                          self.phandler.get_participations()[0].contact)

    def test_contacts_dont_match_principal_mapping(self):
        # Create a contact with the same name as a mapped user in order to
        # verify the mapping doesn't match the contact.id
        contact = create(Builder('contact')
                         .having(firstname='contact',
                                 lastname='old'))

        # Create a participation using that contact
        p = self.phandler.create_participation(contact.contactid(), ['regard'])
        self.phandler.append_participiation(p)

        migrator = DossierMigrator(self.portal, {contact.id: 'new'}, 'move')
        migrator.migrate()

        # Should not have been migrated, participation should still refer
        # to contact:old-contact
        self.assertEquals('contact:old-contact',
                          self.phandler.get_participations()[-1].contact)

    def test_raises_if_strict_and_user_doesnt_exist(self):
        migrator = DossierMigrator(
            self.portal, {'old.participant': 'doesnt.exist'}, 'move')

        with self.assertRaises(UserMigrationException):
            migrator.migrate()

    def test_doesnt_raise_if_not_strict_and_user_doesnt_exist(self):
        migrator = DossierMigrator(
            self.portal, {'old.participant': 'doesnt.exist'},
            'move', strict=False)

        migrator.migrate()

        self.assertEquals('doesnt.exist',
                          self.phandler.get_participations()[0].contact)

    def test_returns_proper_results_for_moving_participants(self):
        migrator = DossierMigrator(
            self.portal, {'old.participant': 'new.participant'}, 'move')
        results = migrator.migrate()

        self.assertEquals(
            [('/plone/dossier-1', 'old.participant', 'new.participant')],
            results['participations']['moved']
        )
