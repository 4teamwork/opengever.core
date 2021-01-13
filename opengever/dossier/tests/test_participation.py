from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages.statusmessages import error_messages
from ftw.testbrowser.pages.statusmessages import info_messages
from opengever.dossier.behaviors.participation import IParticipationAware
from opengever.dossier.participations import DupplicateParticipation
from opengever.dossier.participations import InvalidParticipantId
from opengever.dossier.participations import InvalidRole
from opengever.dossier.participations import IParticipationData
from opengever.dossier.participations import MissingParticipation
from opengever.dossier.participations import PloneParticipationHandler
from opengever.dossier.participations import SQLParticipationHandler
from opengever.testing import IntegrationTestCase


class TestPloneParticipationHanlder(IntegrationTestCase):

    handler_class = PloneParticipationHandler
    valid_id = 'kathi.barfuss'

    def test_handler_delegates_to_correct_handler_class(self):
        self.login(self.regular_user)
        handler = IParticipationAware(self.empty_dossier)
        self.assertIsInstance(handler.handler, self.handler_class)

    def test_adding_participation(self):
        self.login(self.regular_user)
        handler = IParticipationAware(self.empty_dossier)
        self.assertItemsEqual(handler.get_participations(), [])

        kathi = handler.add_participation(
            participant_id=self.valid_id,
            roles=['participation', 'final-drawing'])

        self.assertItemsEqual(handler.get_participations(), [kathi])

    def test_updating_participaton(self):
        self.login(self.regular_user)
        handler = IParticipationAware(self.empty_dossier)
        handler.add_participation(
            participant_id=self.valid_id,
            roles=['participation', 'final-drawing'])
        participation = handler.get_participation(self.valid_id)
        self.assertItemsEqual(
            IParticipationData(participation).roles,
            ['participation', 'final-drawing'])

        handler.update_participation(self.valid_id, roles=['participation'])
        participation = handler.get_participation(self.valid_id)
        self.assertItemsEqual(
            IParticipationData(participation).roles, ['participation'])

    def test_deleting_participaton(self):
        self.login(self.regular_user)
        handler = IParticipationAware(self.empty_dossier)
        handler.add_participation(
            participant_id=self.valid_id,
            roles=['participation', 'final-drawing'])
        self.assertTrue(handler.has_participation(self.valid_id))

        handler.remove_participation(self.valid_id)
        self.assertFalse(handler.has_participation(self.valid_id))

    def test_only_one_participation_per_participant_is_allowed(self):
        self.login(self.regular_user)
        handler = IParticipationAware(self.empty_dossier)

        handler.add_participation(participant_id=self.valid_id,
                                  roles=['participation', 'final-drawing'])

        with self.assertRaises(DupplicateParticipation) as exc:
            handler.add_participation(participant_id=self.valid_id,
                                      roles=['participation', 'final-drawing'])
        self.assertEqual(
            'There is already a participation for {}'.format(self.valid_id),
            exc.exception.message)

    def test_cannot_add_participation_for_invalid_participant(self):
        self.login(self.regular_user)
        handler = IParticipationAware(self.empty_dossier)

        with self.assertRaises(InvalidParticipantId) as exc:
            handler.add_participation(participant_id='invalid-id',
                                      roles=['participation', 'final-drawing'])

        self.assertEqual(
            'invalid-id is not a valid id',
            exc.exception.message)
        self.assertFalse(handler.has_participation('invalid-id'))

    def test_cannot_delete_missing_participation(self):
        self.login(self.regular_user)
        handler = IParticipationAware(self.empty_dossier)
        self.assertFalse(handler.has_participation(self.valid_id))

        with self.assertRaises(MissingParticipation) as exc:
            handler.remove_participation(self.valid_id)

        self.assertEqual(
            '{} has no participations on this context'.format(self.valid_id),
            exc.exception.message)

    def test_cannot_update_missing_participation(self):
        self.login(self.regular_user)
        handler = IParticipationAware(self.empty_dossier)
        self.assertFalse(handler.has_participation(self.valid_id))
        with self.assertRaises(MissingParticipation) as exc:
            handler.update_participation(self.valid_id, roles=['participation'])

        self.assertEqual(
            '{} has no participations on this context'.format(self.valid_id),
            exc.exception.message)

    def test_cannot_add_participation_with_invalid_role(self):
        self.login(self.regular_user)
        handler = IParticipationAware(self.empty_dossier)

        with self.assertRaises(InvalidRole) as exc:
            handler.add_participation(participant_id=self.valid_id,
                                      roles=['invalid-role'])

        self.assertEqual(
            "Role 'invalid-role' does not exist",
            exc.exception.message)
        self.assertFalse(handler.has_participation(self.valid_id))

    def test_cannot_add_participation_without_role(self):
        self.login(self.regular_user)
        handler = IParticipationAware(self.empty_dossier)

        with self.assertRaises(InvalidRole) as exc:
            handler.add_participation(participant_id=self.valid_id,
                                      roles=[])

        self.assertEqual(
            "A list of roles is required",
            exc.exception.message)
        self.assertFalse(handler.has_participation(self.valid_id))

    def test_cannot_update_participaton_with_invalid_role(self):
        self.login(self.regular_user)
        handler = IParticipationAware(self.empty_dossier)
        handler.add_participation(
            participant_id=self.valid_id,
            roles=['participation', 'final-drawing'])

        with self.assertRaises(InvalidRole) as exc:
            handler.update_participation(self.valid_id, roles=['invalid-role'])
        self.assertEqual(
            "Role 'invalid-role' does not exist",
            exc.exception.message)

        participation = handler.get_participation(self.valid_id)
        self.assertItemsEqual(
            IParticipationData(participation).roles,
            ['participation', 'final-drawing'])

    def test_cannot_update_participaton_without_role(self):
        self.login(self.regular_user)
        handler = IParticipationAware(self.empty_dossier)
        handler.add_participation(
            participant_id=self.valid_id,
            roles=['participation', 'final-drawing'])

        with self.assertRaises(InvalidRole) as exc:
            handler.update_participation(self.valid_id, roles=[])
        self.assertEqual(
            "A list of roles is required",
            exc.exception.message)

        participation = handler.get_participation(self.valid_id)
        self.assertItemsEqual(
            IParticipationData(participation).roles,
            ['participation', 'final-drawing'])


class TestSQLParticipationHanlder(TestPloneParticipationHanlder):

    features = ('contact', )

    handler_class = SQLParticipationHandler
    valid_id = 'ogds_user:kathi.barfuss'


class TestParticipationAddForm(IntegrationTestCase):

    def add_participation_to_dossier(self, contact_id, roles, browser):
        browser.visit(self.dossier)
        factoriesmenu.add('Participant')
        browser.fill({'Roles': roles})
        form = browser.find_form_by_field('Person')
        form.find_widget('Person').fill(contact_id)
        browser.find('Add').click()

    @browsing
    def test_participant_can_only_have_one_participation_per_context(self, browser):
        self.login(self.regular_user, browser)

        self.add_participation_to_dossier(self.regular_user.getId(), ['Regard'], browser)
        self.assertEqual(['Participation created.'], info_messages())
        self.assertEqual([], error_messages())

        self.add_participation_to_dossier(self.regular_user.getId(), ['Participation'], browser)
        self.assertEqual(['A participation already exists for this contact.'], error_messages())
        self.assertEqual('http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/'
                         'dossier-1/add-plone-participation', browser.url)
