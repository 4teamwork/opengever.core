from DateTime import DateTime
from ftw.builder import Builder
from ftw.builder import create
from opengever.testing import FunctionalTestCase


class TestOverview(FunctionalTestCase):

    use_browser = True

    def setUp(self):
        super(TestOverview, self).setUp()
        self.dossier = create(Builder('dossier').titled(u'Testdossier'))

    def assert_subdossier_box(self, expected):
        subdossiers = self.browser.css(
            '#subdossiersBox a.contenttype-opengever-dossier-businesscasedossier')

        self.assertEquals(
            expected, [aa.plain_text() for aa in subdossiers],
            'the subdossierbox does not contain the expected subdossiers')

    def test_subdossier_box_items_are_limited_to_five_sort_by_modified(self):
        for i in range(6):
            create(Builder('dossier')
                   .within(self.dossier)
                   .with_modification_date(DateTime()+i)
                   .titled(u'Dossier %s' % i))

        self.browser.open(
            '%s/tabbedview_view-overview' % self.dossier.absolute_url())

        self.assert_subdossier_box(
            ['Dossier 5', 'Dossier 4', 'Dossier 3', 'Dossier 2', 'Dossier 1'])

    def test_subdossier_box_only_list_open_dossiers(self):
        create(Builder('dossier').within(self.dossier)
               .titled(u'Dossier Open')
               .in_state('dossier-state-active'))

        create(Builder('dossier').within(self.dossier)
               .titled(u'Dossier Inactive')
               .in_state('dossier-state-inactive'))

        create(Builder('dossier').within(self.dossier)
               .titled(u'Dossier Resolved')
               .in_state('dossier-state-resolved'))

        self.browser.open(
            '%s/tabbedview_view-overview' % self.dossier.absolute_url())

        self.assert_subdossier_box(['Dossier Open'])
