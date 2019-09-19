from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from opengever.activity.model import Activity
from opengever.activity.model import Notification
from opengever.activity.model.subscription import Subscription
from opengever.meeting.activity.helpers import actor_link
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

        submitted_proposal = self.submit_proposal(proposal, browser)
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

        submitted_proposal = self.submit_proposal(proposal, browser)
        committee_group_id = self.committee.load_model().group_id

        self.assertSubscribersLength(1 + self.count_group_members(committee_group_id))

        self.reject_proposal(submitted_proposal, browser)

        self.assertSubscribersForResource([self.dossier_responsible], proposal)
        self.assertSubscribersLength(1)

    @browsing
    def test_record_activity_on_comment_for_proposal_and_submitted_proposal(self, browser):
        self.login(self.manager, browser)
        committee_group_id = self.committee.load_model().group_id
        commented_activities = self.query_activities('proposal-commented')

        self.assertEqual(0, commented_activities.count())

        proposal = self.create_proposal_with_issuer(
            self.dossier_responsible, self.committee, browser)
        self.submit_proposal(proposal, browser)

        proposal.comment(u'james b\xc3\xb6nd')

        self.assertEqual(2, commented_activities.count())
        for activity in commented_activities.all():
            self.assertEquals('proposal-commented', activity.kind)
            self.assertEquals(proposal.title, activity.title)
            self.assertEquals(
                u'Proposal commented by {}'.format(actor_link()),
                activity.summary)

        self.assertEqual(
            [u'Proposal commented', u'Submitted proposal commented'],
            [activity.label for activity in commented_activities.all()]
        )

        users = self.get_group_members(committee_group_id) + [self.dossier_responsible]
        self.assertBadgeNotificationsForUsers(
            users, u'proposal-commented')

    @browsing
    def test_record_activity_on_submtitting_a_proposal_for_proposal_and_submitted_proposal(self, browser):
        self.login(self.manager, browser)
        committee_group_id = self.committee.load_model().group_id
        submitted_activities = self.query_activities('proposal-transition-submit')

        proposal = self.create_proposal_with_issuer(
            self.dossier_responsible, self.committee, browser)

        self.assertEqual(0, submitted_activities.count())

        self.submit_proposal(proposal, browser)

        self.assertEqual(2, submitted_activities.count())
        for activity in submitted_activities.all():
            self.assertEquals('proposal-transition-submit', activity.kind)
            self.assertEquals('Proposal submitted', activity.label)
            self.assertEquals(proposal.title, activity.title)
            self.assertEquals(
                u'Submitted by {}'.format(actor_link()),
                activity.summary)

        users = self.get_group_members(committee_group_id)
        self.assertBadgeNotificationsForUsers(
            users, u'proposal-transition-submit')

    @browsing
    def test_record_activity_on_rejecting_a_proposal_for_proposal_and_submitted_proposal(self, browser):
        self.login(self.manager, browser)
        rejected_activities = self.query_activities('proposal-transition-reject')

        proposal = self.create_proposal_with_issuer(
            self.dossier_responsible, self.committee, browser)
        submitted_proposal = self.submit_proposal(proposal, browser)

        self.assertEqual(0, rejected_activities.count())

        self.reject_proposal(submitted_proposal, browser)

        self.assertEqual(2, rejected_activities.count())
        for activity in rejected_activities.all():
            self.assertEquals('proposal-transition-reject', activity.kind)
            self.assertEquals('Proposal rejected', activity.label)
            self.assertEquals(proposal.title, activity.title)
            self.assertEquals(
                u'Rejected by {}'.format(actor_link()),
                activity.summary)

        users = [self.dossier_responsible]
        self.assertBadgeNotificationsForUsers(
            users, u'proposal-transition-reject')

    @browsing
    def test_record_activity_on_schedule_a_proposal_for_proposal_and_submitted_proposal(self, browser):
        self.login(self.manager, browser)
        scheduled_activities = self.query_activities('proposal-transition-schedule')
        meeting = self.meeting.model

        proposal = self.create_proposal_with_issuer(
            self.dossier_responsible, self.committee, browser)
        submitted_proposal = self.submit_proposal(proposal, browser)

        self.assertEqual(0, scheduled_activities.count())

        submitted_proposal.load_model().schedule(meeting)

        self.assertEqual(2, scheduled_activities.count())
        for activity in scheduled_activities.all():
            self.assertEquals('proposal-transition-schedule', activity.kind)
            self.assertEquals('Proposal scheduled', activity.label)
            self.assertEquals(proposal.title, activity.title)
            self.assertEquals(
                u'Scheduled for meeting {} by {}'.format(meeting.get_title(), actor_link()),
                activity.summary)

        users = [self.dossier_responsible]
        self.assertBadgeNotificationsForUsers(
            users, u'proposal-transition-schedule')

    @browsing
    def test_record_activity_on_decide_a_proposal_for_proposal_and_submitted_proposal(self, browser):
        self.login(self.committee_responsible, browser)
        decided_activities = self.query_activities('proposal-transition-decide')

        proposal = self.create_proposal_with_issuer(
            self.dossier_responsible, self.committee, browser)
        submitted_proposal = self.submit_proposal(proposal, browser)

        agenda_item = self.schedule_proposal(self.meeting,
                                             submitted_proposal)
        agenda_item.decide()
        excerpt = agenda_item.generate_excerpt('Foo')

        self.assertEqual(0, decided_activities.count())

        submitted_proposal.load_model().decide(agenda_item, excerpt)

        self.assertEqual(2, decided_activities.count())

        for activity in decided_activities.all():
            self.assertEquals('proposal-transition-decide', activity.kind)
            self.assertEquals('Proposal decided', activity.label)
            self.assertEquals(proposal.title, activity.title)
            self.assertEquals(
                u'Proposal decided by {}'.format(actor_link()),
                activity.summary)

        users = [self.dossier_responsible]
        self.assertBadgeNotificationsForUsers(
            users, u'proposal-transition-decide')

    @browsing
    def test_record_activity_on_update_attachment_for_proposal_and_submitted_proposal(self, browser):
        self.login(self.manager, browser)
        attachment_updated_activities = self.query_activities('proposal-attachment-updated')
        committee_group_id = self.committee.load_model().group_id
        rtool = api.portal.get_tool('portal_repository')

        document = self.subdocument

        proposal = self.create_proposal_with_issuer(
            self.dossier_responsible, self.committee, browser)
        self.submit_proposal(proposal, browser)

        # create init version
        rtool.save(document)
        proposal.submit_additional_document(document)

        self.assertEqual(0, attachment_updated_activities.count())

        # create version 1
        rtool.save(document)
        proposal.submit_additional_document(document)

        self.assertEqual(2, attachment_updated_activities.count())

        for activity in attachment_updated_activities.all()[-2:]:
            self.assertEquals('proposal-attachment-updated', activity.kind)
            self.assertEquals('Attachment updated', activity.label)
            self.assertEquals(proposal.title, activity.title)
            self.assertEquals(
                u'Submitted document {} updated to version 1'.format(document.title),
                activity.summary)

        users = self.get_group_members(committee_group_id)
        self.assertBadgeNotificationsForUsers(
            users, u'proposal-attachment-updated')

    @browsing
    def test_record_activity_on_submit_attachment_for_proposal_and_submitted_proposal(self, browser):
        self.login(self.manager, browser)
        attachment_submitted_activities = self.query_activities(
            'proposal-additional-documents-submitted')
        committee_group_id = self.committee.load_model().group_id
        document = self.subdocument

        proposal = self.create_proposal_with_issuer(
            self.dossier_responsible, self.committee, browser)
        self.submit_proposal(proposal, browser)

        self.assertEqual(0, attachment_submitted_activities.count())

        proposal.submit_additional_document(document)

        self.assertEqual(2, attachment_submitted_activities.count())

        for activity in attachment_submitted_activities.all():
            self.assertEquals('proposal-additional-documents-submitted', activity.kind)
            self.assertEquals('Additional documents submitted', activity.label)
            self.assertEquals(proposal.title, activity.title)
            self.assertEquals(
                u'Document {} submitted'.format(document.title),
                activity.summary)

        users = self.get_group_members(committee_group_id)
        self.assertBadgeNotificationsForUsers(
            users, u'proposal-additional-documents-submitted')

    @browsing
    def test_do_not_record_activity_for_submitted_documents_on_submtitting_a_proposal_with_documents(self, browser):
        self.login(self.manager, browser)
        attachment_submitted_activities = self.query_activities(
            'proposal-additional-documents-submitted')

        proposal = self.create_proposal_with_issuer(
            self.dossier_responsible, self.committee, browser,
            Attachments=[self.document])

        self.assertEqual(0, attachment_submitted_activities.count())

        self.submit_proposal(proposal, browser)

        self.assertEqual(0, attachment_submitted_activities.count())

    def assertBadgeNotificationsForUsers(self, users, activity_kind=None):
        notifications = self.query_notifications(activity_kind).filter(
            Notification.is_badge.is_(True))

        self.assertItemsEqual(
            [user.id for user in users],
            [notification.userid for notification in notifications.all()])

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

    def lookup_submitted_proposal(self, proposal):
        return self.portal.restrictedTraverse(
            proposal.load_model().submitted_physical_path.encode('utf-8'))

    def count_group_members(self, group_id):
        return len(self.get_group_members(group_id))

    def get_group_members(self, group_id):
        return api.user.get_users(groupname=group_id)

    def execute_transition(self, obj, transition, browser, comment=''):
        browser.visit(
            obj, view="addtransitioncomment_sql?form.widgets.transition={}".format(
                transition))
        if comment:
            browser.fill({'Comment': comment})
        browser.find('Confirm').click()

    def submit_proposal(self, proposal, browser, comment=''):
        browser.open(proposal)
        browser.click_on('proposal-transition-submit ')
        if comment:
            browser.fill({'Comment': comment})
        browser.click_on('Confirm')
        return self.lookup_submitted_proposal(proposal)

    def reject_proposal(self, proposal, browser, comment=''):
        self.execute_transition(proposal, 'submitted-pending', browser, comment)

    def query_notifications(self, activity_kind=None):
        notifications_query = Notification.query
        if activity_kind:
            notifications_query = notifications_query.filter(
                Notification.activity.has(kind=activity_kind))

        return notifications_query

    def query_activities(self, kind=None):
        activities_query = Activity.query
        if kind:
            activities_query = activities_query.filter(Activity.kind == kind)

        return activities_query

    def create_proposal_with_issuer(
            self, issuer, committee, browser, **kwargs):
        browser.open(self.dossier)
        factoriesmenu.add('Proposal')

        values = {
            'Committee': committee.title,
            'Proposal template': u'Geb\xfchren',
            'Edit after creation': False}
        values.update(kwargs)

        browser.fill(values)

        form = browser.find_form_by_field('Issuer')
        form.find_widget('Issuer').fill(issuer.id)
        form.save()

        return browser.context
