from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.testing import FunctionalTestCase


class TestPathBar(FunctionalTestCase):

    def setUp(self):
        super(TestPathBar, self).setUp()
        self.admin_unit.public_url = 'http://nohost/plone'

        self.root = create(Builder('repository_root').titled(u'Repository'))
        self.repo = create(Builder('repository')
                           .within(self.root)
                           .titled(u'Testposition'))
        self.dossier = create(Builder('dossier')
                              .within(self.repo)
                              .titled(u'Dossier 1'))
        self.meeting_dossier = create(
            Builder('meeting_dossier').within(self.repo))

    @browsing
    def test_regression_committee_is_not_duplicated_in_pathbar(self, browser):
        container = create(Builder('committee_container'))
        committee = create(Builder('committee').within(container))
        meeting = create(Builder('meeting')
                         .having(committee=committee.load_model(),
                                 start=self.localized_datetime(2010, 1, 1))
                         .link_with(self.meeting_dossier))

        browser.login().open(meeting.get_url())
        self.assertEqual(
            ['Client1', 'opengever-meeting-committeecontainer',
             'My Committee', 'Jan 01, 2010'],
            browser.css('#portal-breadcrumbs a').text)
