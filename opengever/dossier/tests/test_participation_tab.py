from opengever.dossier.behaviors.dossier import IDossier
from opengever.dossier.behaviors.participation import IParticipationAware
from opengever.testing import SolrIntegrationTestCase


class TestParticipationTabbedview(SolrIntegrationTestCase):

    def get_tabbed_view(self, name):
        view = self.dossier.restrictedTraverse(name)
        view.update()
        return view

    def test_participants_includes_responsible(self):
        self.login(self.regular_user)

        handler = IParticipationAware(self.dossier)
        self.assertEqual(0, len(handler.get_participations()))

        view = self.get_tabbed_view('tabbedview_view-participants')
        self.assertEqual(1, len(view.contents))
        responsible = view.contents[0]
        self.assertEqual(IDossier(self.dossier).responsible, responsible.contact)

    def test_participants_text_filter(self):
        self.login(self.regular_user)
        handler = IParticipationAware(self.dossier)
        handler.add_participation(
            participant_id=self.regular_user.id,
            roles=['participation', 'final-drawing'])
        handler.add_participation(
            participant_id=self.secretariat_user.id,
            roles=['participation', 'final-drawing'])

        view = self.get_tabbed_view('tabbedview_view-participants')
        self.assertEqual(3, len(view.contents))
        self.assertItemsEqual(
            [self.regular_user.id, self.secretariat_user.id, self.dossier_responsible.id],
            [participant.contact for participant in view.contents])

        self.portal.REQUEST['searchable_text'] = 'kathi'
        view = self.get_tabbed_view('tabbedview_view-participants')
        self.assertEqual(1, len(view.contents))
        self.assertItemsEqual(
            [self.regular_user.id],
            [participant.contact for participant in view.contents])
