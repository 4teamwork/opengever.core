from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.testing import FunctionalTestCase


class TestCommitteeTabs(FunctionalTestCase):

    def setUp(self):
        super(TestCommitteeTabs, self).setUp()

        self.maxDiff = None
        self.container = create(Builder('committee_container'))
        self.committee = create(Builder('committee')
                                .within(self.container)
                                .with_default_period()
                                .titled(u'Kleiner Burgerrat'))
        self.committee_model = self.committee.load_model()

        self.repository_root, self.repository_folder = create(
            Builder('repository_tree'))
        self.meeting_dossier = create(Builder('meeting_dossier')
                                      .titled(u'D\xf6ssier')
                                      .within(self.repository_folder))

        create(Builder('meeting')
               .having(committee=self.committee_model)
               .link_with(self.meeting_dossier))

        create(Builder('meeting')
               .having(committee=self.committee_model, end=None)
               .link_with(self.meeting_dossier))

    @browsing
    def test_meeting_listing(self, browser):
        browser.login().open(self.committee, view='tabbedview_view-meetings')

        table = browser.css('.listing').first

        self.assertEquals([
            {'Title': u'C\xf6mmunity meeting',
             'State': u'Pending',
             'Date': 'Dec 13, 2011',
             'Location': u'B\xe4rn',
             'From': '09:30 AM',
             'To': '11:45 AM',
             'Dossier': u'D\xf6ssier'},
            {'Title': u'C\xf6mmunity meeting',
             'State': u'Pending',
             'Date': 'Dec 13, 2011',
             'Location': u'B\xe4rn',
             'From': '09:30 AM',
             'To': '',
             'Dossier': u'D\xf6ssier'}
        ], table.dicts())
