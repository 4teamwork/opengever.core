from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from opengever.activity.model import Activity
from opengever.activity.model.subscription import Subscription
from opengever.meeting.activity.activities import actor_link
from opengever.testing import IntegrationTestCase
from plone import api
from zope.app.intid.interfaces import IIntIds
from zope.component import getUtility


class TestMeetingActivities(IntegrationTestCase):

    features = ('meeting', 'activity')

    @browsing
    def test_adding_proposal_adds_issuer_to_watchers(self, browser):
        self.login(self.committee_responsible, browser)

        self.assertSubscribersLength(0)

        proposal = self.create_proposal_with_issuer(
            self.dossier_responsible, self.committee, browser)

        self.assertSubscribersLength(1)
        self.assertSubscribersForResource([self.dossier_responsible], proposal)

    @browsing
    def test_change_proposals_issuer_updates_watchers(self, browser):
        self.login(self.committee_responsible, browser)

        self.assertSubscribersLength(0)

        proposal = self.create_proposal_with_issuer(
            self.dossier_responsible, self.committee, browser)

        browser.open(proposal, view="edit")
        form = browser.find_form_by_field('Issuer')
        form.find_widget('Issuer').fill(self.regular_user.id)
        form.save()

        self.assertSubscribersForResource([self.regular_user], proposal)
        self.assertSubscribersLength(1)

    @browsing
    def test_submit_proposal_adds_committee_users_to_watchers(self, browser):
        self.login(self.committee_responsible, browser)

        self.assertSubscribersLength(0)

        proposal = self.create_proposal_with_issuer(
            self.dossier_responsible, self.committee, browser)

        self.assertSubscribersLength(1)

        self.submit_proposal(proposal, browser)

        submitted_proposal = self.lookup_submitted_proposel(proposal)
        committee_group_id = self.committee.load_model().group_id

        self.assertSubscribersLength(1 + self.count_group_members(committee_group_id))
        self.assertSubscribersForResource([self.dossier_responsible], proposal)
        self.assertSubscribersForResource(
            self.get_group_members(committee_group_id),
            submitted_proposal)

    @browsing
    def test_reject_submitted_proposal_removes_committee_users_as_watchers(self, browser):
        self.login(self.committee_responsible, browser)

        self.assertSubscribersLength(0)

        proposal = self.create_proposal_with_issuer(
            self.dossier_responsible, self.committee, browser)

        self.assertSubscribersLength(1)

        self.submit_proposal(proposal, browser)

        submitted_proposal = self.lookup_submitted_proposel(proposal)
        committee_group_id = self.committee.load_model().group_id

        self.assertSubscribersLength(1 + self.count_group_members(committee_group_id))

        self.reject_proposal(submitted_proposal, browser)

        self.assertSubscribersForResource([self.dossier_responsible], proposal)
        self.assertSubscribersLength(1)

    @browsing
    def test_record_activity_on_comment_for_proposal_and_submitted_proposal(self, browser):
        self.login(self.committee_responsible)

        self.assertEqual(0, Activity.query.count())

        self.proposal.comment(u'james b\xc3\xb6nd')

        self.assertEqual(2, Activity.query.count())
        for activity in Activity.query.all():
            self.assertEquals('proposal-commented', activity.kind)
            self.assertEquals(self.proposal.title, activity.title)
            self.assertEquals(
                u'Proposal commented by {}'.format(actor_link()),
                activity.summary)

    @browsing
    def test_record_activity_on_submtitting_a_proposal_for_proposal_and_submitted_proposal(self, browser):
        self.login(self.committee_responsible, browser)

        self.assertEqual(0, Activity.query.count())

        self.submit_proposal(self.draft_proposal, browser, comment=u'james b\xc3\xb6nd')

        self.assertEqual(2, Activity.query.count())
        for activity in Activity.query.all():
            self.assertEquals('proposal-transition-submit', activity.kind)
            self.assertEquals('Proposal submitted', activity.label)
            self.assertEquals(self.draft_proposal.title, activity.title)
            self.assertEquals(
                u'Submitted by {}'.format(actor_link()),
                activity.summary)

    @browsing
    def test_record_activity_on_rejecting_a_proposal_for_proposal_and_submitted_proposal(self, browser):
        self.login(self.committee_responsible, browser)

        self.assertEqual(0, Activity.query.count())

        self.reject_proposal(self.submitted_proposal, browser, comment=u'james b\xc3\xb6nd')

        self.assertEqual(2, Activity.query.count())
        for activity in Activity.query.all():
            self.assertEquals('proposal-transition-reject', activity.kind)
            self.assertEquals('Proposal rejected', activity.label)
            self.assertEquals(self.proposal.title, activity.title)
            self.assertEquals(
                u'Rejected by {}'.format(actor_link()),
                activity.summary)

    @browsing
    def test_record_activity_on_schedule_a_proposal_for_proposal_and_submitted_proposal(self, browser):
        self.login(self.committee_responsible, browser)
        meeting = self.meeting.model

        self.assertEqual(0, Activity.query.count())

        self.submitted_proposal.load_model().schedule(meeting)

        self.assertEqual(2, Activity.query.count())
        for activity in Activity.query.all():
            self.assertEquals('proposal-transition-schedule', activity.kind)
            self.assertEquals('Proposal scheduled', activity.label)
            self.assertEquals(self.proposal.title, activity.title)
            self.assertEquals(
                u'Scheduled for meeting {} by {}'.format(meeting.get_title(), actor_link()),
                activity.summary)

    def assertSubscribersForResource(self, subscribers, resource):
        self.assertItemsEqual(
            [subscriber.id for subscriber in subscribers],
            self.subscribers(resource))

    def assertSubscribersLength(self, length):
        self.assertEqual(length, len(self.subscribers()))

    def clear_subscribers(self):
        Subscription.query.delete()

    def subscribers(self, resource=None):
        query = Subscription.query
        if resource:
            intid = getUtility(IIntIds).getId(resource)
            query = query.filter(Subscription.resource.has(int_id=intid))

        return [subscription.watcher.actorid for subscription in query.all()]

    def lookup_submitted_proposel(self, proposal):
        return self.portal.restrictedTraverse(
            proposal.load_model().submitted_physical_path.encode('utf-8'))

    def count_group_members(self, group_id):
        return len(self.get_group_members(group_id))

    def get_group_members(self, group_id):
        return api.user.get_users(groupname=group_id)

    def execute_transition(self, obj, transition, browser, comment=''):
        browser.visit(
            obj, view="addtransitioncomment?form.widgets.transition={}".format(
                transition))
        if comment:
            browser.fill({'Comment': comment})
        browser.find('Confirm').click()

    def submit_proposal(self, proposal, browser, comment=''):
        self.execute_transition(proposal, 'pending-submitted', browser, comment)

    def reject_proposal(self, proposal, browser, comment=''):
        self.execute_transition(proposal, 'submitted-pending', browser, comment)

    def create_proposal_with_issuer(self, issuer, committee, browser):
        browser.open(self.dossier)
        factoriesmenu.add('Proposal')

        browser.fill(
            {'Committee': committee.title,
             'Proposal template': u'Geb\xfchren',
             'Edit after creation': False})

        form = browser.find_form_by_field('Issuer')
        form.find_widget('Issuer').fill(issuer.id)
        form.save()

        return browser.context
