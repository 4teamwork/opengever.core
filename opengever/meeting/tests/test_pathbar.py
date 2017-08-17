from datetime import date
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.base.model import create_session
from opengever.meeting.wrapper import MemberWrapper
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

        # XXX the permissions currently don't work well. this checks
        # modify poral content on committee-container, so we need to be
        # an admin for now. see #2829.
        self.login(self.administrator, browser)
        wrapped_member = MemberWrapper.wrap(self.committee_container, member)
        # NOTE: this opens the edit view! there is no separate view for
        # a single membership, they are all listed on the member view.
        browser.open(membership.get_url(wrapped_member))
        self.assertEqual(
            [u'Hauptmandant',
             u'Sitzungen',
             u'M\xfcller Peter',
             u'M\xfcller Peter, Jan 01, 2014 - Jan 01, 2015'],
            breadcrumbs.text_items())
