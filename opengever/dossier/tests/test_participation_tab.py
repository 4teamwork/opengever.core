from ftw.builder import Builder
from ftw.builder import create
from opengever.testing import FunctionalTestCase
from plone.app.testing import TEST_USER_ID
from opengever.dossier.behaviors.participation import ParticipationHandler


class TestParticipationTabbedview(FunctionalTestCase):

    def setUp(self):
        super(TestParticipationTabbedview, self).setUp()

        self.dossier = create(Builder('dossier')
                              .having(responsible=TEST_USER_ID))

    def get_tabbed_view(self, name):
        view = self.dossier.restrictedTraverse(name)
        view.update()
        return view

    def test_participants_includes_responsible(self):
        view = self.get_tabbed_view('tabbedview_view-participants')
        self.assertEqual(1, len(view.contents))
        responsible = view.contents[0]
        self.assertEqual(TEST_USER_ID, responsible.contact)

    def test_participants_text_filter(self):
        self.portal.REQUEST['searchable_text'] = 'sepp'

        handler = ParticipationHandler(self.dossier)
        sepp = handler.create_participation(
            contact='sepp', roles=['Reader', 'Editor'])
        handler.append_participiation(sepp)

        view = self.get_tabbed_view('tabbedview_view-participants')
        self.assertEqual(1, len(view.contents))
