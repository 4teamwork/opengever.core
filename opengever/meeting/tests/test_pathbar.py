from datetime import date
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.base.model import create_session
from opengever.testing import IntegrationTestCase
from opengever.testing.pages import breadcrumbs


class TestPathBar(IntegrationTestCase):

    features = ('meeting',)

    @browsing
    def test_committee_pathbar_is_correct(self, browser):
        self.login(self.meeting_user, browser)

        browser.open(self.meeting.model.get_url())
        self.assertEqual(
            ['Hauptmandant',
             'Sitzungen',
             u'Rechnungspr\xfcfungskommission',
             u'9. Sitzung der Rechnungspr\xfcfungskommission'],
            breadcrumbs.text_items())

    @browsing
    def test_member_pathbar_is_correct(self, browser):
        with self.login(self.administrator):
            member = create(Builder('member'))
            create_session().flush()  # XXX maybe auto-flush here ...

        self.login(self.meeting_user, browser)
        browser.open(member.get_url(self.committee_container))
        self.assertEqual(
            [u'Hauptmandant', u'Sitzungen', u'M\xfcller Peter'],
            breadcrumbs.text_items())

    @browsing
    def test_membership_pathbar_is_correct(self, browser):
        with self.login(self.administrator):
            committee_model = self.committee.load_model()
            member = create(Builder('member'))
            membership = create(Builder('membership')
                                .having(member=member,
                                        committee=committee_model,
                                        date_from=date(2014, 1, 1),
                                        date_to=date(2015, 1, 1)))
            create_session().flush()  # XXX maybe auto-flush here ...

        self.login(self.committee_responsible, browser)
        browser.open(membership.get_edit_url())
        self.assertEqual(
            [u'Hauptmandant',
             u'Sitzungen',
             u'Rechnungspr\xfcfungskommission',
             u'M\xfcller Peter, Jan 01, 2014 - Jan 01, 2015'],
            breadcrumbs.text_items())
