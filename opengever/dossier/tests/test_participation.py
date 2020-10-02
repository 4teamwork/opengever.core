from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages.statusmessages import error_messages
from ftw.testbrowser.pages.statusmessages import info_messages
from ftw.testing import MockTestCase
from mocker import ANY
from opengever.core.testing import COMPONENT_UNIT_TESTING
from opengever.dossier.behaviors.participation import PloneParticipationHandler
from opengever.dossier.interfaces import IParticipationCreated
from opengever.dossier.interfaces import IParticipationRemoved
from opengever.testing import IntegrationTestCase
from zope.annotation.interfaces import IAnnotations
from zope.interface import Interface


class TestPloneParticipationHanlder(MockTestCase):
    layer = COMPONENT_UNIT_TESTING

    def setUp(self):
        super(TestPloneParticipationHanlder, self).setUp()
        self.context = self.mocker.mock()

        annonation_storage = {}

        def annotation_adapter(obj):
            return annonation_storage

        self.mock_adapter(annotation_adapter, IAnnotations, [Interface, ])

        created_handler = self.mocker.mock()
        self.expect(
            created_handler(ANY)).result('created event fired').count(0, 3)
        self.mock_handler(created_handler, [IParticipationCreated, ])

        removed_handler = self.mocker.mock()
        self.expect(
            removed_handler(ANY)).result('removed event fired').count(0, 1)
        self.mock_handler(removed_handler, [IParticipationRemoved, ])

    def test_participation_with_handler(self):
        self.replay()
        handler = PloneParticipationHandler(self.context)

        # creation
        peter = handler.create_participation(
            {'contact': 'peter', 'roles': ['Reader', ], })
        sepp = handler.create_participation(
            {'contact': 'sepp', 'roles': ['Reader', 'Editor'], })
        hugo = handler.create_participation(
            {'contact': 'hugo'})

        # test appending
        handler.append_participation(peter)
        self.assertEquals(handler.get_participations(), [peter, ])

        handler.append_participation(sepp)
        self.assertEquals(handler.get_participations(), [peter, sepp])

        # an existing participation should not be addable multiple time
        self.assertEquals(handler.append_participation(peter), None)

        # test has participation
        self.assertEquals(handler.has_participation(peter), True)
        self.assertEquals(handler.has_participation(hugo), False)

        # test removing
        handler.remove_participation(peter)
        self.assertEquals(handler.get_participations(), [sepp, ])


class TestParticipationAddForm(IntegrationTestCase):

    def add_participation_to_dossier(self, contact_id, roles, browser):
        browser.visit(self.dossier)
        factoriesmenu.add('Participant')
        browser.fill({'Roles': roles})
        form = browser.find_form_by_field('Contact')
        form.find_widget('Contact').fill(contact_id)
        browser.find('Add').click()

    @browsing
    def test_participant_can_only_have_one_participation_per_context(self, browser):
        self.login(self.regular_user, browser)

        self.add_participation_to_dossier(self.regular_user.getId(), ['Regard'], browser)
        self.assertEqual(['Participation created.'], info_messages())
        self.assertEqual([], error_messages())

        self.add_participation_to_dossier(self.regular_user.getId(), ['Participation'], browser)
        self.assertEqual(['There is already a participation for this contact.'], error_messages())
        self.assertEqual('http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/'
                         'dossier-1/add-plone-participation', browser.url)
